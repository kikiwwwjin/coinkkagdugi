# 패키지
import pandas as pd
import numpy as np
import copy
import xlrd
import re
import os
from tqdm import tqdm
import math

# 제어 관련 패키지
import time
from timeit import default_timer as timer
from datetime import timedelta
import calendar
import datetime
from dateutil.relativedelta import relativedelta
import os

# 크롤링 관련 패키지
from bs4 import BeautifulSoup
import requests
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import webbrowser

# 시각화 툴
# import seaborn as sns
# import matplotlib.pyplot as plt

# 업비트 및 바이낸스 관련 패키지
import ccxt
import pyupbit

# IV값 산출 및 변수 선택 패키지
from xverse.transformer import MonotonicBinning

# SCALING 패키지
from sklearn.preprocessing import MinMaxScaler, MaxAbsScaler

# 모델관련 패키지
from pycaret.regression import *
import tensorflow as tf
from keras.utils.np_utils import to_categorical # DNN
from keras import models # DNN
from keras import layers # DNN

# 결과 지표 산출 패키지
from sklearn.metrics import mean_absolute_error, mean_squared_error


##############################################################################################
# 주제 : 암호 화폐 관련 기사의 텍스트 마이닝을 통한 동향 및 전망 분석
# 사이트
# 1. investing.com(암호화폐 뉴스)
# 2. 네이버 뉴스 검색 "비트코인" 최신순 정렬
# 3. 코인데스크 뉴스 => http://www.coindeskkorea.com/news/articleList.html?view_type=sm
# 4. 디센터 뉴스 => https://decenter.kr/NewsList/GZ03
# 서론 : 최근  암호화폐 시장에서의 뉴스 및 트위터의 영향이 주식 시장보다 시세 변동성이나 영향력이 강력하게 작용하는것으로 보아
#       텍스트 분석이 암호화폐 동향 및 전망 파악에 유의미 할 것이라고 판단
#
#

# 파일경로 설정

# 파일경로 설정(기본 경로)
# file_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\' # 기본경로
# file_csv_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\static\\coin_data\\' #  코인 관련 csv 경로
# file_image_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\static\\images\\' # 코인 관련 image 경로

# 로컬 콘솔 실행 경로
file_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\coinkkagdugi\\' # 기본경로
file_csv_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\coinkkagdugi\\static\\coin_data\\' # 코인 관련 csv 경로
file_image_path = os.path.dirname(os.path.abspath(os.curdir)) + '\\coinkkagdugi\\static\\images\\' # 코인 관련 image 경로

print('기본 경로 :', file_path)
print('CSV 파일 경로 :', file_csv_path)
print('이미지 파일 경로 :', file_image_path)

