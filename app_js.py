from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import datetime
app = Flask(__name__)

# 경로 설정
file_path = 'C:\\Users\\wai\\Desktop\\프로젝트\\암호화폐\\'
# file_path = 'D:\\암호화폐\\'

# 시간 설정
dt = datetime.datetime.today().strftime('%Y%m%d')
# 워드클라우드 버튼 기간 설정(일주일전 ~ 현재)
bf_dt = (datetime.datetime.today() - datetime.timedelta(days=7)).strftime('%Y%m%d')
btn_dt_index = pd.date_range(start=bf_dt,end=dt).map(lambda x : str(x).replace(' 00:00:00', ''))
# dt = '20210630'

@app.route('/')
def haram():
   return render_template('candle.html')

@app.route('/result')
def result():
   f_nm = file_path+'score_af_'+dt+'.csv'
   df = pd.read_csv(f_nm, encoding='cp949')
   result_list = list(df.values)
   df_h = df.to_html(table_id='table', header=True)
   return render_template('result.html', result_list = result_list, df_html = df_h, ssibal = 'ssibalnum', df = df)

@app.route('/chart')
def chart():
    # 데이터 임포트
    f_nm = file_path + 'score_' + dt + '.csv'
    df = pd.read_csv(f_nm, encoding='cp949', dtype='str')

    ### 1. 일자별 정보
    bit_df = df[df['코인명'] == '비트코인']  # 일자별 '비트코인' 추출
    bit_df = bit_df.astype({'스코어_합계' : 'int'})
    # 그래프 도식화를 위한 MIN_MAX_SCAILING
    max_sr = int(bit_df['스코어_합계'].max())
    min_sr = int(bit_df['스코어_합계'].min())

    if abs(max_sr) >= abs(min_sr):
       max_scale_value = abs(max_sr)
    else:
       max_scale_value = abs(min_sr)
    print('절대값 최고치 :', max_scale_value)

    # 스코어 합계 => SCALING
    if max_scale_value != 0:
        bit_df['스코어_SCALING'] = bit_df['스코어_합계']/max_scale_value
    else: # 양수, 음수 절대값 => 0 일때
        pass
        bit_df['스코어_SCALING'] = 0

    bit_dict = dict({
        '등록시간': list(bit_df['등록시간']),
        '스코어_SCALING': list(bit_df['스코어_SCALING']),
        '스코어_합계': list(bit_df['스코어_합계']),
        '전체건수': len(bit_df)
    })  # 일자별 비트코인에 대한 긍부정 합계 스코어
    print(bit_dict)

    ### 2. 오늘 날짜 정보
    to_df = df[df['등록시간'] == dt] # 오늘 날짜 데이터 프레임 추출
    print(len(to_df))
    to_dict = dict({'코인명' : list(to_df['코인명']),
         '스코어_긍정' : list(to_df['스코어_긍정']),
         '스코어_부정' : list(to_df['스코어_부정']),
         '전체건수' : len(to_df['코인명'])
         }) # 코인 및 상품리스트
    print(to_dict)


    ### 3. 비트코인 정보 데이터
    bit_info_df = pd.read_csv(file_path+'bitcoin_info_'+dt+'.csv', encoding='cp949',
                              dtype={'날짜':'str', '종가':'float', '오픈':'float', '고가':'float'
                                  , '저가':'float', 'RSI_3':'float', 'RSI_7':'float', 'RSI_14':'float'})

    # 가격 값 전체에 대한 평균
    df_size = bit_info_df[['종가', '오픈', '고가', '저가']].shape[0]*bit_info_df[['종가', '오픈', '고가', '저가']].shape[1]
    avg_value = bit_info_df[['종가', '오픈', '고가', '저가']].sum().sum()/df_size
    dv_max_value = abs(np.max(bit_info_df[['종가', '오픈', '고가', '저가']] - avg_value).max())

    # SCALING => 편차 / 편차의 최대 절대값 ( x <= 1 )
    scale_df = (bit_info_df[['종가', '오픈', '고가', '저가']] - avg_value) / dv_max_value
    scale_df.columns = [x+'_SCALING' for x in scale_df.columns]

    bit_info_df = pd.merge(bit_info_df, scale_df, left_index=True, right_index=True, how='left')
    bit_info_df = pd.merge(bit_info_df, bit_df[['등록시간', '스코어_SCALING']], left_on='날짜', right_on='등록시간',how='left')\
                        .drop(columns=['등록시간'])
    bit_info_df.sort_values(['날짜'], inplace=True) # 날짜 순으로 정렬
    gg_chart_df = bit_info_df[['날짜', '저가_SCALING', '오픈_SCALING', '종가_SCALING', '고가_SCALING', '스코어_SCALING', 'RSI_3', 'RSI_7', 'RSI_14']]

    # 컬럼 재배열 후 리스트 생성
    col_list = list(gg_chart_df.columns)[:5]
    candle_list = [col_list]
    # google chart 입력 순서(저가, 시가, 종가, 고가) => 양봉차트를 위한 데이터와 날짜 컬럼
    candle_list.extend(np.array(gg_chart_df[col_list]).tolist())
    print('candle_list : ', candle_list)

    # 지표 컬럼 및 데이터 리스트 생성
    col_list = list(gg_chart_df.columns)[5:] # 지표 컬럼 리스트 추출
    index_list = [col_list]
    # google chart 지표를 나타내는 선을 위한 index
    index_list.extend(np.array(gg_chart_df[col_list]).tolist())
    del scale_df

    bit_info_dict = dict({
                        '등록시간' : list(bit_info_df['날짜']),
                        '종가' : list(bit_info_df['종가']),
                        '오픈' : list(bit_info_df['오픈']),
                        '고가' : list(bit_info_df['고가']),
                        '저가' : list(bit_info_df['저가']),
                        '종가_SCALING': list(bit_info_df['종가_SCALING']),
                        '오픈_SCALING': list(bit_info_df['오픈_SCALING']),
                        '고가_SCALING': list(bit_info_df['고가_SCALING']),
                        '저가_SCALING': list(bit_info_df['저가_SCALING']),
                        '거래량' : list(bit_info_df['거래량']),
                        '변동' : list(bit_info_df['변동']),
                        # 'RSI_3' : list(bit_info_df['RSI_3']),
                        # 'RSI_7': list(bit_info_df['RSI_7']),
                        # 'RSI_14': list(bit_info_df['RSI_14']),
                        '전체건수' : len(bit_info_df),

    })
    print(gg_chart_df)

    bit_gg_dict = {
        'candle_data' : candle_list,
        'index_data' : index_list,
        '최대값': 1,
        '최소값': -1,
        '지표컬럼': col_list,
    }
    print(bit_gg_dict)


    return render_template('chart_js.html',to_dict=to_dict,bit_dict=bit_dict,bit_info_dict=bit_info_dict
                           ,bit_gg_dict=bit_gg_dict, btn_dt_index=btn_dt_index)


# @app.route('/result', methods = ['POST', 'GET']) # 접속 url
# def result():
#    if request.method == 'POST':
#       result = request.form
#       return render_template("result.html",result = result)

if __name__ == '__main__':
   app.run(debug = True)


