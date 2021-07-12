# 패키지
import pandas as pd
import numpy as np
import copy
import xlrd
import re
import os
from tqdm import tqdm
import math
from ast import literal_eval

# 제어 관련 패키지
import time
from timeit import default_timer as timer
from datetime import timedelta
import datetime
from dateutil.relativedelta import relativedelta
import os
import pyautogui

# 크롤링 관련 패키지
from bs4 import BeautifulSoup
import requests
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

# NLP 관련 패키지
from soynlp import DoublespaceLineCorpus
from konlpy.tag import Twitter as o_twit
from ckonlpy.tag import Twitter as c_twit # 커스터마이즈 konlpy
from ckonlpy.tag import Postprocessor # ngram을 통해 복합명사를 만들어줌

# 문서 유사도 산출 패키지
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

# 워드클라우드 패키지
from wordcloud import WordCloud, STOPWORDS

##############################################################################################
# 데이터 전처리
# 1. 데이터 임포트
# 2. 데이터 전처리
# 3. 텍스트 마이닝(문맥 분석)
# 4. 스코어 산출
##############################################################################################


# corpus = DoublespaceLineCorpus(file_path+'2016-10-20.txt')

# # 형태소 분리 적용
# from soynlp.word import WordExtractor
# from soynlp.postagger import Dictionary
#
#
# Dictionary()
# word_ext = WordExtractor()
# word_ext.train(corpus)
# word_score = word_ext.extract()
#
#
# word_ext.accessor_variety('뉴스기사')


# 1. 데이터 불러오기

file_path = 'C:\\Users\\wai\\Desktop\\프로젝트\\암호화폐\\'
# file_path = 'D:\\암호화폐\\'

# 날짜 셋팅
today_dt = datetime.datetime.today()  # 오늘 날짜(적재 날짜)
today_dt = today_dt.strftime(format='%Y%m%d')  # 현재 시각

# 크롤링 데이터 리스트
f_list = ['coindesk', 'investing', 'naver', 'decenter']

# 코인명 리스트
coin_nm_list = ['암호화폐', '가상화폐', '비트코인', '메이저','알트코인', '라이트코인', '도지코인', '폴카닷', '디카르고', '에이다'
                , '마로', '페이코인', '썸씽', '이더리움 클래식', '이더리움', '비체인', '비트코인골드', '마로', '오브스', '모스코인'
                , '펀디엑스', '카르다노', '리플', '이오스', '엠블', '골렘', '엘프', '스톰엑스', '세럼', '트론', '비트토렌트', '가스'
                , '온톨로지가스', '던프로토콜', '스트라이크', '스텔라루멘', '스트라티스', '코모도']

# 코인 긍부정 용어 셋팅
coin_jud_dict ={'긍정' : ['상승', '급등', '호재', '상승세', '반등', '투자', '투자유치', '강세장', '호황', '뛰어난', '성장', '오르고', '올랐다'
                    , '하드포크', '소프트포크', '업데이트', '떡상', '추매', '에어드랍', '메인넷', '↑', '친환경', '환경친화적', '긍정']
                , '부정' : ['하락', '급락', '상폐', '상장폐지', '악재', '하락세', '떡락', '종결', '끝물', '추락', '약세', '대폭락', '내리고'
                    , '암흑기', '암흑', '↓', '환경파괴', '환경 파괴', '환경오염', '유의종목', '날벼락', '부정', '내렸다']} # 특정 비트코인에 한하여

# 상품 및 암호화폐 관련 용어 리스트
prd_nm_list = ['비트코인 ETF', 'ETF', '비트코인 파생상품', '암호화폐 파생상품', '가상자산 파생상품', '법정화폐', '채굴장', '채굴업체'
               , '채굴']

# 상품 긍부정 용어 셋팅
prd_jud_dict = {'긍정' : ['승인', '채택', '런칭']
                , '부정' : ['연기', '철회', '폐지', '폐쇄', '사라지다', '사라진다', '금지', '연장']}

