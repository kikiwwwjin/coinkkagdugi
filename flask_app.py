from flask import Flask, render_template
import pandas as pd
import numpy as np
import datetime
import os
from sklearn.preprocessing import MaxAbsScaler
app = Flask(__name__)

# 경로 설정 위치 고정 필요
# 파일경로 설정(기본 경로)
# file_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\' # 기본경로
# file_csv_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\static\\coin_data\\' #  코인 관련 csv 경로
# file_image_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\static\\images\\' # 코인 관련 image 경로

# 로컬 콘솔 실행 경로
# file_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/coinkkagdugi/' # 기본경로
# file_csv_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/coinkkagdugi/static/coin_data/' # 코인 관련 csv 경로
# file_image_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/coinkkagdugi/static/images/' # 코인 관련 image 경로
file_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/' # 기본경로
file_csv_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/static/coin_data/' # 코인 관련 csv 경로
file_image_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/static/images/' # 코인 관련 image 경로

# 비트코인 관련 단어 사전 리스트 가져오기
from coin_word_dictionary import coin_noun_all
f_list, coin_nm_list, coin_jud_dict, prd_nm_list, prd_jud_dict, fin_nm_list, bit_men_list, csd_dict = coin_noun_all()

# 시간 설정(서버는 9시간 전 고려)
# dt = datetime.datetime.today() + datetime.timedelta(hours=9)
# dt = dt.strftime('%Y%m%d')
# # 워드클라우드 버튼 기간 설정(일주일전 ~ 현재, 서버는 9시간 전 고려)
# bf_dt = (datetime.datetime.today() - datetime.timedelta(days=6, hours=15)).strftime('%Y%m%d')
# btn_dt_index = pd.date_range(start=bf_dt,end=dt).map(lambda x : str(x).replace(' 00:00:00', ''))
dt = datetime.datetime.today()
dt = dt.strftime('%Y%m%d')


# 워드클라우드 버튼 기간 설정(일주일전 ~ 현재, 서버는 9시간 전 고려)
bf_dt = (datetime.datetime.today() - datetime.timedelta(days=7)).strftime('%Y%m%d')

bf_dt = '20210902'
dt = '20210909'

btn_dt_index = pd.date_range(start=bf_dt,end=dt).map(lambda x : str(x).replace(' 00:00:00', ''))

