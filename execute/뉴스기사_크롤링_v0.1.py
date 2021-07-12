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
import pyautogui

# 크롤링 관련 패키지
from bs4 import BeautifulSoup
import requests
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import webbrowser

# 업비트 및 바이낸스 관련 패키지
import ccxt
import pyupbit
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
file_path = 'C:\\Users\\wai\\Desktop\\프로젝트\\암호화폐\\'
# file_path = 'D:\\암호화폐\\'



#####################################################################
# 1. investing.com(암호화폐 뉴스 url) 크롤링 함수
# bs4, request 함수로는 BAN 처리 당함 => 셀레니움만 가능

def investing_crawling(p_file_path):
    main_url = 'https://kr.investing.com/news/cryptocurrency-news/'
    driver = webdriver.Chrome(file_path + 'chromedriver.exe')
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
    # 배치 주기(일별) => 오늘 날짜인 것만 크롤링, 사이트는 최신순으로 자동정렬
    dt_list = soup.find('div', {'class': 'largeTitle'}).find_all('span', {'class': 'date'})
    connect_cnt = sum(list(map(lambda x: 1 if str(x).find('전') != -1 else 0, dt_list)))

    # 오늘 날짜로 등록된 기사가 첫페이지의 전체이면 다음페이지도 오늘 날짜 기사를 확인해야함
    page_no = 1  # 크롤링 할 페이지 수크롤링 페이지 번호
    while connect_cnt == len(dt_list):
        # 특정 페이지의 오늘 날짜 기사 건수 확인
        page_no += 1
        print('페이지 번호 :', page_no)
        driver.get(main_url + str(page_no))  # 다음페이지 url 접속
        dt_list = soup.find('div', {'class': 'largeTitle'}).find_all('span', {'class': 'date'})
        connect_cnt = sum(list(map(lambda x: 1 if str(x).find('전') != -1 else 0, dt_list)))
        print(page_no, '페이지 전체 건수 :', len(dt_list), ', 오늘 날짜 기사 건수 :', connect_cnt)

    # 크롤링 코드
    today_dt = datetime.datetime.today().strftime(format='%Y%m%d')  # 오늘 날짜(적재 날짜)
    upload_fnm = 'investing_crawling.csv'  # 적재 파일명
    f_list = os.path.splitext(file_path + upload_fnm)
    upload_fnm = f_list[0] + '_' + today_dt + f_list[1]
    for no in range(1, page_no + 1):  # 페이지 번호 기준
        # 딕셔너리 선언
        news_dict = dict()
        news_dict['title'] = list()  # 기사 제목
        news_dict['reg_date'] = list()  # 등록일자
        news_dict['content'] = list()  # 기사 내용

        print('#' * 80)
        print('크롤링 페이지 번호 :', no)
        driver.get(main_url + str(no))  # 특정페이지 url 접속
        time.sleep(2.5)

        # 특정 페이지에 있는 각 기사 정보 추출
        news_list = soup.find('div', {'class': 'largeTitle'}).find_all('div', {'class': 'textDiv'})

        # 마지막 페이지에서 오늘 날짜 기사만 크롤링
        if page_no == no: # page_no => 마지막 페이지, no => 현재 페이지
            news_list = news_list[:connect_cnt] # 마지막 페이지의 오늘 날짜인 기사만 추출(최신순, 건수로 적용ㄴ)

        print('크롤링 기사 건수 :', len(news_list))
        check_no = 0
        for news in news_list:
            check_no += 1
            print('기사 순번 ===>',check_no,'/',len(news_list))
            # 출처 사이트 => 'MK 부터' => 매일 경제 홈페이지 url로 직접 접속
            news_url = news.find('a',{'class':'title'}).get('href')
            ref_site = news.find('span',{'class':'articleDetails'}).find('span').text
            if ref_site == '부터 MK':
                print('출처 ==> 매일경제')
                driver.get(news_url)
            elif ref_site == '부터 Investing.com Studios':
                print('파트너사 뉴스 => 제외')
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
            title = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', title)
            title = re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff]', '', title)
            news_dict['title'].append(title)
            # 날짜 포맷 : 7 시간 전 (0000년 00월 00일 01:39) => YYYY-mm-dd %HH:%MM:%SS(년-월-일 시-분-초)
            reg = soup.find('div', {'class': 'contentSectionDetails'}).find('span').get_text()
            reg = reg.split('(')[1].replace(')', '')
            reg = datetime.datetime.strptime(reg, '%Y년 %m월 %d일 %H:%M').strftime('%Y-%m-%d %H:%M:%S')
            news_dict['reg_date'].append(reg)
            # 기사 내용
            content_info = soup.find('div', {'class': 'articlePage'}).find_all('p')
            content_list = list()
            for content in content_info:
                ctt = re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff]', '', content.get_text())
                ctt = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', ctt)
                print('기사내용 :', ctt)
                content_list.append(ctt)
            news_dict['content'].append(content_list)
            print('기사 제목 :', title, '=> 크롤링 성공')

        # 딕셔너리 데이터 프레임에 적재
        df = pd.DataFrame(news_dict)
        if os.path.isfile(upload_fnm) == False:
            print('인베스팅 크롤링 파일 미존재 => 파일생성 및 적재')
            df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
        else:
            print('인베스팅 크롤링 파일 존재 => 적재')
            df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')
        print('적재완료')
        print('#' * 80)

    print('investing.com 전체 기사 크롤링 완료')
    return