# 금융 단어 용어 리스트
fin_nm_list = ['금리인상', '금리 인상', '인플레이션', '테이퍼링', 'CBDC', '디지털 원화', '디지털 화폐', '디지털 위안화', '디지털 달러'
               , '디지털원화', '디지털화폐', '디지털위안화', '디지털달러', '연준', '코인정리', '코인 정리', '업비트', '코인원'
               , '바이낸스', '골드만삭스', 'JP모건', '월가', '월 가', '증권거래위원회', '비트코인 상장지수펀드', '스테이킹']

# 비트코인 관련 인물
bit_men_list = ['은성수', '홍남기', '일론 머스크', '일론', '제롬 파웰', '제롬 파월', '옐런']


# 긍부정 단어 전체 리스트
coin_jud_list = sum(list(coin_jud_dict.values()),[])
prd_jud_list = sum(list(prd_jud_dict.values()),[])
jud_word_list = sum(list(coin_jud_dict.values()) + list(prd_jud_dict.values()),[])

# 전체 단어 리스트
all_word_list = jud_word_list + coin_nm_list + prd_nm_list + fin_nm_list + bit_men_list

# 복합명사 => 튜플형태로 전환
comp_word_list = [(tuple(x.split(' ')), 'Noun') for x in all_word_list if x.find(' ') != -1]

# 통폐합(동의어) 단어 딕셔너리
csd_dict = {
    '카르다노' : ['에이다'],
    '비트코인' : ['암호화폐', '가상화폐'],
}

# TWITTER CUSTOMIZED => 신조어(고유 명사) 코인명 파씽 인식
c_twit = c_twit()
c_twit.add_dictionary(words=coin_nm_list, tag='Noun')
c_twit.add_dictionary(words=prd_nm_list, tag='Noun')
c_twit.add_dictionary(words=fin_nm_list, tag='Noun')
c_twit.add_dictionary(words=jud_word_list, tag='Noun')

postpcsr = Postprocessor(base_tagger=c_twit, ngrams=comp_word_list)

# 기사 제목 및 기사 내용 파씽 및 문맥 분석
all_df = pd.DataFrame()
for f_nm in tqdm(f_list):
    print('텍스트 마이닝 대상 파일명 :', f_nm)
    # print('코인 or 상품에 따른 긍부정 단어 딕셔너리 :', score_dict)
    # f_nm = 'naver_crawling'
    # f_nm = 'coindesk'
    # f_nm = 'decenter'
    # 크롤링 파일 불러오기
    try:
        df = pd.read_csv(file_path+f_nm+'_crawling_'+today_dt+'.csv', encoding='cp949')
        df['ref_site'] = f_nm
        all_df = pd.concat([all_df, df])
    except:
        print(f_nm, '=> 해당 파일 부재')

all_df['doc_content'] = all_df['title'] + ' ' + all_df['content']
all_df['doc_content'] = all_df['doc_content'].str.replace('[', '').replace(']', '')
all_df = all_df.reset_index(drop=True) # 인덱스 리셋
all_passing_words = list()

for cont in all_df['doc_content']:
    print(cont)
    passing_words = postpcsr.pos(cont)
    passing_words = [x[0] for x in passing_words if re.sub('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]', '', x[0]) != '']
    all_passing_words.append(passing_words)



# TfidfVectorizer에 전체 파씽된 단어 학습
tfidf_vec = TfidfVectorizer()
tfidf_fit = tfidf_vec.fit(sum(all_passing_words, []))
len(tfidf_fit.vocabulary_)
all_word_dict = dict()
for k, v in sorted(tfidf_fit.vocabulary_.items()):
    # print(k, v)
    all_word_dict[k] = v


# 키 => 인덱스 순서대로 정렬
all_word_dict.fromkeys(sorted(all_word_dict.keys()))
sorted(tfidf_fit.vocabulary_.values())

tfidf_array = tfidf_fit.transform(all_df['doc_content']).toarray()
tfidf_df = pd.DataFrame(data=tfidf_array, columns=list(all_word_dict.keys()))

# 기사간 유사도 측정
sml_array = linear_kernel(tfidf_df)
# 유사도 80% 이상 문서 추출
sml_idx = np.where(sml_array >= 0.8)
sml_list = list()
for x, y in zip(sml_idx[0], sml_idx[1]):
    if x - y == 0:
        print(x, y, '자기 자신과의 유사도 비교한 값 => 의미 없음')
    else:
        print(x, y, '두개의 기사간 유사도가 비슷')
        if len(sml_list) != 0:
            if [y, x] in sml_list:
                print('중복은 넘어감')
            else:
                print('증복되지 않은 문서간 유사도 비슷')
                sml_list.append([x,y])
                continue

        else: # 최초 인덱스 담기
            sml_list.append([x, y])