@app.route('/')
def chart():
    ### 1. 비트코인 긍부정 지수 데이터(30일 기준)
    bit_df = pd.read_csv(file_csv_path + 'bitcoin_idx_result_'+dt+'.csv',encoding='cp949',dtype='str')
    # 컬럼 타입 정의
    col_type_dict = dict()
    for x in bit_df.columns:
        if x in ['코인명', '등록시간']:
            col_type_dict[x] = 'str'
        else:
            col_type_dict[x] = 'float'
    bit_df = bit_df.astype(col_type_dict) # 타입 변경

    # 딕셔너리(JSON) 타입으로 변경
    bit_dict = dict({
        '등록시간': list(bit_df['등록시간']),
        '스코어_SCALING': list(bit_df['스코어_SCALING']),
        '스코어_합계': list(bit_df['스코어_합계']),
        '전체건수': len(bit_df)
    })  # 일자별 비트코인에 대한 긍부정 합계 스코어
    print('#'*150+'\n', '비트코인 긍부정 지수 딕셔너리 \n', bit_dict.keys(),'\n 건수 :',len(bit_df),'\n'+'#'*150)

    ### 2. 코인별 긍부정 지수(오늘 기준)
    to_df = pd.read_csv(file_csv_path + 'allcoin_idx_result_'+dt+'.csv',encoding='cp949',dtype='str')
    # 컬럼 타입 정의
    col_type_dict = dict()
    for x in to_df.columns:
        if x in ['코인명', '등록시간']:
            col_type_dict[x] = 'str'
        else:
            col_type_dict[x] = 'float'
    to_df = to_df.astype(col_type_dict)  # 타입 변경

    # 긍부정 스코어가 없는 코인은 제외
    # to_df = to_df[(to_df['스코어_긍정'] != 0) & (to_df['스코어_부정'] != 0)]

    # 딕셔너리(JSON) 타입으로 변경
    to_dict = dict({'코인명': list(to_df['코인명']),
                    '스코어_긍정': list(to_df['스코어_긍정_SCALING']),
                    '스코어_부정': list(to_df['스코어_부정_SCALING']),
                    '전체건수': len(to_df['코인명'])
                    })  # 코인 및 상품리스트
    print('#'*150+'\n', '코인별 긍부정 지수(오늘 기준) \n', to_dict.keys(),'\n 건수 :',len(to_df),'\n'+'#'*150)

    ### 3. 코인별 점유율 지수 데이터(주간 기준)
    freq_df = pd.read_csv(file_csv_path + '핵심단어_빈도수_' + dt + '.csv', encoding='cp949', dtype='str')
    # 컬럼 타입 정의
    col_type_dict = dict()
    for x in freq_df.columns:
        if x in ['명사', '등록시간']:
            col_type_dict[x] = 'str'
        else:
            col_type_dict[x] = 'float'
    freq_df = freq_df.astype(col_type_dict)  # 타입 변경
    coin_list = list(to_df['코인명'].unique())  # 코인리스트 추출
    alt_coin_df = freq_df[freq_df['명사'].isin(coin_list)] # 코인리스트에 대한 빈도수 데이터 프레임 추출
    # 주간(7일) 기준 및 알트코인 추출
    alt_coin_df = alt_coin_df[(alt_coin_df['등록시간'] > bf_dt) & (alt_coin_df['명사'] != '비트코인')]

    # 주간 알트 코인별 빈도수 합계 => 상위 7개 코인 추출
    alt_coin_df = alt_coin_df.groupby(['명사']).sum().reset_index().sort_values(['COUNT'], ascending=False)
    alt_coin_df = alt_coin_df.iloc[:7]
    alt_coin_df['점유율'] = alt_coin_df['COUNT']/alt_coin_df['COUNT'].sum()

    # 딕셔너리(JSON) 타입으로 변경
    alt_dict = dict({'코인명': list(alt_coin_df['명사']),
                    '빈도수': list(alt_coin_df['COUNT']),
                    '점유율': list(alt_coin_df['점유율']),
                    '전체건수': len(alt_coin_df['명사'])
                    })  # 코인 및 상품리스트
    print('#' * 150 + '\n', '코인별 점유율 지수 데이터(주간 기준) \n', alt_dict.keys(), '\n 건수 :', len(alt_dict['코인명']),
          '\n' + '#' * 150)

    ### 4. 코인 관련 인물별 점유율 지수 데이터(주간 기준) ###
    men_df = freq_df[freq_df['명사'].isin(bit_men_list) & (freq_df['등록시간'] > bf_dt)]  # 주간(7일) 기준 및 인물 추출

    # 주간 인물별 빈도수 합계 => 상위 3명 추출
    men_df = men_df.groupby(['명사']).sum().reset_index().sort_values(['COUNT'], ascending=False)
    men_df = men_df.iloc[:3]
    men_df['점유율'] = np.round((men_df['COUNT'] / men_df['COUNT'].sum())*100)
    print(men_df['점유율'])

    # 딕셔너리(JSON) 타입으로 변경
    men_dict = dict()
    cnt = 0
    for name, ocp_rt in zip(men_df['명사'], men_df['점유율']):
        print(name, ocp_rt)
        img_size = str(400 - cnt*100)
        print('사진 크기 :',img_size)
        men_dict[name] = [img_size, ocp_rt]
        cnt = cnt + 1

    print('#' * 150 + '\n', '코인 관련 인물별 점유율 지수 데이터(주간 기준) \n', men_dict.keys(), '\n 건수 :', men_dict, len(men_dict),
          '\n' + '#' * 150)


    ### 5. 비트코인(바이낸스&업비트) 정보 데이터 ###
    bit_info_df = pd.read_csv(file_csv_path+'bitcoin_price_idx_result_'+dt+'.csv',encoding='cp949',dtype='str')
    # 컬럼 타입 정의
    col_type_dict = dict()
    for x in bit_info_df.columns:
        if x in ['등록시간', '출처']:
            col_type_dict[x] = 'str'
        else:
            col_type_dict[x] = 'float'

    bit_info_df = bit_info_df.astype(col_type_dict) # 타입 변경

    # for문 출처 binance, upbit 에 따른 구분
    coin_firm = ['binance', 'upbit'] # 출처 구분
    for firm in coin_firm:
        print(firm)
        # 출처에 따른 데이터 추출
        bit_firm_df = bit_info_df[bit_info_df['출처'] == firm]

        # '종가' 컬럼만 SCAILING => 30일 기준(일별로 보는 비트코인에 대한 긍부정 지수 차트)
        ma_scaler = MaxAbsScaler()
        avg_value = np.nanmean(bit_firm_df['종가'].values)
        ma_scaler.fit(np.array(bit_firm_df['종가'] - avg_value).flatten().reshape(-1, 1))
        scale_data = ma_scaler.transform(np.array(bit_firm_df['종가'] - avg_value).flatten().reshape(-1,1))
        bit_firm_df['종가_SCALING'] = scale_data

        # 양봉 컬럼('등록시간','저가','오픈','종가','고가') 정의
        candle_col_list = ['등록시간','저가','오픈','종가','고가']
        # 지표 컬럼(종가_SCALING, RSI_3, RSI_7, RSI_14, 기준선, 전환선, 선행스팬_1, 선생스팬_2, 후행스팬, 스코어_SCALING) 정의
        temp_list = ['거래량','출처']
        temp_list.extend(candle_col_list) # 양봉 컬럼 + 거래량, 출처 컬럼
        idx_col_list = [x for x in bit_firm_df.columns if x not in temp_list] # 지표 컬럼

        # 캔들 차트를 위한 컬럼 Numpy화
        candle_list = ['일봉차트' if x == '저가' else x for x in candle_col_list]
        candle_list = [candle_list]

        # google chart 입력 순서(저가, 시가, 종가, 고가) Numpy 화 => 양봉차트를 위한 등록시간 및 양봉 데이터 컬럼
        candle_list.extend(np.array(bit_firm_df[candle_col_list]).tolist())
        print('양봉 데이터 candle_list : ', candle_list)

        # 지표 데이터 리스트 생성
        gg_chart_df = bit_firm_df[idx_col_list]  # 지표 컬럼만 추출한 데이터 프레임
        idx_list = [idx_col_list]
        # google chart 지표를 나타내는 선을 위한 index
        idx_list.extend(np.array(bit_firm_df[idx_col_list]).tolist())
        print('지수 데이터 idx_list : ', idx_list)

        # 일별로 보는 비트코인에 대한 긍부정 지수(바이낸스 기준) : 딕셔너리 선언
        globals()['bit_'+firm+'_dict'] = dict({
                            '등록시간' : list(bit_firm_df['등록시간']),
                            '종가_SCALING': list(bit_firm_df['종가_SCALING']), # 사용
                            '전체건수' : len(bit_firm_df),
        })
        
        # 바이낸스 및 업비트 지표
        globals()['bit_'+firm+'_gg_dict'] = {
            'candle_data' : candle_list,
            'index_data' : idx_list,
            '지표컬럼': idx_col_list
        }

        print('#' * 150 + '\n', '코인별 긍부정 지수(오늘 기준) \n', globals()['bit_'+firm+'_dict'].keys(), '\n 건수 :', len(globals()['bit_'+firm+'_dict']), '\n' + '#' * 150)
        print('#' * 150 + '\n', '코인별 긍부정 지수(오늘 기준) \n', globals()['bit_'+firm+'_gg_dict'].keys(), '\n 건수 :', len(globals()['bit_'+firm+'_gg_dict']), '\n' + '#' * 150)

    ### 코인 일별 종가 예측 결과 데이터 ###
    bit_score_df = pd.read_csv(file_csv_path + 'score_data_' + dt + '.csv', encoding='cp949',
                              dtype='str')


    bit_score_df = bit_score_df[['등록시간', 'target', '전통모델_pred', 'DNN_pred', 'LSTM_pred']]
    dt_max = bit_score_df['등록시간'].max()
    next_dt = datetime.datetime.strptime(dt_max, '%Y%m%d') + datetime.timedelta(days=1)
    next_dt = next_dt.strftime('%Y%m%d')
    bit_score_df['등록시간'] = bit_score_df['등록시간'].shift(-1)
    bit_score_df['등록시간'] = bit_score_df['등록시간'].fillna(next_dt)
    bit_score_df.rename(columns={'target' : '종가'}, inplace=True) # 'TARGET' 컬럼명을 '종가' 로 변경

    # 컬럼 타입 정의
    col_type_dict = dict()
    for x in bit_score_df.columns:
        if x in ['등록시간', '출처']:
            col_type_dict[x] = 'str'
        else:
            col_type_dict[x] = 'float'
    bit_score_df = bit_score_df.astype(col_type_dict)  # 컬럼 타입 변경

    # 딕셔너리(JSON) 타입으로 변경
    bit_score_dict = dict({'등록시간': list(bit_score_df['등록시간']),
                     '종가': list(bit_score_df['종가']),
                     '전통모델_예측값': list(bit_score_df['전통모델_pred']),
                     'DNN_예측값': list(bit_score_df['DNN_pred']),
                     'LSTM_예측값': list(bit_score_df['LSTM_pred'])
                     })  # 코인 및 상품리스트
    print('#' * 150 + '\n', '일별 종가 실제값 및 예측값\n', bit_score_dict.keys(), '\n 건수 :', len(bit_score_dict['등록시간']),
          '\n' + '#' * 150)

    # 코인 일별 종가 예측 결과 데이터
    model_idx_df = pd.read_csv(file_csv_path + 'model_idx_result_' + dt + '.csv', encoding='cp949',
                               dtype='str')
    # 컬럼 타입 정의
    col_type_dict = dict()
    for x in model_idx_df.columns:
        if x in ['Model', '출처']:
            col_type_dict[x] = 'str'
        else:
            col_type_dict[x] = 'float'
    model_idx_df = model_idx_df.astype(col_type_dict)  # 컬럼 타입 변경

    model_idx_dict = dict()
    for x in model_idx_df.iterrows():
        print(x[1].Model)
        model_idx_dict[x[1].Model] = [round(x[1].MAE), round(x[1].MSE), round(x[1].Accuracy*100), x[1].출처]

    print('#' * 150 + '\n', '일별 종가 실제값 및 예측값\n', model_idx_dict.keys(), '\n 건수 :', len(model_idx_dict),
          '\n' + '#' * 150)

    # return to_dict, bit_dict, bit_binance_dict, bit_binance_gg_dict, bit_upbit_dict, bit_upbit_gg_dict
    return render_template('chart_js.html',to_dict=to_dict,bit_dict=bit_dict, btn_dt_index=btn_dt_index, today_dt=dt
                          ,alt_dict=alt_dict, men_dict=men_dict
                          ,bit_binance_dict=bit_binance_dict, bit_binance_gg_dict=bit_binance_gg_dict
                          ,bit_upbit_dict=bit_upbit_dict, bit_upbit_gg_dict=bit_upbit_gg_dict
                          ,bit_score_dict=bit_score_dict, model_idx_dict=model_idx_dict)

if __name__=='__main__':
    app.run()