investing_crawling(p_file_path=file_path)

#####################################################################
# 2. 네이버 뉴스 검색 "비트코인" 언론사 및 최신순(오늘날짜만)

def naver_crawling(p_file_path, p_start_date):
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
    f_list = os.path.splitext(p_file_path + upload_fnm)
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
                        # print(news)
                        # 해당 뉴스 링크로 접속
                        link = news.find('a', {'class': 'news_tit'}).get('href')
                        article_info = requests.get(link)
                        time.sleep(0.5)
                        article_html = BeautifulSoup(article_info.text, 'html.parser')
                        # 뉴스 기사 제목
                        title = article_html.find('div', {'class': 'article_tbx'}).find('h1').get_text()
                        title = re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff]', '', title)
                        title = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', title)


                        news_dict['title'].append(title)  # 기사 제목 담기

                        # 등록날짜
                        reg = article_html.find('div', {'class': 'date'}).get_text()
                        if reg.find('|') != -1:
                            reg = reg.split('|')[0]
                        reg = reg.replace('등록', '').replace('/','-').replace(u'\xa0','').strip() # 등록일시 추출
                        news_dict['reg_date'].append(reg)

                        # 기사내용
                        content_info = article_html.find('div', {'id': 'textBody'}).text
                        content_info = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', content_info)
                        ctt_list = re.sub('[\u2000-\u9999\n\t\r\ufeff]', '', content_info).split('\n')
                        ctt_list = [x for x in ctt_list if x != '']  # 줄바꿈 생략
                        news_dict['content'].append(ctt_list)

                        # 확인용 출력
                        print(firm_nm, ', 기사 제목 :', title, ', 등록날짜 :', reg, '내용:', ctt_list)

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
# 크롤링 날짜 설정
start_date = '20210608'
naver_crawling(p_file_path=file_path, p_start_date=start_date)

########################################################################
# 3. 코인데스크 뉴스 => http://www.coindeskkorea.com/news/articleList.html?sc_day=1&sc_word=&sc_area=&view_type=sm&sc_order_by=E
# 출처 : 한겨레 기사
# 코인데이스크 크롤링 함수

def coindesk_crawling(p_file_path):
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
            title = re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff]', '', title)
            title = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', title)
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
                content = re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff]', '', p_info.text)
                content = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', content)
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
    f_list = os.path.splitext(p_file_path + upload_fnm)
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
            title = re.sub('[\u2000-\u9999\n\t\r\ufeff]', '', title)
            title = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', title)
            news_dict['title'].append(title)
            # 기사 내용
            c_list = soup.find_all('br')
            c_list = list(map(lambda x: re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0'
                                               '\xe9\xa5\x80\x9a\xf3]', '', x.text), c_list))
            c_list = [x for x in c_list if x != '']
            news_dict['content'].append(c_list)
            # 등록 일시
            reg = atc_info.find('li',{'class':'letter'}).text
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
                title = re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff\xf3]', '', title)
                title = re.sub('[\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', title)
                news_dict['title'].append(title)

                # 기사 내용
                c_list = soup.find_all('br')
                c_list = list(map(lambda x: re.sub('[\u2000-\u9999\n\t\r\xa0\ufeff\xa0\x82\xa1\xa2\xa3\xa4\x87\xb5'
                                                   '\xd6\xe0\xe9\xa5\x80\x9a\xf3]', '', x.text), c_list))
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
    f_list = os.path.splitext(file_path + upload_fnm)
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

    # 가격 값 전체에 대한 평균
    df_size = bit_df[['종가', '오픈', '고가', '저가']].shape[0] * bit_df[['종가', '오픈', '고가', '저가']].shape[1]
    avg_value = bit_df[['종가', '오픈', '고가', '저가']].sum().sum() / df_size
    dv_max_value = abs(np.max(bit_df[['종가', '오픈', '고가', '저가']] - avg_value).max())

    # SCALING => 편차 / 편차의 최대 절대값 (산출값 <= 1 )
    scale_df = (bit_df[['종가', '오픈', '고가', '저가', '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬']] - avg_value) / dv_max_value
    scale_df.columns = [x + '_SCALING' for x in scale_df.columns]

    bit_df = pd.merge(bit_df, scale_df, left_index=True, right_index=True, how='left')
    # 컬럼 재배치 및 수정
    bit_df = bit_df[
        ['등록시간', '저가', '오픈', '종가', '고가', '거래량', '저가_SCALING', '오픈_SCALING', '종가_SCALING', '고가_SCALING', 'RSI_3',
         'RSI_7', 'RSI_14', '전환선_SCALING', '기준선_SCALING', '선행스팬_1_SCALING', '선행스팬_2_SCALING', '후행스팬_SCALING']]

    # 출처 컬럼 생성
    bit_df['출처'] = 'binance'

    # 크롤링 코드
    today_dt = datetime.datetime.today().strftime(format='%Y%m%d')  # 오늘 날짜(적재 날짜)
    upload_fnm = 'bitcoin_info.csv'  # 적재 파일명
    f_list = os.path.splitext(p_file_path + upload_fnm)
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

    print('비트코인 정보 데이터 크롤링 및 적재 완료')
    return