#####################################################################
# 1. investing.com(암호화폐 뉴스 url) 크롤링 함수 => 날짜 수집 30일
# bs4, request 함수로는 BAN 처리 당함 => 셀레니움만 가능
def investing_crawling(p_file_path):
    main_url = 'https://kr.investing.com/news/cryptocurrency-news/'
    print(p_file_path + 'chromedriver.exe')
    driver = webdriver.Chrome(p_file_path + 'chromedriver.exe')
    driver.get(main_url)  # url 접속
    time.sleep(0.5)
    # 페이지 소스 정보 => beautiful soup로 전환
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 팝업창 확인
    try:
        popup_info = soup.find_all(['div'], {'id': re.compile('.*PopUp.*')})  # 팝업창 있는지 확인
        if len(popup_info):
            print('팝업창 확인')
            for p_info in popup_info:
                popup_dict = p_info.find(['i', 'div', 'span'], {re.compile('.*close.*', re.I)}).attrs
                popup_attr = re.sub('[,\[\]\']', '', str(list(popup_dict.keys())))
                popup_str = re.sub('[,\[\]\']', '', str(sum(popup_dict.values(), [])[0]))

                if popup_attr == 'id':
                    driver.find_element(By.ID, popup_str).click()
                elif popup_attr == 'class':
                    driver.find_element(By.CLASS_NAME, popup_str).click()

    except:
        print('팝업창 없음')
    time.sleep(0.5)

    # 현재날짜 기준 30일보다 더 이전의 게시글이 존재할때 크롤링 for문 Break
    today_dt = datetime.datetime.today()
    ds = today_dt - datetime.timedelta(days=30)  # 30일 전날짜
    today_dt = today_dt.strftime('%Y%m%d')
    bf_dt = ds.strftime('%Y%m%d')

    # 오늘 날짜로 등록된 기사가 첫페이지의 전체이면 다음페이지도 오늘 날짜 기사를 확인해야함
    page_no = 0  # 크롤링 할 페이지 수크롤링 페이지 번호
    stop_flag = True
    stop_now_flag = True
    while stop_flag:
        # 특정 페이지의 오늘 날짜 기사 건수 확인
        page_no += 1
        print('페이지 번호 :', page_no)
        driver.get(main_url + str(page_no))  # 다음페이지 url 접속
        time.sleep(1)
        # 페이지 소스 정보 => beautiful soup로 전환
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        dt_list = soup.find('div', {'class': 'largeTitle'}).find_all('span', {'class': 'date'}) # 해당 페이지의 게시글 날짜리스트 수집
        dt_list = [today_dt if (x.text.find('시간') != -1) | (x.text.find('분') != -1) | (x.text.find('방금') != -1)
                   else re.sub('[^A-Za-z0-9가-힣↑↓]', '', x.text.replace('년', '').replace('월', '').replace('일', '')) for x in dt_list]

        # 30일 전보다 과거의 날짜가 있을시 Break
        dt_array = np.array(list(map(lambda x : int(x), dt_list)))

        # 특정 페이지에 있는 각 기사 정보 추출
        news_list = soup.find('div', {'class': 'largeTitle'}).find_all('div', {'class': 'textDiv'})

        # 30일 이전 등록기사가 존재할 때
        if min(dt_array) < int(bf_dt):
            print('30일보다 더 과거의 날짜 기사 :',min(dt_list),', Break!!!')
            stop_flag = False
            t_idx = np.where(dt_array < int(bf_dt))[0][0]
            if t_idx > 0:
                news_list = news_list[:t_idx]
            else:
                # 더이상 크롤링 대상 기사가 없음
                print('## 더이상 크롤링 수집 기간에 해당하는 기사가 없습니다. ##')
                stop_now_flag = False

        # 크롤링 즉시 중단 플래그
        if stop_now_flag == False:
            print('### CRAWLING NOW STOP FLAG FALSE ###')
            print('### 크롤링 즉시 종료 ###')
            break



        print('페이지 번호 :', page_no, ', 크롤링 대상 기사 건수 :', len(news_list))
        print('#' * 80)
        # 딕셔너리 선언
        news_dict = dict()
        news_dict['title'] = list()  # 기사 제목
        news_dict['reg_date'] = list()  # 등록일자
        news_dict['content'] = list()  # 기사 내용

        check_no = 0
        for news in news_list:
            check_no += 1
            print('기사 순번 ===>',check_no,'/',len(news_list))
            # 출처 사이트 => 'MK 부터' => 매일 경제 홈페이지 url로 직접 접속
            news_url = news.find('a',{'class':'title'}).get('href')
            # 태그가 div 또는 span 형태로 존재
            try:
                ref_site = news.find('span',{'class':'articleDetails'}).find('span').text
            except:
                ref_site = news.find('div', {'class': 'articleDetails'}).find('span').text

            if ref_site == '부터 MK':
                print('출처 ==> 매일경제')
                driver.get(news_url)
            elif ref_site == '부터 Investing.com Studios' or ref_site == '부터 asiae':
                print('파트너사 뉴스 또는 asiae 뉴스 => 제외')
                continue
            else:
                print('investing 자체 url로 접속')
                driver.get('https://kr.investing.com' + news_url)
            time.sleep(0.5)
            # 페이지 소스 요청
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')  # bs4 형태로 전환
            # 기사제목
            title = soup.find('h1', {'class': 'articleHeader'}).get_text()
            title = re.sub('[^A-Za-z0-9가-힣↑↓]', '', title)
            news_dict['title'].append(title)
            # 날짜 포맷 : 7 시간 전 (0000년 00월 00일 01:39) => YYYY-mm-dd %HH:%MM:%SS(년-월-일 시-분-초)
            reg = soup.find('div', {'class': 'contentSectionDetails'}).find('span').get_text()
            if (reg.find('시간') != -1) | (reg.find('분') != -1) | (reg.find('초') != -1):
                reg = reg.split('(')[1].replace(')', '')
            reg = datetime.datetime.strptime(reg, '%Y년 %m월 %d일 %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            news_dict['reg_date'].append(reg)
            # 기사 내용
            content_info = soup.find('div', {'class': 'articlePage'}).find_all('p')
            content_list = list()
            for content in content_info:
                ctt = re.sub('[^A-Za-z0-9가-힣↑↓]', '', content.get_text())
                print('기사내용 :', ctt)
                content_list.append(ctt)
            news_dict['content'].append(content_list)
            print('기사 제목 :', title, '=> 크롤링 성공')

        # 딕셔너리 데이터 프레임에 적재
        today_dt = datetime.datetime.today().strftime(format='%Y%m%d')  # 오늘 날짜(적재 날짜)
        upload_fnm = 'investing_crawling.csv'  # 적재 파일명
        f_list = os.path.splitext(p_file_path + 'static\\coin_data\\' + upload_fnm)
        upload_fnm = f_list[0] + '_' + today_dt + f_list[1]

        df = pd.DataFrame(news_dict)
        if os.path.isfile(upload_fnm) == False:
            print('인베스팅 크롤링 파일 미존재 => 파일생성 및 적재')
            df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
        else:
            print('인베스팅 크롤링 파일 존재 => 적재')
            df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')
        print('적재완료')
        print('#' * 80)

    print('크롬드라이브 세션 닫기')
    driver.close()
    print('investing.com 전체 기사 크롤링 완료')
    return
investing_crawling(p_file_path=file_path)

#####################################################################
# 2. 네이버 뉴스 검색 "비트코인" 언론사 및 최신순 => 뉴스기사 수집 30일

def naver_crawling(p_file_path):
    # 필요 변수 선언
    main_url = 'https://search.naver.com/search.naver?'
    # 해당 페이지에 기사가 있을때
    crawling_exec_flag = True
    # 언론사 코드
    news_firm = {
        '뉴시스': '1003'
    }
    today_dt = datetime.datetime.today()  # 오늘 날짜(적재 날짜)
    dt = today_dt.strftime(format='%Y.%m.%d')  # 현재 시간
    ds = today_dt - datetime.timedelta(days=30) # 30일 전날짜
    ds = ds.strftime(format='%Y.%m.%d') # 크롤링 시작 시간
    upload_fnm = 'naver_crawling.csv'  # 적재 파일명
    f_list = os.path.splitext(p_file_path + 'static\\coin_data\\' + upload_fnm)
    upload_fnm = f_list[0] + '_' + today_dt.strftime(format='%Y%m%d') + f_list[1]
    # 언론사 기준 for문
    for firm_nm, firm_cd in news_firm.items():
        # 첫번째 기사
        start_no = 1

        # 딕셔너리 선언
        news_dict = dict()
        news_dict['title'] = list()  # 기사 제목
        news_dict['reg_date'] = list()  # 등록일자
        news_dict['content'] = list()  # 기사 내용
        print('#' * 80)
        print('크롤링 언론사 :', firm_nm, ', 코드 :', firm_cd)
        while crawling_exec_flag:

            try:
                # 검색 조건 설정
                params = {'where': 'news'
                    , 'query': '비트코인'
                    , 'sm': 'tab_opt'
                    , 'sort': '1'
                    , 'photo': '0'
                    , 'field': '0'
                    , 'pd': '3'
                    , 'ds': ds  # 시작날짜 => 오늘날짜
                    , 'de': dt  # 종료날짜 => 오늘날짜
                    , 'docid': ''
                    , 'related': '0'
                    , 'mynews': '1'
                    , 'office_type': '2'
                    , 'office_section_code': '2'
                    , 'news_office_checked': firm_cd  # 언론사 코드
                    , 'nso': ''
                    , 'is_sug_officeid': '0'
                    , 'start': str(start_no)}  # 뉴스 넘버링
                p_param = parse.urlencode(params)  # 파라미터 인코딩
                # url 로 접속
                request_info = requests.get(main_url + p_param)
                html_co_cel = BeautifulSoup(request_info.text, 'html.parser')
                # 페이지 크롤링
                news_info = html_co_cel.find('ul', {'class': 'list_news'}).find_all('li', {'class': 'bx'})
                connect_cnt = len(news_info)  # 페이지당 기사 건수
                print('해당 페이지 기사 건수 :', connect_cnt)

                # 뉴스 회사마다 크롤링이 달라짐 => 선정 뉴스사 : 뉴시스
                # 뉴시스
                if firm_nm == '뉴시스':
                    for news in news_info:
                        print(news)
                        # 해당 뉴스 링크로 접속
                        link = news.find('a', {'class': 'news_tit'}).get('href')
                        article_info = requests.get(link)
                        time.sleep(0.5)
                        article_html = BeautifulSoup(article_info.text, 'html.parser')


                        # 뉴스 기사 제목
                        title = article_html.find('div', {'class': 'top'}).find('p').get_text()
                        title = re.sub('[^A-Za-z0-9가-힣↑↓]', '', title)
                        news_dict['title'].append(title)  # 기사 제목 담기

                        # 등록날짜
                        reg = article_html.find('div', {'class': 'infoLine'}).find('span').get_text()
                        if reg.find('|') != -1:
                            reg = reg.split('|')[0]
                        reg = reg.replace('등록', '').replace('/','-').replace(u'\xa0','').strip() # 등록일시 추출
                        news_dict['reg_date'].append(reg)

                        # 기사내용
                        cons_list = article_html.text.split('\n')
                        article_list = list()
                        article_flag = False
                        for cons in cons_list:
                            if cons.find('[서울=뉴시스]') != -1:
                                article_flag = True
                            elif cons.find('공감언론 뉴시스') != -1:
                                article_flag = False

                            # aritcle_flag : 기사 내용 여부(TRUE : 기사내용 , False : 기사 외 다른 내용)
                            if article_flag:
                                print('기사 내용 :', cons)
                                cons = re.sub('[^A-Za-z0-9가-힣↑↓\n]', '', cons) # 에러 발생 특수문자 제거
                                article_list.append(cons)

                        article_list = [x for x in article_list if x not in ['\r', '']] # '\r' or '' 는 리스트 요소에서 제거
                        news_dict['content'].append(article_list)

                        # 확인용 출력
                        print(firm_nm, ', 기사 제목 :', title, ', 등록날짜 :', reg, '내용:', article_list)

                start_no += connect_cnt  # 다음 페이지 설정


            # 기사 없는 url 까지 크롤링
            except:
                search_str = html_co_cel.find('div', {'class': 'not_found02'}).get_text()
                if search_str.find('검색결과가 없습니다') != -1:
                    print('더이상 비트코인에 관련된 뉴스가 없음')
                crawling_exec_flag = False

        df = pd.DataFrame(news_dict)
        df = df.drop_duplicates('title')  # 같은 제목의 기사는 중복 제거!!
        # df['new_ref'] = firm_nm
        print('딕셔너리 데이터 => 데이터 프레임화 완료')

        if os.path.isfile(upload_fnm) == False:
            print('로그 파일 미존재 => 파일생성 및 적재')
            df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
        else:
            print('로그 파일 존재 => 적재')
            df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')
        print('적재완료')
        print('#' * 80)

    print('크롤링 종료')
    return
naver_crawling(p_file_path=file_path)

########################################################################
# 3. 코인데스크 뉴스 => http://www.coindeskkorea.com/news/articleList.html?sc_day=1&sc_word=&sc_area=&view_type=sm&sc_order_by=E
# 출처 : 한겨레 기사
# 코인데이스크 크롤링 함수

def coindesk_crawling(p_file_path):
    print('############### coindesk_crawling 함수 시작 ##############')
    # 필요 변수 선언
    main_url = 'http://www.coindeskkorea.com/news/articleList.html?sc_day=1&sc_word=&sc_area=&view_type=sm&sc_order_by=E'
    params = {'page': '1'}
    p_param = parse.urlencode(params)
    request_info = requests.get(main_url + p_param)
    html_info = BeautifulSoup(request_info.text, 'html.parser')

    # 접속 url
    try:
        link_info = html_info.find('li', {'class': 'pagination-start'}).find('a').get('href')
        total_cnt = int([x for x in link_info.split('&') if x.find('total') != -1][0].replace('total=', ''))  # 현재 날짜에 대한 전체 뉴스 건수
    except:
        print('오늘 날짜에 대한 정보가 없음')
        return



    # 1 페이지당 최대 20개의 뉴스 기사
    today_dt = datetime.datetime.today()  # 오늘 날짜(적재 날짜)

    if total_cnt != 0:
        print('현재 날짜 :', today_dt.strftime(format='%Y-%m-%d'), '등록된 기사 존재 => 크롤링 시작')
    else:
        print('현재 날짜에 등록된 기사가 부재 => 크롤링 취소')





    # 딕셔너리 선언
    news_dict = dict()
    news_dict['title'] = list()  # 기사 제목
    news_dict['reg_date'] = list()  # 등록일자
    news_dict['content'] = list()  # 기사 내용

    # 크롤링 코드
    page_no = math.ceil(total_cnt / 20)  # 크롤링 해야할 전체 페이지 수
    for no in range(1, page_no + 1):
        print('페이지 번호 :', no, ', url 접속')

        # 특정 페이지로 접속
        params = {'page': str(no)}
        p_param = parse.urlencode(params)
        request_info = requests.get(main_url + p_param)
        html_info = BeautifulSoup(request_info.text, 'html.parser')
        time.sleep(0.5)

        # 페이지 기사 정보 리스트
        article_info = html_info.find('div', {'class', 'article-list'}).find_all('div', {'class': 'text-block'})

        for article in article_info:
            # print(article)
            link = article.find('div', {'class': 'list-titles'}).find('a').get('href')
            request_info = requests.get('http://www.coindeskkorea.com' + link)
            html_info = BeautifulSoup(request_info.text, 'html.parser')

            # 기사 제목
            title = html_info.find('div', {'class': 'article-head-title'}).text
            title = re.sub('[^A-Za-z0-9가-힣↑↓]', '', title)
            news_dict['title'].append(title)


            # 등록 날짜
            reg = html_info.find('div', {'class': 'editors-p'}).find('span', {'class': 'updated'}).text
            reg = datetime.datetime.strptime(reg, '%Y년 %m월%d일 %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            news_dict['reg_date'].append(reg)

            # 기사 내용
            html_info.find('div', {'id': 'article-view-content-div'}).find_all('h3')  # 소제목

            # 내용
            ctt_list = list()
            for p_info in html_info.find('div', {'id': 'article-view-content-div'}).find_all('p'):
                print(p_info.text)
                content = re.sub('[^A-Za-z0-9가-힣↑↓]', '', p_info.text)
                ctt_list.append(content)

            ctt_list = [x for x in ctt_list if x != '']

            # 기사 내용 적재
            news_dict['content'].append(ctt_list)

    # 데이터 프레임화
    df = pd.DataFrame(news_dict)
    df = df.drop_duplicates('title')  # 같은 제목의 기사는 중복 제거!!

    print('딕셔너리 데이터 => 데이터 프레임화 완료')

    # 적재할 파일명 설정
    today_dt = datetime.datetime.today()  # 오늘 날짜(적재 날짜)
    dt = today_dt.strftime(format='%Y.%m.%d')  # 현재 시각
    upload_fnm = 'coindesk_crawling.csv'  # 적재 파일명
    f_list = os.path.splitext(p_file_path + 'static\\coin_data\\' + upload_fnm)
    upload_fnm = f_list[0] + '_' + today_dt.strftime(format='%Y%m%d') + f_list[1]

    if os.path.isfile(upload_fnm) == False:
        print('로그 파일 미존재 => 파일생성 및 적재')
        df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('로그 파일 존재 => 적재')
        df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')
    print('적재완료')
    print('#' * 80)

    return
coindesk_crawling(p_file_path=file_path)

########################################################################
# 4. Decenter.kr 뉴스 => https://decenter.kr/NewsList/GZ03
# 출처 : Decenter
# 디센터(블록체인) 크롤링 함수

def decenter_crawling(p_file_path):
    main_url = 'https://decenter.kr/NewsList/GZ03'
    driver = webdriver.Chrome(file_path + 'chromedriver.exe')
    driver.get(main_url)  # url 접속
    time.sleep(0.5)
    # 페이지 소스 정보 => beautiful soup로 전환
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 배치 주기(일별) => 오늘 날짜인 것만 크롤링, 사이트는 최신순으로 자동정렬
    # 오늘 날짜
    t_dt = datetime.datetime.today().strftime('%Y-%m-%d')
    # 뉴스 게시물 건수 확인(기사는 최신순 정렬)
    dt_list = soup.find('ul', {'class' : 'news_list'}).find_all('span',{'class':'letter'})
    connect_cnt = len([x.text for x in dt_list if x.text == t_dt])

    # 딕셔너리 선언
    news_dict = dict()
    news_dict['title'] = list()  # 기사 제목
    news_dict['reg_date'] = list()  # 등록일자
    news_dict['content'] = list()  # 기사 내용

    # 오늘 날짜로 등록된 기사가 첫페이지의 전체이면 다음페이지도 오늘 날짜 기사를 확인해야함
    page_no = 1
    if connect_cnt != len(dt_list):
        # 뉴스 기사 정보 크롤링(오늘 날짜만 크롤링)
        article_info = soup.find('ul', {'class': 'news_list'})
        for atc in article_info.find_all('li'):
            print(atc)
            # 특정 기사 날짜 정보
            dt = atc.find('span', {'class': 'letter'}).text
            if t_dt != dt:
                continue  # 기사 날짜가 오늘 날짜가 아니면 넘긴다.(오늘 날짜로 등록된 기사만 추출)


            # 기사 링크
            atc_link = atc.find('a').get('href')
            # 링크로 접속
            html = requests.get('https://decenter.kr' + atc_link)
            soup = BeautifulSoup(html.text, 'html.parser')
            atc_info = soup.find('div', {'class': 'sub_view'})

            # 기사 제목
            title = atc_info.find('h2').text
            title = re.sub('[^A-Za-z0-9가-힣↑↓]', '', title)
            news_dict['title'].append(title)
            # 기사 내용
            c_list = soup.find_all('br')
            c_list = list(map(lambda x: re.sub('[^A-Za-z0-9가-힣↑↓]', '', x.text), c_list))
            c_list = [x for x in c_list if x != '']
            news_dict['content'].append(c_list)
            # 등록 일시(수정 기준)
            reg = re.sub('[\n\r수정]', '', atc_info.find_all('span',{'class':'url_txt'})[1].text).strip()
            news_dict['reg_date'].append(reg)  # 기사 날짜 정보 담기

            print('기사 제목 :', title, '=> 크롤링 성공')

        print(page_no, '페이지 전체 건수 :', len(dt_list), ', 오늘 날짜 기사 건수 :', connect_cnt)


    else:
        while connect_cnt == len(dt_list):
            # 특정 페이지의 오늘 날짜 기사 건수 확인
            if page_no >= 2:
                print('페이지 번호 :', page_no)
                driver.get(main_url)  # url 접속
                time.sleep(0.5)
                # 다음페이지 클릭
                driver.find_element(By.CLASS_NAME, 'deskPage').find_element(By.CLASS_NAME, 'e_next').click()
                # 다음페이지 정보 가져오기
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                # 뉴스 게시물 건수 확인
                dt_list = soup.find('ul', {'class': 'news_list'}).find_all('span', {'class': 'letter'})
                connect_cnt = len([x.text for x in dt_list if x.text == t_dt])

            # 뉴스 기사 정보 크롤링(오늘 날짜만 크롤링)
            article_info = soup.find('ul', {'class': 'news_list'})
            for atc in article_info.find_all('li'):
                print(atc)
                # 특정 기사 날짜 정보
                dt = atc.find('span',{'class':'letter'}).text
                if t_dt != dt:
                    continue # 기사 날짜가 오늘 날짜가 아니면 넘긴다.(오늘 날짜로 등록된 기사만 추출)

                # 기사 링크
                atc_link = atc.find('a').get('href')
                # 링크로 접속
                html = requests.get('https://decenter.kr'+atc_link)
                soup = BeautifulSoup(html.text, 'html.parser')
                atc_info = soup.find('div',{'class':'sub_view'})

                # 기사 제목
                title = atc_info.find('h2').text
                title = re.sub('[^A-Za-z0-9가-힣↑↓]', '', title)
                news_dict['title'].append(title)

                # 기사 내용
                c_list = soup.find_all('br')
                c_list = list(map(lambda x: re.sub('[^A-Za-z0-9가-힣↑↓]', '', x.text), c_list))
                c_list = [x for x in c_list if x != '']
                news_dict['content'].append(c_list)
                print('기사 제목 :', title, '=> 크롤링 성공')

                # 등록 일시
                reg = atc_info.find('li', {'class': 'letter'}).text
                news_dict['reg_date'].append(reg)  # 기사 날짜 정보 담기

            print(page_no, '페이지 전체 건수 :', len(dt_list), ', 오늘 날짜 기사 건수 :', connect_cnt)
            page_no += 1 # 페이지 수 변수


    # 크롤링 코드
    today_dt = datetime.datetime.today().strftime(format='%Y%m%d')  # 오늘 날짜(적재 날짜)
    upload_fnm = 'decenter_crawling.csv'  # 적재 파일명
    f_list = os.path.splitext(p_file_path + 'static\\coin_data\\' + upload_fnm)
    upload_fnm = f_list[0] + '_' + today_dt + f_list[1]



    # 딕셔너리 데이터 프레임에 적재
    df = pd.DataFrame(news_dict)
    if os.path.isfile(upload_fnm) == False:
        print('디센터 크롤링 파일 미존재 => 파일생성 및 적재')
        df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('디센터 크롤링 파일 존재 => 적재')
        df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')
    print('적재완료')
    print('#' * 80)

    print('크롬드라이브 세션 닫기')
    driver.close()

    print('decenter.com 전체 기사 크롤링 완료')
    return
decenter_crawling(p_file_path=file_path)


########################################################################
# 5. 바이낸스 기준 비트코인 일별 시세 크롤링
def binance_info_crawling(p_file_path, p_start_date, p_end_date):
    main_url = 'https://kr.investing.com/crypto/bitcoin/historical-data' # 비트코인 데이터 제공 사이트
    driver = webdriver.Chrome(p_file_path + 'chromedriver.exe')
    driver.get(main_url)  # url 접속
    time.sleep(0.5)
    # 페이지 소스 정보 => beautiful soup로 전환
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 팝업창 확인
    try:
        popup_info = soup.find_all(['div'], {'id': re.compile('.*PopUp.*')})  # 팝업창 있는지 확인
        if len(popup_info):
            print('팝업창 확인')

            # 팝업창 닫기 클릭
            driver.find_elements_by_xpath('//*[@id="PromoteSignUpPopUp"]/div[2]/i')[0].click()

    except:
        print('팝업창 없음')

    # 기간 설정
    driver.find_element(By.ID, 'data_interval').click() # 기간 박스란 클릭
    time.sleep(0.3)
    driver.find_element_by_xpath('//*[@id="data_interval"]/option[1]').click() # "일간" 클릭
    time.sleep(0.3)

    # 날짜 설정
    driver.find_element(By.ID, 'widgetFieldDateRange').click() # 날짜 박스 클릭
    time.sleep(0.3)
    driver.find_element(By.ID, 'startDate').clear()
    driver.find_element(By.ID, 'startDate').send_keys(p_start_date)
    driver.find_element(By.ID, 'endDate').clear()
    driver.find_element(By.ID, 'endDate').send_keys(p_end_date)
    driver.find_element(By.ID, 'applyBtn').click() # 확인 클릭
    time.sleep(0.5)

    # 내용 수집하기
    # 페이지 소스 정보 => beautiful soup로 전환
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content_info = soup.find('div', {'id':'results_box'}).find_all('td')
    print(content_info)
    cnt = 0
    con_list = list()
    all_con_list = list()
    for con in content_info[:-5]: # 마지막 5개 원소는 필요 없음
        con = con.text
        cnt += 1
        con_list.append(con)
        if cnt%7 == 0:
            print(con_list)
            all_con_list.append(con_list)
            con_list = list()  # 리스트 초기화

    bit_df = pd.DataFrame(data=all_con_list, columns=['등록시간', '종가', '오픈', '고가', '저가', '거래량', '변동'])
    bit_df = bit_df.applymap(lambda x: x.replace(',', ''))
    # 비트코인 시세 및 동향 데이터 전처리
    bit_df['등록시간'] = bit_df['등록시간'].map(lambda x: re.sub('[년월일 ]', '', x))
    # 거래량(K), 변동(%), ADJ_조정 단위처리
    bit_df = bit_df.astype({'종가': float, '오픈': float, '저가': float, '고가': float})
    bit_df['거래량'] = bit_df['거래량'].apply(lambda x: float(x.replace('K', '')) * 1000)
    bit_df['변동'] = bit_df['변동'].apply(lambda x: float(x.replace('%', '')) * 0.01)

    # 33347.1 (7/5) 35298.2 (7/4)
    # RSI 지표 산출
    # bit_df_2 = bit_df.set_index(pd.DatetimeIndex(bit_df['날짜'].values))
    bit_df['ADJ_종가'] = bit_df['종가']
    bit_df = bit_df.sort_values(['등록시간'], ascending=True)
    delta = bit_df['ADJ_종가'].diff(1)
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()

    # 상승폭 및 하락폭
    up[up < 0] = 0
    down[down > 0] = 0

    # 기간 가져오기
    period_list = [3, 7, 14]  # 3, 7, 14일 평균값을 구하기 위한 일정 기간 세팅, rolling 함수는 이동평균함수
    for p in period_list:
        avg_gain = up.rolling(window=p).mean() # 상승 평균
        avg_loss = abs(down.rolling(window=p).mean()) # 하락 평균

        # Calculate the RSI
        # Calculate the Relative Strength (RS)
        rs = avg_gain / avg_loss # 일정기간동안의 상승평균 / 하락평균
        rsi = 1.0 - (1.0 / (1.0 + rs)) # rs 값과 rs index와 비례관계

        bit_df['RSI_'+str(p)] = rsi

    ### 일목균형표 ###

    # 전환선(기간 : 9일)
    nine_high = bit_df['고가'].rolling(window=9).max()
    nine_low = bit_df['저가'].rolling(window=9).min()
    bit_df['전환선'] = (nine_high + nine_low) / 2  # 전환선

    # 기준선(기간 : 26일)
    p_ts_high = bit_df['고가'].rolling(window=26).max()
    p_ts_low = bit_df['저가'].rolling(window=26).min()
    bit_df['기준선'] = (p_ts_high + p_ts_low) / 2

    # 선행스팬 1({전환선 + 기준선}/2, 26일 선행하여 배치)
    bit_df['선행스팬_1'] = ((bit_df['전환선'] + bit_df['기준선']) / 2).shift(26)

    # 선행스팬 2(52일 선행하여 배치)
    p_ft_high = bit_df['고가'].rolling(window=52).max()
    p_ft_min = bit_df['저가'].rolling(window=52).min()
    bit_df['선행스팬_2'] = ((p_ft_high + p_ft_min) / 2).shift(26)

    # 후행스팬
    bit_df['후행스팬'] = bit_df['종가'].shift(-26)

    # 분석 기법 1 : '구름' => 선행스팬 1, 선행스팬 2의 사이!!
    # 분석 기법 2 : 전환선과 기준선의 관계 => 1. 기준선(26일, 중기) 중기적인 추세를 얘기하고 상승, 하락 추세를 어느정도 판별
    #                                       2. 전환선(9일, 단기) 이 기준선을 역전하는가??? => 중기 및 단기 상승, 하락 추세를 결정
    #

    # # 가격 값 전체에 대한 평균
    # df_size = bit_df[['종가', '오픈', '고가', '저가']].shape[0] * bit_df[['종가', '오픈', '고가', '저가']].shape[1]
    # avg_value = bit_df[['종가', '오픈', '고가', '저가']].sum().sum() / df_size
    # dv_max_value = abs(np.max(bit_df[['종가', '오픈', '고가', '저가']] - avg_value).max())
    #
    # # SCALING => 편차 / 편차의 최대 절대값 (산출값 <= 1 )
    # scale_df = (bit_df[['종가', '오픈', '고가', '저가', '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬']] - avg_value) / dv_max_value
    # scale_df.columns = [x + '_SCALING' for x in scale_df.columns]
    #
    # bit_df = pd.merge(bit_df, scale_df, left_index=True, right_index=True, how='left')
    c_bd = (datetime.datetime.today() - datetime.timedelta(days=99)).strftime('%Y%m%d')  # 일봉 차트 기준(100일)
    bit_df = bit_df[bit_df['등록시간'] >= c_bd]
    scale_col = ['종가', '오픈', '고가', '저가', '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬']
    ma_scaler = MaxAbsScaler()
    avg_value = np.nanmean(bit_df[scale_col].values)
    ma_scaler.fit(np.array(bit_df[scale_col] - avg_value).flatten().reshape(-1, 1))
    scale_data = ma_scaler.transform(np.array(bit_df[scale_col] - avg_value))
    scale_df = pd.DataFrame(data=scale_data, columns=scale_col, index=bit_df.index)
    scale_df.columns = [x + '_SCALING' for x in scale_df.columns]

    # 스케일링 데이터 Merge
    bit_df = pd.concat([bit_df, scale_df], axis=1)
    print(bit_df, '스케일링 MERGE 완료')


    # 컬럼 재배치 및 수정
    bit_df = bit_df[['등록시간', '저가', '오픈', '종가', '고가', '거래량',
                     '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬',
                     'RSI_3', 'RSI_7', 'RSI_14']]

    # 출처 컬럼 생성
    bit_df['출처'] = 'binance'

    # 크롤링 코드
    today_dt = datetime.datetime.today().strftime(format='%Y%m%d')  # 오늘 날짜(적재 날짜)
    upload_fnm = 'bitcoin_info.csv'  # 적재 파일명
    f_list = os.path.splitext(p_file_path + 'static\\coin_data\\' + upload_fnm)
    upload_fnm = f_list[0] + '_' + today_dt + f_list[1]

    # 딕셔너리 데이터 프레임에 적재
    if os.path.isfile(upload_fnm) == False:
        print('비트코인 정보 파일 미존재 => 파일생성 및 적재')
        bit_df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('비트코인 정보 파일 존재 => 적재')
        bit_df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')
    print('적재완료')
    print('#' * 80)

    print('크롬드라이브 세션 닫기')
    driver.close()

    print('비트코인 정보 데이터 크롤링 및 적재 완료')
    return

# 기본 세팅 기간 99일 전(오늘 꺼까지 포함하면 총 100일)
bd = (datetime.datetime.today() - datetime.timedelta(days=200)).strftime('%Y/%m/%d')
td = datetime.datetime.today().strftime('%Y/%m/%d')
binance_info_crawling(p_file_path=file_path, p_start_date=bd, p_end_date=td)


########################################################################
# 6. 업비트 API를 활용한 데이터 수집 (차트 일봉 기준 => 현재 날짜 ~ 100일전 기준)
########################################################################
def upbit_api_modeling(p_file_path, p_interval):
    print('#' * 80)
    print('#'*30, '업비트 API 데이터 수집', '#'*30)
    ac_key = 'BFQ8XewRvrFJTQcsCDrAuGCdxVRmH9Ixphdezydf'
    sc_key = 'yhx6TyxAdZJxBZtSMBJyTeRC8pF4PLpuN0YGbwTJ'
    upbit = pyupbit.Upbit(ac_key, sc_key)
    # upbit.get_avg_buy_price('KRW-BTC') - pyupbit.get_current_price(['KRW-BTC'])['KRW-BTC']
    # upbit.get_amount()
    # upbit.get_balance('KRW-BTC') # 코인 보유량

    # 업비트 코인별 현재 가격 조회
    # pyupbit.get_current_price(['KRW-BTC', 'KRW-ETH', 'KRW-XRP', 'KRW-CBK'])
    # pyupbit.get_ohlcv()
    # 시가, 고가, 저가, 종가, 거래량(volume)
    # option => ticker : 조회를 원하는 심볼값, interval : 조회 하고자하는 차트 종류(분, 일..), count : 조회 데이터 건수 (캔들 개수
    # interval 값 예시 : day, minute1, minute5, minute10, minute15, minute30, minute60, minute240, week, month
    # 모델 설계 : 현재 시간 ~ 1달(5분단위 데이터 수집)

    # 우선 일단위로 해서 바이낸스 차트와 동일하게
    # 전체 데이터 수집기간 : 비트고인 시작(2017년 9월 25일) ~ 하루전날짜
    # 학습 데이터 기간 : 2년 6개월
    # 검증 데이터 기간 : 2년 6개월 이후 나머지 기간(최근)
    bd = datetime.datetime(year=2017, month=9, day=25)
    c_bd = (datetime.datetime.today() - datetime.timedelta(days=99)).strftime('%Y%m%d')# 일봉 차트 기준(100일)
    data_term = (datetime.datetime.today() - bd).days + 1 # 비트코인 시작날 포함 +1

    # 오늘 날짜

    today_dt = datetime.datetime.today().strftime('%Y%m%d')
    # 데이터 가져오기
    upbit_df = pyupbit.get_ohlcv(ticker='KRW-BTC', interval=p_interval, count=data_term) # count +1

    # 컬럼명 수정
    upbit_df.columns =['오픈','고가','저가','종가','거래량','value']

    if interval == 'day':
        upbit_df['등록시간'] = list(map(lambda x: x.strftime(format='%Y%m%d'), list(upbit_df.index)))
        upbit_df.index = pd.to_datetime(list(map(lambda x: x.strftime(format='%Y%m%d'), list(upbit_df.index))), format='%Y%m%d')

    ### 이동평균선 산출 ###
    # 이동 평균선 기간 설정 : 5, 10, 20, 60, 120일 기준
    for p in [5, 10, 20, 60, 120]:
        print('업비트 종가 기준 => 이동평균선',str(p)+'일 산출 완료')
        upbit_df['이동평균선_'+str(p)] = upbit_df['종가'].rolling(window=p).mean()



    ### RSI 지표 산출 ###
    upbit_df.sort_index(ascending=True, inplace=True) # 인덱스(날짜 및 시간) 오름차순 정렬
    pd.to_datetime(list(upbit_df.index), format='%Y-%m-%d')
    upbit_df['ADJ_종가'] = upbit_df['종가']
    delta = upbit_df['ADJ_종가'].diff(1) # 현재날짜-전날짜 종가ㅁ

    # RSI를 산출하기위한 데이터프레임 선언
    delta = delta.dropna()
    up = delta.copy()
    down = delta.copy()
    # 전날 대비 가격 상승 및 하락폭 산출
    up[up < 0] = 0 # 전날 대비 가격 상승폭
    down[down > 0] = 0 # 전날 대비 가격 하락폭

    # 기간 가져오기
    period_list = [3, 7, 14]  # 3, 7, 14일 평균값을 구하기 위한 일정 기간 세팅, rolling 함수는 이동평균함수
    for p in period_list:

        avg_gain = up.rolling(window=p).mean() # 상승 평균
        avg_loss = abs(down.rolling(window=p).mean()) # 하락 평균
        # print(p, avg_gain, avg_loss)
        # Calculate the RSI
        # Calculate the Relative Strength (RS)
        rs = avg_gain / avg_loss # 일정기간동안의 상승평균 / 하락평균
        rsi = 1.0 - (1.0 / (1.0 + rs)) # rs 값과 rs index와 비례관계
        upbit_df['RSI_'+str(p)] = rsi # rsi 컬럼 생성

    ### 일목균형표 ###
    # 전환선(기간 : 9일)
    nine_high = upbit_df['고가'].rolling(window=9).max()
    nine_low = upbit_df['저가'].rolling(window=9).min()
    upbit_df['전환선'] = (nine_high + nine_low)/2 # 전환선

    # 기준선(기간 : 26일)
    p_ts_high =  upbit_df['고가'].rolling(window=26).max()
    p_ts_low =  upbit_df['저가'].rolling(window=26).min()
    upbit_df['기준선'] = (p_ts_high + p_ts_low)/2

    # 선행스팬 1({전환선 + 기준선}/2, 26일 선행하여 배치)
    upbit_df['선행스팬_1'] = ((upbit_df['전환선'] + upbit_df['기준선']) / 2).shift(26)

    # 선행스팬 2(52일 선행하여 배치)
    p_ft_high = upbit_df['고가'].rolling(window=52).max()
    p_ft_min = upbit_df['저가'].rolling(window=52).min()
    upbit_df['선행스팬_2'] = ((p_ft_high + p_ft_min) / 2).shift(26)

    # 후행스팬
    upbit_df['후행스팬'] = upbit_df['종가'].shift(-26)

    # 분석 기법 1 : '구름' => 선행스팬 1, 선행스팬 2의 사이!!
    # 분석 기법 2 : 전환선과 기준선의 관계 => 1. 기준선(26일, 중기) 중기적인 추세를 얘기하고 상승, 하락 추세를 어느정도 판별
    #                                       2. 전환선(9일, 단기) 이 기준선을 역전하는가??? => 중기 및 단기 상승, 하락 추세를 결정

    # 가격 값 전체에 대한 평균

    # df_size = upbit_df[['종가', '오픈', '고가', '저가']].shape[0] * upbit_df[['종가', '오픈', '고가', '저가']].shape[1]
    # avg_value = upbit_df[['종가', '오픈', '고가', '저가']].sum().sum() / df_size
    # dv_max_value = abs(np.max(upbit_df[['종가', '오픈', '고가', '저가']] - avg_value).max())
    #
    # # SCALING => 편차 / 편차의 최대 절대값 (산출값 <= 1 )
    # scale_df = (upbit_df[['종가', '오픈', '고가', '저가', '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬']] - avg_value) / dv_max_value
    # scale_df.columns = [x + '_SCALING' for x in scale_df.columns]

    # 차트용 데이터 100일 추출
    upbit_chart_df = upbit_df[upbit_df['등록시간'] >= c_bd]
    print(id(upbit_df), id(upbit_chart_df))
    # 전체 대상, 100일 대상 스케일링

    # for df_nm in ['upbit_df', 'upbit_chart_df']:
    # for df_nm in ['test_df']:
    def scaling(p_data):
        scale_col = ['종가', '오픈', '고가', '저가', '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬']
        ma_scaler = MaxAbsScaler()
        avg_value = np.nanmean(p_data[scale_col].values)
        ma_scaler.fit(np.array(p_data[scale_col] - avg_value).flatten().reshape(-1,1))
        scale_data = ma_scaler.transform(np.array(p_data[scale_col] - avg_value))
        scale_df = pd.DataFrame(data=scale_data, columns=scale_col, index=p_data.index)
        scale_df.columns = [x + '_SCALING' for x in scale_df.columns]

        # 스케일링 데이터 Merge
        print('### Merge 전 데이터 프레임 정보들 ###')
        print(len(p_data), len(p_data.columns))
        print(len(scale_df), len(scale_df.columns))
        print('####################################')
        p_data = p_data.merge(scale_df, right_index=True, left_index=True, how='left')
        print(id(p_data))
        print('Merge 후')
        print(p_data.columns, len(p_data), len(p_data.columns))
        print('스케일링 MERGE 완료')

        print('최종')
        # print(vars())
        return p_data
    upbit_df = scaling(p_data=upbit_df)
    upbit_chart_df = scaling(p_data=upbit_chart_df)
    # 컬럼 재배치 및 수정
    # upbit_chart_df = upbit_chart_df[
    #     ['등록시간', '저가', '오픈', '종가', '고가', '거래량', '저가_SCALING', '오픈_SCALING', '종가_SCALING', '고가_SCALING', 'RSI_3',
    #      'RSI_7', 'RSI_14', '전환선_SCALING', '기준선_SCALING', '선행스팬_1_SCALING', '선행스팬_2_SCALING', '후행스팬_SCALING']]
    upbit_chart_df = upbit_chart_df[['등록시간', '저가', '오픈', '종가', '고가', '거래량',
                                     '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬',
                                     'RSI_3', 'RSI_7', 'RSI_14']]


    # 출처 컬럼 생성
    upbit_chart_df['출처'] = 'upbit'

    # 데이터 생성 및 적재
    today_dt = datetime.datetime.today().strftime(format='%Y%m%d')  # 오늘 날짜(적재 날짜)
    upload_fnm = 'bitcoin_info.csv'  # 적재 파일명
    f_list = os.path.splitext(p_file_path + 'static\\coin_data\\' + upload_fnm)
    upload_fnm = f_list[0] + '_' + today_dt + f_list[1]

    # 딕셔너리 데이터 프레임에 적재
    if os.path.isfile(upload_fnm) == False:
        print('비트코인 업비트 차트 정보 파일 미존재 => 파일생성 및 적재')
        upbit_chart_df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('비트코인 업비트 차트 정보 파일 존재 => 적재')
        upbit_chart_df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')


    print('적재완료')
    print('#' * 80)

    ### 모델링 데이터 준비(학습, 검증) 및 변수 추출
    # 변수 재정의 => value, ADJ종가, 후행스팬, 후행스팬_SCALING 컬럼 제거
    upbit_df.drop(columns=['value','ADJ_종가','후행스팬_SCALING', '후행스팬'], inplace=True)

    # 학습 및 검증 데이터 셋 Split (랜덤 추출, 비율 8:2)
    upbit_df = upbit_df[:-1] # 오늘 날짜 제거
    upbit_df['target'] = upbit_df['종가'].shift(-1)  # 타겟 다음날 종가 컬럼 생성
    upbit_df = upbit_df.dropna()  # 결측치 제거


    # 학습데이터 및 검증데이터 나누기 : TRAIN & TEST 데이터 Split(TRAIN:TEST = 8:2)
    split_no = len(upbit_df) // 5
    upbit_tr_df = upbit_df[:-split_no]  # TRAIN SET
    upbit_test_df = upbit_df[-split_no:]  # TEST SET

    ## 예측모델 => 컨셉 전날의 데이터로 다음 날의 종가 예측
    # pycaret 준비단계
    setup_rg = setup(data=upbit_tr_df, target='target', ignore_features=['등록시간'], silent=True)

    # compare_models : 모델 비교(sort = 비교 기준 지표, n_selecd = return 으로 상위 추출 모델리스트 수)
    best_models = compare_models(n_select=3, sort='MSE')
    # 모델 생성 : 특정모델 생성 => create_model 함수
    # exclude = None => 2.1버전부터 blacklist
    # include = None => 2.1버전부터 whitelist
    # fold = 10 => 표시할 모델 수(K-fold 임 => 데이터 셋을 5번 바꿔서 검증)
    # round = 4 => 표시할 소수점 자리수
    # sort = 'Accuracy' => 순위 정렬 기준
    # n_select = 1 # 최종 선택될 모델수
    # budget_time = 0 => 0이 아닌 값을 넣은 경우
    # turbo = True => False로 설정하면 runtime이 긴 모델도 평가대상에 포함
    # verbose = True => False로 설정하면 순위표가 출력되지 않음

    # 모델별 결과지표 데이터 프레임 추출
    # Classification(분류모델) 결과지표 : Accuracy, AUC, Recall, Precision, F1, Kappa, MCC
    # Regression(예측모델) 결과지표 : MAE, MSE, RMSE, R2, RMSLE, MAPE
    # 기본적으로 테이블은 분류일 경우 정확도, 회귀일 경우 R2로 정렬됨
    # 콘솔창에 '엔터키' 쳐야지 데이터 프레임으로 가져올 수 있음 => ipython에서는 확인가능
    models_idx_df = pull()
    models_idx_df = models_idx_df.reset_index().rename(columns={'index':'model_nm'})
    print('### 모델 결과 지표기준(R2)에 따른 모델 순위 ###','\n',models_idx_df)

    # 모델 튜닝
    # tune_model 함수의 옵션
    # estimator
    # fold
    # n_iter
    # custom_grid
    # optimize
    # custom_scorer
    # choose_better
    # verbose = True
    # tuned_models_idx_df = pull()

    # ensemble_model(앙상블 모델) => 각 모델별 Bagging(결합), Boosting(보완)
    # bagged_models = ensemble_model(best_models[0], method='Bagging')
    # bagged_models_idx_df = pull()
    # models_idx_df

    # blend_model => 모델간 결합
    # blend_model()
    # blended = blend_models(estimator_list=best_models, fold=2)
    # blended_idx_df = pull()

    # 최종 모델 선정 및 검증
    final_model = finalize_model(best_models[0])
    print('최종 선정 TOP 모델 :', final_model)
    upbit_test_df = predict_model(final_model, data=upbit_test_df) # 예측값 컬럼명 : 'Label'
    upbit_test_df.rename(columns={'Label' : '전통모델_pred'}, inplace=True) # 예측값 컬럼명 변경

    # 테스트 데이터에 대한 결과 지표 산출
    trd_mae = mean_absolute_error(y_pred=upbit_test_df['전통모델_pred'], y_true=upbit_test_df['target'])
    trd_mse = mean_squared_error(y_pred=upbit_test_df['전통모델_pred'], y_true=upbit_test_df['target'])

    # 모델 및 결과지표 딕셔너리 선언
    model_result_dict = dict()
    for i in ['Model', 'MAE', 'MSE', 'Accuracy']:
        model_result_dict[i] = list()
    # 전통 모델 결좌 지표 담기
    model_result_dict['Model'].append(models_idx_df['Model'].values[0])
    model_result_dict['MAE'].append(trd_mae)
    model_result_dict['MSE'].append(trd_mse)

    # 실제값 : UP, DOWN (올랐다, 내렸다) 분류 문제까지 정의
    upbit_test_df['target_updown'] = upbit_test_df['target'] - upbit_test_df['종가']
    upbit_test_df['target_updown'] = upbit_test_df['target_updown'].apply(lambda x : 'UP' if x > 0 else 'STAY_OR_DOWN') # 실제값 : 다음날 종가 'UP', 'STAY_OR_DOWN'

    upbit_test_df['전통모델_오차값'] = upbit_test_df['전통모델_pred'] - upbit_test_df['종가']
    upbit_test_df['전통모델_등락여부'] = upbit_test_df['전통모델_오차값'].apply(lambda x : 'UP' if x > 0 else 'STAY_OR_DOWN')
    upbit_test_df['전통모델_정답여부'] = [1 if pred == tgt else 0 for pred, tgt in zip(upbit_test_df['전통모델_등락여부'], upbit_test_df['target_updown'])]

    model_acc = upbit_test_df['전통모델_정답여부'].sum()/len(upbit_test_df)
    model_result_dict['Accuracy'].append(model_acc)
    print('등락여부 정답률 :', round(model_acc, 2)*100,'%')

    # 모델 저장
    save_model(final_model, file_csv_path+'model_'+today_dt)
    print('예측 모델 저장 완료')

    ### 2. 분류 모델(인공신경망) => DDN, LSTM Classification 모델 (분류 : 상승, 하락)
    ### 2. 인공신경망 회귀(Regression) 모델 => 다음날 '종가' 예측

    # 학습 대상 컬럼만 추출(마이너스 값이 포함된 컬럼도 제외)
    d_col = ['등록시간', '출처', 'target']
    for x in upbit_tr_df.columns:
        print(x)
        if x not in d_col:
            temp_df = upbit_tr_df[x].map(lambda x : 1 if x < 0 else 0)
            if temp_df.sum() > 0:
                print(x, '데이터에 음수가 포함')
                d_col.append(x)

    t_col = list(upbit_tr_df.columns)
    del_list = list(set(t_col).intersection(d_col))
    for x in del_list:
        t_col.remove(x)

    # 모델링을 위한 학습데이터 Numpy 형변환
    tr_array = np.array(upbit_tr_df[t_col]) # INPUT DATA
    tg_array = np.array(upbit_tr_df['target']) # TARGET DATA
    test_array = np.array(upbit_test_df[t_col]) # TEST DATA
    test_tg_array = np.array(upbit_test_df['target'])  # TEST DATA


    # 학습데이터 확인
    print('SHAPE 확인 : ', tr_array.shape, tg_array.shape, test_array.shape)

    # 모델 생성(DNN)
    dnn_model = models.Sequential()
    # ReLU 의 역효과참고 : 배니싱 그래디언트로부터 자유로워진 ReLU는 backpropagation 과정에서 비용함수를 계산하는 계수를 온전히 전달하지만,
    # input값에 음수가 포함이 된다면 기울기가 0이 되버리므로, 미분을 하면 backpropagation 과정 중간에 꺼져버리는 상황이 발생한다.
    # Chain rule로 미분을 하기 때문에 음수가 한번 나오면 뒤에서도 다 꺼진다.
    # 따라서 input 데이터에서 음수값이 포함되지 않도록 0~1사이의 값으로 정규화 시키는 과정을 거치는 것이 좋다.
    dnn_model.add(layers.Dense(256, activation='relu', input_shape=(tr_array.shape[1],)))
    dnn_model.add(layers.Dense(128, activation='relu'))
    dnn_model.add(layers.Dense(64, activation='relu'))
    dnn_model.add(layers.Dense(32, activation='relu'))
    dnn_model.add(layers.Dense(16, activation='relu'))
    dnn_model.add(layers.Dense(1, activation='linear'))

    # 모델 학습과정 설정
    # 활성화 함수 : linear, sigmoid, softmax
    # 손실 함수 : mse, binary_crossentropy(이진 분류), categorical_crossentropy(다중 분류)
    # 옵티마이저(최적화 알고리즘) : gradient desent methoid, SGD, rmsprop, adam, adagrad
    dnn_model.compile(loss='mse', optimizer='rmsprop', metrics=['mae','mse'])

    # 모델 학습
    hist = dnn_model.fit(tr_array, tg_array, epochs=50, verbose=2)

    # 스코어링
    dnn_eval = dnn_model.evaluate(test_array, test_tg_array)
    model_result_dict['Model'].append('DNN') # 모델명 저장
    model_result_dict['MAE'].append(dnn_eval[1]) # MAE 저장
    model_result_dict['MSE'].append(dnn_eval[2]) # MSE 저장

    # 테스트 셋에 대한 예측값 산출
    proba = dnn_model.predict(x=test_array)
    upbit_test_df['DNN_pred'] = proba

    # 예측값과 실제값과 비교
    upbit_test_df['DNN_오차값'] = upbit_test_df['DNN_pred'] - upbit_test_df['종가'] # 예측값에 대한 오차
    upbit_test_df['DNN_등락여부'] = upbit_test_df['DNN_오차값'].apply(lambda x: 'UP' if x > 0 else 'STAY_OR_DOWN')
    upbit_test_df['DNN_정답여부'] = [1 if pred == tgt else 0 for pred, tgt in zip(upbit_test_df['DNN_등락여부'], upbit_test_df['target_updown'])]

    # 정확도
    dnn_acc = upbit_test_df['DNN_정답여부'].sum()/len(upbit_test_df)
    model_result_dict['Accuracy'].append(dnn_acc)
    print('DNN 모델 정확도 :', dnn_acc)


    ### 3. LSTM 모델 : 5일전 데이터 부터 현재의 데이터로 다음날 '종가' 예측

    ## 학습데이터 구축(Window size : 5)
    # INPUT(TRAIN, TEST) 데이터 생성 함수
    def create_input_data(p_window_size, p_feature, p_scaling):
        print('################ INPUT DATA 생성 시작 ################')
        # 1. Window 사이즈 설정
        w_size = p_window_size
        print('Window 사이즈 :', w_size)
        # Features 선택 (1 : target에 해당 하는 '종가', 2 : 변수중 음수값을 가진 컬럼을 제외한 모든 컬럼)
        if p_feature == 1:
            t_col = ['종가']
            print('FEATURE LIST :',t_col)
        else:
            # 학습 대상 컬럼만 추출(마이너스 값이 포함된 컬럼도 제외)
            d_col = ['등록시간', '출처', 'target']
            for x in upbit_tr_df.columns:
                print(x)
                if x not in d_col:
                    temp_df = upbit_tr_df[x].map(lambda x: 1 if x < 0 else 0)
                    if temp_df.sum() > 0:
                        print(x, '데이터에 음수가 포함')
                        d_col.append(x)

            t_col = list(upbit_tr_df.columns)
            del_list = list(set(t_col).intersection(d_col))
            for x in del_list:
                t_col.remove(x)
            print('FEATURE LIST :', t_col)

        # 변수 SCALING 여부(SCALING 방식 : MINMAXSCALING => 0 ~ 1의 값)
        # 타겟인 변수 : '종가'만 채택 되었을 때만 SCALING 적용가능
        if p_scaling == 1:
            # MINMAXSCALING
            mm_scaler = MinMaxScaler()
            upbit_df['종가_SCALING_INPUT'] = mm_scaler.fit_transform(np.array(upbit_df['종가']).reshape(-1, 1)).flatten()
            t_col = ['종가_SCALING_INPUT']
            print('스케일링 적용')
        else : print('스케일링 미적용')

        # INPUT 데이터 생성 FOR문
        cnt = 0 # for문 순번 count
        if len(t_col) == 1: # t_col은 학습대상의 변수 리스트
            print('Features list :', t_col)
            for i in range(0,len(upbit_df)-w_size):
                cnt += 1
            # temp_list = upbit_df[t_col].iloc[i:i+w_size+1].values.tolist()
                temp_arr = upbit_df[t_col].iloc[i:i+w_size+1].values.reshape(-1,w_size+1,len(t_col))
                if cnt == 1:
                    all_arr = copy.deepcopy(temp_arr)
                else:
                    all_arr = np.append(all_arr, temp_arr, axis=0)
                # print('순번 :',cnt,'전체 INPUT DATA SHAPE:',all_arr.shape, 'TEMP INPUT DATA SHAPE :',temp_arr.shape)

        else: # 학습대상 변수가 여러개일때
            print('Features', t_col)
            for i in range(0, len(upbit_df) - w_size):
                cnt += 1
                temp_arr = upbit_df[t_col].iloc[i:i+w_size+1].values.reshape(-1,w_size+1,len(t_col))
                if cnt == 1:
                    all_arr = copy.deepcopy(temp_arr)
                else:
                    all_arr = np.append(all_arr, temp_arr, axis=0)
                # print('순번 :',cnt,'전체 INPUT DATA SHAPE:',all_arr.shape, 'TEMP INPUT DATA SHAPE :',temp_arr.shape)

        print('전체 INPUT DATA SHAPE:',all_arr.shape, 'TEMP INPUT DATA SHAPE :',temp_arr.shape)

        # TRAIN & TEST INPUT DATA
        tr_arr = all_arr[:-split_no]  # TRAIN INPUT DATA
        tt_arr = all_arr[-split_no:]  # TEST INPUT DATA

        # TRAIN & TEST TARGET DATA
        tg_arr = np.array(upbit_df['target'][w_size:])
        tg_arr = np.reshape(tg_arr, (tg_arr.shape[0],1))
        tr_tg_arr = tg_arr[:-split_no]  # TRAIN TARGET DATA
        tt_tg_arr = tg_arr[-split_no:]  # TEST TARGET DATA

        print('TRAIN DATA shape(INPUT, TARGET) :', tr_arr.shape, tr_tg_arr.shape)
        print('TEST DATA shape(INPUT, TARGET) :', tt_arr.shape, tt_tg_arr.shape)
        print('################ INPUT DATA 생성 완료 ################')

        return tr_arr, tr_tg_arr, tt_arr, tt_tg_arr
    # 학습데이터 생성 함수 실행
    tr_arr, tr_tg_arr, tt_arr, tt_tg_arr = create_input_data(p_window_size=5, p_feature=1, p_scaling=1)

    # 모델 생성(LSTM)
    lstm_model = models.Sequential()
    lstm_model.add(layers.LSTM(64, input_shape=(tr_arr.shape[1], tr_arr.shape[2]), activation='relu'))
    lstm_model.add(layers.Dense(32, activation='relu'))
    lstm_model.add(layers.Dense(16, activation='relu'))
    lstm_model.add(layers.Dense(1, activation='linear'))

    # loss = Huber
    lstm_model.compile(loss='mse', optimizer='rmsprop', metrics=['mae','mse'])
    print(lstm_model.summary())

    # 모델 학습
    hist = lstm_model.fit(tr_arr, tr_tg_arr, epochs=50, verbose=2)

    # 결과 지표 산출
    lstm_eval = lstm_model.evaluate(tt_arr, tt_tg_arr) # LOSS, MAE, MSE 결과
    model_result_dict['Model'].append('LSTM')  # 모델명 저장
    model_result_dict['MAE'].append(lstm_eval[1])  # MAE 저장
    model_result_dict['MSE'].append(lstm_eval[2])  # MSE 저장

    # 테스트 셋에 대한 예측값 산출
    proba = lstm_model.predict(x=tt_arr)
    upbit_test_df['LSTM_pred'] = proba

    # 예측값과 실제값과 비교
    upbit_test_df['LSTM_오차값'] = upbit_test_df['LSTM_pred'] - upbit_test_df['종가']
    upbit_test_df['LSTM_등락여부'] = upbit_test_df['LSTM_오차값'].apply(lambda x: 'UP' if x > 0 else 'STAY_OR_DOWN')
    upbit_test_df['LSTM_정답여부'] = [1 if pred == tgt else 0 for pred, tgt in zip(upbit_test_df['LSTM_등락여부'], upbit_test_df['target_updown'])]

    # 정확도
    lstm_acc = upbit_test_df['LSTM_정답여부'].sum()/len(upbit_test_df)
    model_result_dict['Accuracy'].append(lstm_acc)
    # DNN - loss: 1580319737320.3694 - mean_absolute_error: 668930.7644 - mean_squared_error: 1580319737320.3694
    print('LSTM 모델 정확도 :', lstm_acc)

    # 전체 모델 비교
    print('정확도 => 전통모델, DNN, LSTM :', model_acc, dnn_acc, lstm_acc)

    ### 업비트 스코어 데이터 및 성능 적재 ###
    # 스코어 성능 적재
    model_result_df = pd.DataFrame(model_result_dict)
    model_result_df['출처'] = 'upbit'
    model_result_df.to_csv(file_csv_path+'model_idx_result_'+today_dt+'.csv', index=False, mode='w', encoding='cp949')

    # 스코어 데이터 적재
    upbit_test_df['출처'] = 'upbit'
    upbit_test_df.to_csv(file_csv_path + 'score_data_' + today_dt + '.csv', index=False, mode='w', encoding='cp949')
    print('스코어 결과 지표 적재 완료')

    return
# 업비트 기준 : 시가, 종가, 고가, 저가 (시간 단위 기준 결정)
interval = 'day'
upbit_api_modeling(p_file_path=file_path, p_interval=interval)

print('전체 크롤링 완료')