# 유사한 문서 중 앞에 있는 문서 제거(유사도 80프로 이상 제거)
all_df.drop(index=[x[0] for x in sml_list], inplace=True)

###################################################################
# 1. 일별 분석
# 2. 당일 분석
############################################


# 분석 대상 날짜 리스트(크롤링 기간 설정 : 시작날짜 ~ 현재 or 마지막 날짜)
def t_delta(p_start_dt, p_last_dt):
    # 날짜 정보가 주어지지 않으면 오늘날짜만 크롤링
    for t in ['p_start_dt', 'p_last_dt']:
        if vars()[t] == '':
            vars()[t] = datetime.datetime.today().strftime('%Y%M%d')
    print('크롤링 기간 정보 :', p_start_dt, '~', p_last_dt)

    dt_index = pd.date_range(start=p_start_dt,end=p_last_dt)
    dt_list = dt_index.strftime('%Y-%m-%d 00:00:00').tolist()

    return dt_list # 크롤링 날짜 리스트 Return

start_dt = all_df['reg_date'].min().split(' ')[0] # 수집된 데이터 중 시작 날짜 추출
last_dt = all_df['reg_date'].max().split(' ')[0] # 수집된 데이터 중 마지막 날짜 추출
anal_dt_list = t_delta(p_start_dt=start_dt, p_last_dt=last_dt)


# 오늘 날짜 설정
today_dt = datetime.datetime.today().strftime('%Y%m%d')
# 명사 단어 빈도수 데이터 프레임 선언
all_freq_df = pd.DataFrame()
# anal_type = 'bf' # bf(9시전) or af(9시후)
# anal_type = 'af' # bf(9시전) or af(9시후)

# 분석 대상 나누기(시간 기준 : 오전 9시 => 개장 시간 기준)
# if anal_type == 'bf':
#     all_df = all_df[all_df['reg_date'] < '2021-06-23 09:00:00']
# else:
#     all_df = all_df[all_df['reg_date'] >= '2021-06-23 09:00:00']

# 등록시간 순으로 정렬
p_all_df = all_df
p_all_df.sort_values(['reg_date'], inplace=True)
p_all_df = p_all_df.reset_index(drop=True)

