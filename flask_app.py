from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import datetime
import os
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler
app = Flask(__name__)

# 경로 설정 위치 고정 필요
# 파일경로 설정(기본 경로)
# file_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\' # 기본경로
# file_csv_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\static\\coin_data\\' #  코인 관련 csv 경로
# file_image_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\static\\images\\' # 코인 관련 image 경로

# 로컬 콘솔 실행 경로
file_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/coinkkagdugi/' # 기본경로
file_csv_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/coinkkagdugi/static/coin_data/' # 코인 관련 csv 경로
file_image_path = os.path.dirname(os.path.abspath(os.curdir)) + '/coinkkagdugi/coinkkagdugi/static/images/' # 코인 관련 image 경로

# 시간 설정(서버는 9시간 전 고려)
dt = datetime.datetime.today() + datetime.timedelta(hours=9)
dt = dt.strftime('%Y%m%d')
# 워드클라우드 버튼 기간 설정(일주일전 ~ 현재, 서버는 9시간 전 고려)
bf_dt = (datetime.datetime.today() - datetime.timedelta(days=6, hours=15)).strftime('%Y%m%d')
btn_dt_index = pd.date_range(start=bf_dt,end=dt).map(lambda x : str(x).replace(' 00:00:00', ''))


@app.route('/')
def chart():
    # 비트코인 긍부정 지수 데이터(30일 기준)
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

    # 딕셔너리(JSON) 타입으로 변경
    to_dict = dict({'코인명': list(to_df['코인명']),
                    '스코어_긍정': list(to_df['스코어_긍정_SCALING']),
                    '스코어_부정': list(to_df['스코어_부정_SCALING']),
                    '전체건수': len(to_df['코인명'])
                    })  # 코인 및 상품리스트
    print('#'*150+'\n', '코인별 긍부정 지수(오늘 기준) \n', to_dict.keys(),'\n 건수 :',len(to_df),'\n'+'#'*150)




    ## 3. 비트코인(바이낸스&업비트) 정보 데이터 ###
    bit_info_df = pd.read_csv(file_csv_path+'bitcoin_info_'+dt+'.csv',encoding='cp949',dtype='str')
    # 컬럼 타입 정의
    col_type_dict = dict()
    for x in bit_info_df.columns:
        if x in ['등록시간', '출처']:
            col_type_dict[x] = 'str'
        else:
            col_type_dict[x] = 'float'

    bit_info_df = bit_info_df.astype(col_type_dict) # 타입 변경

    # 스코어 긍부정 지수 merge
    bit_info_df = pd.merge(bit_info_df, bit_df[['등록시간','스코어_SCALING']], on=['등록시간'], how='left')

    # for문 출처에 따른 구분
    coin_firm = ['binance', 'upbit'] # 출처 구분
    for firm in coin_firm:
        # 출처에 따른 데이터 추출
        bit_firm_df = bit_info_df[bit_info_df['출처'] == firm]
        gg_col_list = [x for x in bit_firm_df.columns if x not in ['저가','오픈','종가','고가','거래량','출처']]
        # 컬럼 재배열 후 리스트 생성
        gg_chart_df = bit_firm_df[gg_col_list]
        col_list = list(gg_chart_df.columns)[:5] # 5열까지 : 등록시간,저가_SCALING,오픈_SCALING,종가_SCALING,고가_SCALING
        candle_list = [col_list]
        # google chart 입력 순서(저가, 시가, 종가, 고가) => 양봉차트를 위한 데이터와 날짜 컬럼
        candle_list.extend(np.array(bit_firm_df[col_list]).tolist())
        print('candle_list : ', candle_list)

        # 지표 컬럼 및 데이터 리스트 생성
        col_list = list(gg_chart_df.columns)[5:] # 지표 컬럼 리스트 추출
        index_list = [col_list]
        # google chart 지표를 나타내는 선을 위한 index
        index_list.extend(np.array(bit_firm_df[col_list]).tolist())

        # 딕셔너리 선언
        globals()['bit_'+firm+'_dict'] = dict({
                            '등록시간' : list(bit_firm_df['등록시간']),
                            '종가' : list(bit_firm_df['종가']),
                            '오픈' : list(bit_firm_df['오픈']),
                            '고가' : list(bit_firm_df['고가']),
                            '저가' : list(bit_firm_df['저가']),
                            '종가_SCALING': list(bit_firm_df['종가_SCALING']),
                            '오픈_SCALING': list(bit_firm_df['오픈_SCALING']),
                            '고가_SCALING': list(bit_firm_df['고가_SCALING']),
                            '저가_SCALING': list(bit_firm_df['저가_SCALING']),
                            '거래량' : list(bit_firm_df['거래량']),
                            # '변동' : list(bit_firm_df['변동']),
                            # 'RSI_3' : list(bit_firm_df['RSI_3']),
                            # 'RSI_7': list(bit_firm_df['RSI_7']),
                            # 'RSI_14': list(bit_firm_df['RSI_14']),
                            '전체건수' : len(bit_firm_df),

        })
        print('bit_'+firm+'_dict : ', globals()['bit_'+firm+'_dict'])

        globals()['bit_'+firm+'_gg_dict'] = {
            'candle_data' : candle_list,
            'index_data' : index_list,
            '최대값': 1,
            '최소값': -1,
            '지표컬럼': col_list,
        }
        print('bit_'+firm+'_gg_dict :',globals()['bit_'+firm+'_gg_dict'])

    # return to_dict, bit_dict, bit_binance_dict, bit_binance_gg_dict, bit_upbit_dict, bit_upbit_gg_dict
    return render_template('chart_js.html',to_dict=to_dict,bit_dict=bit_dict, btn_dt_index=btn_dt_index
                          ,bit_binance_dict=bit_binance_dict, bit_binance_gg_dict=bit_binance_gg_dict
                          ,bit_upbit_dict=bit_upbit_dict, bit_upbit_gg_dict=bit_upbit_gg_dict)