# 기본 세팅 기간 99일 전(오늘 꺼까지 포함하면 총 100일)
bd = (datetime.datetime.today() - datetime.timedelta(days=99)).strftime('%Y/%m/%d')
td = datetime.datetime.today().strftime('%Y/%m/%d')
binance_info_crawling(p_file_path=file_path, p_start_date=bd, p_end_date=td)

print('전체 크롤링 완료')

########################################################################
# 6. 업비트 API를 활용한 데이터 수집
########################################################################
def upbit_api(p_file_path, p_interval):
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
    # 기본 세팅 기간 100일
    #     bd = (datetime.datetime.today() - datetime.timedelta(days=30)).strftime('%Y%m%d')
    #     td = datetime.datetime.today().strftime('%Y%m%d')

    upbit_df = pyupbit.get_ohlcv(ticker='KRW-BTC', interval=p_interval, count=100) # count +1
    # 컬럼명 수정
    upbit_df.columns =['오픈','고가','저가','종가','거래량','value']

    if interval == 'day':
        upbit_df['등록시간'] = list(map(lambda x: x.strftime(format='%Y%m%d'), list(upbit_df.index)))

    ### RSI 지표 산출 ###
    # bit_df_2 = bit_df.set_index(pd.DatetimeIndex(bit_df['날짜'].values))
    upbit_df.sort_index(ascending=True, inplace=True) # 인덱스(날짜 및 시간) 오름차순 정렬
    pd.to_datetime(list(upbit_df.index), format='%Y-%m-%d')
    upbit_df['ADJ_종가'] = upbit_df['종가']
    delta = upbit_df['ADJ_종가'].diff(1) # 현재날짜-전날짜 종가

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
    #


    # 가격 값 전체에 대한 평균
    df_size = upbit_df[['종가', '오픈', '고가', '저가']].shape[0] * upbit_df[['종가', '오픈', '고가', '저가']].shape[1]
    avg_value = upbit_df[['종가', '오픈', '고가', '저가']].sum().sum() / df_size
    dv_max_value = abs(np.max(upbit_df[['종가', '오픈', '고가', '저가']] - avg_value).max())

    # SCALING => 편차 / 편차의 최대 절대값 (산출값 <= 1 )
    scale_df = (upbit_df[['종가', '오픈', '고가', '저가', '전환선', '기준선', '선행스팬_1', '선행스팬_2', '후행스팬']] - avg_value) / dv_max_value
    scale_df.columns = [x + '_SCALING' for x in scale_df.columns]

    upbit_df = pd.merge(upbit_df, scale_df, left_index=True, right_index=True, how='left')
    # 컬럼 재배치 및 수정
    upbit_df = upbit_df[
        ['등록시간','저가','오픈','종가','고가','거래량','저가_SCALING','오픈_SCALING','종가_SCALING','고가_SCALING','RSI_3',
         'RSI_7', 'RSI_14','전환선_SCALING', '기준선_SCALING', '선행스팬_1_SCALING', '선행스팬_2_SCALING', '후행스팬_SCALING']]

    # 출처 컬럼 생성
    upbit_df['출처'] = 'upbit'

    # 데이터 생성 및 적재
    today_dt = datetime.datetime.today().strftime(format='%Y%m%d')  # 오늘 날짜(적재 날짜)
    upload_fnm = 'bitcoin_info.csv'  # 적재 파일명
    f_list = os.path.splitext(p_file_path + upload_fnm)
    upload_fnm = f_list[0] + '_' + today_dt + f_list[1]

    # 딕셔너리 데이터 프레임에 적재
    if os.path.isfile(upload_fnm) == False:
        print('업비트 정보 파일 미존재 => 파일생성 및 적재')
        upbit_df.to_csv(upload_fnm, index=False, mode='w', encoding='cp949')
    else:
        print('업비트 정보 파일 존재 => 적재')
        upbit_df.to_csv(upload_fnm, index=False, mode='a', header=False, encoding='cp949')
    print('적재완료')
    print('#' * 80)

# 업비트 기준 : 시가, 종가, 고가, 저가 (시간 단위 기준 결정)
interval = 'day'
upbit_api(p_file_path=file_path, p_interval=interval)