# 날짜별 분석을 따로 실시
for dt in tqdm(anal_dt_list):
    print('날짜 :', dt, '=> 데이터 추출')
    next_dt = datetime.datetime(year=int(dt[:4]),month=int(dt[5:7]),day=int(dt[8:10])) + datetime.timedelta(1)
    next_dt = next_dt.strftime('%Y-%m-%d HH:MM:DD')
    # 날짜별 크롤링 데이터 추출
    df = p_all_df[(p_all_df['reg_date'] >= dt) & (p_all_df['reg_date'] < next_dt)]

    # 코인에 따른 긍부정 단어 딕셔너리 선언
    score_dict = dict()
    # 코인명 => key 정의
    for nm in coin_nm_list + prd_nm_list:
        score_dict[nm] = list()

    # 명사 단어 리스트
    all_noun = list()

    ### 문맥 분석(특정 날짜 데이터)
    for title, content, reg in zip(df['title'], df['content'], df['reg_date']):
        print(content, type(content))
        l_con = literal_eval(content) # String => 코드 자체로 읽어 들이기 list화
        l_con.append(title) # 기사 제목도 기사 본문 내용처럼 함께 분석 대상에 포함
        for sentence in l_con:
            print('문장 :', sentence)
            # sentence = '비트코인은 오르고, 이더리움은 내렸다.'
            # sentence = '채굴장 90%이상 대폭락'
            sentence = postpcsr.pos(sentence)

            # 문맥(최대한 짧은 문장으로 쪼개서)
            # 1. 단(코인) 단(긍부정) / (코인 + 긍부정) Flag => 새로운 코인 초기화
            # 2. 단(코인) 다(긍부정) /
            # 3. 다(코인) 단(긍부정) /
            # 4. 다(코인) 다(긍부정) /
            # 5. 단(긍부정) 단(코인) / (긍부정 + 코인) Flag => 새로운 긍부정 초기화
            # 6. 단(긍부정) 다(코인) /
            # 5. 다(긍부정) 단(코인) /
            # 5. 다(긍부정) 다(코인) /

            # 명사만 all_noun 리스트에 담기
            all_noun.extend([x[0].replace(' - ', ' ') for x in sentence if x[1] == 'Noun'])

            # 문맥 분석을 위한 코인, 상품 및 플래그 선언(코인 및 상품 용어, 코인 및 상품 긍부정 용어)
            for m in ['coin', 'prd']:
                vars()[m+'_flag'] = False
                vars()[m+'_pn_flag'] = False
                vars()['temp_'+m+'_list'] = list()
                vars()['temp_'+m+'_jud_list'] = list()
                vars()['bf_'+m+'_info'] = ''
             # 직전 단어('긍부정' or '코인')에 대한 정보
            print('파씽 단어 :', sentence)

            count = 0
            for word in sentence:
                count += 1
                # 파씽 단어중 복합 단어의 '-'는
                word = word[0].replace(' - ', ' ')

                # print('파씽 단어 :', word)
                # 특정 코인 or 상품 단어 출현
                for m in ['prd', 'coin']:
                    print('단어 :', word, ', 키 :', m)
                    if word in vars()[m+'_nm_list']:
                        # 매핑 조건
                        # 이전에 코인 및 상품과 그에 대한 긍부정 단어가 출현을 했고, 직전 단어가 '코인' 및 '상품'이 아닐 경우 => 매핑 => 초기화
                        if (vars()[m+'_flag'] == True) and (vars()[m+'_pn_flag'] == True) and (vars()['bf_'+m+'_info'] == m+'pn'):
                            print('코인 출현, 긍부정 출현, 직전 출현 단어 정보와 불일치 => 매핑 => 초기화 작업')
                            print('bf_info 변수 :', vars()['bf_'+m+'_info'])
                            # 코인 및 상품 리스트 중복제거
                            vars()['temp_'+m+'_list'] = list(set(vars()['temp_'+m+'_list']))
                            print('코인 or 상품 출현 정보 :', vars()['temp_'+m+'_list'], '긍부정 출현 정보 :', vars()['temp_'+m+'_jud_list'])

                            # 코인리스트에 대한 긍부정리스트 매핑(2중 for문)
                            for coin_nm in vars()['temp_'+m+'_list']:
                                for jud_word in vars()['temp_'+m+'_jud_list']:
                                    score_dict[coin_nm].append(jud_word)  # 코인리스트에 긍부정 단어 매칭

                            # 코인, 긍부정 단어 리스트 초기화
                            vars()['temp_'+m+'_list'], vars()['temp_'+m+'_jud_list'] = list(), list()
                            vars()[m+'_flag'], vars()[m+'_pn_flag'] = False, False

                        # 코인 단어 출현 여부 및 직전 단어 정보 변수에 담기
                        vars()['bf_'+m+'_info'] = m
                        vars()[m+'_flag'] = True

                        # 긍부정 단어과 매핑을 위한 리스트에 담기
                        vars()['temp_'+m+'_list'].append(word)


                    # 긍부정 단어 출현
                    if word in vars()[m+'_jud_list']:
                        # 매핑 조건
                        # 이전에 코인과 긍부정 단어가 출현을 했고, 직전 단어가 '긍부정'이 아닐 경우 => 매핑 => 초기화
                        if (vars()[m+'_flag'] == True) and (vars()[m+'_pn_flag'] == True) and (vars()['bf_'+m+'_info'] == m):
                            print('코인 출현, 긍부정 출현, 직전 출현 단어 정보와 불일치 => 매핑 => 초기화 작업')
                            print('bf_info 변수 :', vars()['bf_'+m+'_info'])
                            print('코인 출현 정보 :', vars()['temp_'+m+'_list'], ', 긍부정 출현 정보 :', vars()['temp_'+m+'_jud_list'])

                            # 코인리스트에 대한 긍부정리스트 매핑(2중 for문)
                            for coin_nm in vars()['temp_'+m+'_list']:
                                for jud_word in vars()['temp_'+m+'_jud_list']:
                                    score_dict[coin_nm].append(jud_word)  # 코인리스트에 긍부정 단어 매칭

                            # 코인, 긍부정 단어 리스트 초기화
                            vars()['temp_'+m+'_list'], vars()['temp_'+m+'_jud_list'] = list(), list()
                            vars()[m+'_flag'], vars()[m+'_pn_flag'] = False, False

                        # 직전 단어 정보 변수에 담기
                        vars()['bf_'+m+'_info'] = m+'pn'
                        vars()[m+'_pn_flag'] = True

                        # 코인과 매핑을 위한 긍부정 단어리스트에 담기
                        vars()['temp_'+m+'_jud_list'].append(word)

                    # 초기화 하지 않은 경우 => 복합 적인 문맥 분석이 필요없을 경우 => 코인과 긍부정 단어 출현 존재시 매핑(문맥 분석이 끝나고)
                    if (vars()[m+'_flag'] == True) and (vars()[m+'_pn_flag'] == True) and len(sentence) == count:
                        print('문맥 분석 종료 => 코인 및 상품별 스코어링')
                        # 코인리스트 중복제거
                        vars()['temp_'+m+'_list'] = list(set(vars()['temp_'+m+'_list']))
                        print('코인 출현 정보 :', vars()['temp_'+m+'_list'], '긍부정 출현 정보 :', vars()['temp_'+m+'_jud_list'])
                        # 코인리스트에 대한 긍부정리스트 매핑(2중 for문)
                        for coin_nm in vars()['temp_'+m+'_list']:
                            for jud_word in vars()['temp_'+m+'_jud_list']:
                                score_dict[coin_nm].append(jud_word)  # 코인리스트에 긍부정
                        # 플래그 초기화
                        vars()[m + '_flag'] = False
                        vars()[m + '_pn_flag'] = False

    print('최종 코인 딕셔너리 :', score_dict)
    print('최종 명사 건수 :', len(all_noun))

    # 동의어 정리(Ex : 카르다노 - 에이다) => 앞에 있는 key로 통폐합
    for k, v_list in csd_dict.items():
        # 작업 전 k, v 값이 딕셔너리 존재하는 여부 확인
        try:
            # key 로 통합
            for v in v_list:
                score_dict[k].extend(score_dict[v])
                # 삭제
                score_dict.pop(v)
        except:
            print('key :',k,'value :',v,'딕셔너리에 존재하는 먼저 확인')

    # 코인에 대한 긍부정 스코어
    score_result_dict = dict()
    for x in ['coin', 'prd']:
        score_result_dict['스코어_'+x+'_긍정'] = list()
        score_result_dict['스코어_'+x+'_부정'] = list()

    coin_list = list() # 코인 리스트 선언
    prd_list = list() # 상품 및 기타 리스트 선언
    for k, v in score_dict.items():
        print(k, v)
        for m in ['coin', 'prd']:
            if k in vars()[m+'_nm_list']:
                vars()[m+'_list'].append(k)
                score_result_dict['스코어_'+m+'_긍정'].append(sum([1 if x in globals()[m+'_jud_dict']['긍정'] else 0 for x in v]))
                score_result_dict['스코어_'+m+'_부정'].append(sum([1 if x in globals()[m+'_jud_dict']['부정'] else 0 for x in v]))

    print(len(coin_list), len(score_result_dict['스코어_coin_긍정']), len(score_result_dict['스코어_coin_부정']), len(prd_list)
          , len(score_result_dict['스코어_prd_긍정']), len(score_result_dict['스코어_prd_긍정']))

    # 데이터 프레임화
    score_coin_df = pd.DataFrame({'코인명': coin_list, '스코어_긍정' : score_result_dict['스코어_coin_긍정']
                             , '스코어_부정' : score_result_dict['스코어_coin_부정'], '등록시간' : dt.split(' ')[0].replace('-','')})
    score_coin_df['스코어_합계'] = score_coin_df['스코어_긍정'] - score_coin_df['스코어_부정']

    score_prd_df = pd.DataFrame({'코인관련주어':prd_list, '스코어_긍정': score_result_dict['스코어_prd_긍정']
                                , '스코어_부정': score_result_dict['스코어_prd_부정'], '등록시간': dt.split(' ')[0].replace('-', '')})
    score_prd_df['스코어_합계'] = score_prd_df['스코어_긍정'] - score_prd_df['스코어_부정']
    # 스코어 및 빈도수 데이터 적재
    upload_fnm = file_path + 'score_' + today_dt + '.csv'
    print('적재 파일명 :', upload_fnm)
    if os.path.isfile(upload_fnm) == False:
        print('스코어 데이터 미존재 => 파일생성 및 적재')
        score_coin_df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('스코어 데이터 존재 => 적재')
        score_coin_df.to_csv(upload_fnm, index=False, mode='a', encoding='cp949', header=False)
    print('스코어 데이터 적재완료')


    # 코인 및 상품 매핑단어 데이터 적재
    score_dict_df = pd.DataFrame({'코인및상품명' : list(score_dict.keys()), '매핑단어' : list(score_dict.values())
                                 ,'등록시간' : dt.split(' ')[0].replace('-','')})
    upload_fnm = file_path + '코인및상품_매핑단어_'+today_dt+'.csv'
    if os.path.isfile(upload_fnm) == False:
        print('코인및상품_매핑단어 데이터 미존재 => 파일생성 및 적재')
        score_dict_df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('코인및상품_매핑단어 데이터 존재 => 적재')
        score_dict_df.to_csv(upload_fnm, index=False, mode='a', encoding='cp949', header=False)
    print('코인및상품_매핑단어 데이터 적재 완료')

    # 크롤링 데이터별 전체 추출된 명사에 대한 빈도수 => 데이터 프레임에 계속 merge(모든 기간 for문이 끝날때 까지)
    noun_key_df = pd.DataFrame(data = all_word_list, columns=['명사'])
    freq_df = pd.DataFrame({'명사': all_noun})
    freq_df = freq_df[freq_df['명사'].isin(all_word_list)].value_counts().reset_index()
    freq_df.columns = ['명사', 'COUNT']
    print('단어별 빈도수 데이터 프레임 : ','\n', freq_df)
    freq_df = pd.merge(noun_key_df, freq_df, on=['명사'], how='left')
    freq_df = freq_df.sort_values(['COUNT'], ascending=False)
    freq_df['등록시간'] = dt.split(' ')[0].replace('-','')
    freq_df = freq_df.fillna(0) # 결측치는 빈도수 => 0 으로 채움
    upload_fnm = file_path + '핵심단어_빈도수_' + today_dt + '.csv'
    if os.path.isfile(upload_fnm) == False:
        print('핵심 단어별 빈도수 데이터 미존재 => 파일생성 및 적재')
        freq_df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('핵심 단어별 빈도수 데이터 미존재 => 적재')
        freq_df.to_csv(upload_fnm, index=False, mode='a', encoding='cp949', header=False)
    print('핵심 단어별 빈도수 데이터 적재 완료')

    # 워드클라우드(일자별)
    freq_dict = dict()
    # for idx, noun in enumerate(freq_df['명사']):
    #     freq_dict[noun] = idx+1
    for noun, cnt in zip(freq_df['명사'], freq_df['COUNT']):
        freq_dict[noun] = cnt

    wc = WordCloud(width=400,height=400,background_color='white',font_path='C:\\Windows\\Fonts\\H2SA1M.TTF')\
        .generate_from_frequencies(freq_dict)
    wc.to_file('C:\\Users\\wai\\Anaconda3\\envs\\untitled\\암호화폐_텍스트마이닝\\static\\images\\wordcloud_'+dt.split(' ')[0].replace('-','')+'.jpg')

# 날짜에 대한 For문 종료

# upload_fnm = file_path + 'freq_' + today_dt + '.csv'
# all_freq_df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')

print('단어별 빈도수 데이터 적재 완료')


############################################################################################


ages = [0,10,15,13,21,23,37,31,43,80,61,20,41,32,100]
bins = [0,15,25,35,60,100]
labels = ['어린이', '청년', '장년', '중년', '노년']
cuts = pd.cut(ages, bins, right=True, include_lowest=True, labels=labels)

season = pd.DataFrame({'계절' : ['봄','여름','가을','겨울']})
season_dummies = pd.get_dummies(season['계절'])