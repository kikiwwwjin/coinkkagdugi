#######################################################################################################################
######################################################### 코인사전 #####################################################
#######################################################################################################################


# 크롤링 데이터 리스트
def coin_noun_all():
    f_list = ['coindesk', 'investing', 'naver', 'decenter']

    # 코인명 리스트
    coin_nm_list = ['암호화폐', '가상화폐', '비트코인', 'BTC', '메이저','알트코인', '라이트코인', '도지코인', '폴카닷', '디카르고', '에이다'
                    , '마로', '페이코인', '썸씽', '이더리움 클래식', '이더리움', '비체인', '비트코인골드', '오브스', '모스코인'
                    , '펀디엑스', '카르다노', '리플', 'XRP', '이오스', 'EOS', '엠블', '골렘', '엘프', '스톰엑스', '세럼', '트론', '비트토렌트', '가스'
                    , '온톨로지가스', '던프로토콜', '스트라이크', '스텔라루멘', '스트라티스', '코모도', '솔라나']

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
                   , '바이낸스', '골드만삭스', 'JP모건', '월가', '월 가', '증권거래위원회', '비트코인 상장지수펀드', '스테이킹', '디파이']

    # 비트코인 관련 인물 단어 리스트
    bit_men_list = ['은성수', '홍남기', '일론 머스크', '일론'
                    ,'제롬 파웰', '제롬 파월', '연준 의장', '미연준 의장', '연방준비제도 의장'
                    ,'재닛 옐런', '옐런', '미국 재무부 장관','미 재무장관'
                    ,'워런'
                    ,'게리 겐슬러', '겐슬러', '미국 증권거래위원장', '미 증권거래위원장'
                    ,'저스틴 선', '비탈릭 부테린', '찰리 리', '나발 라비칸트'
                    ,'창펑자오', '창펑 자오','바이낸스 대표이사'
                    ,'로저 버','닉 재보'
                    ,'캐시 우드', '돈나무 언니'
                    ,'잭 도시', '트위터 CEO'
                    ]

    # 통폐합(동의어) 단어 딕셔너리
    csd_dict = {
        # 코인
        '카르다노' : ['에이다'],
        '비트코인' : ['암호화폐', '가상화폐', 'BTC'],
        '이오스' : ['EOS'],
        '리플' : ['XRP'],

        # 인물
        '제롬 파월' : ['제롬 파웰', '연준 의장', '미연준 의장', '연방준비제도 의장'],
        '재닛 옐런' : ['미국 재무부 장관', '미 재무장관', '옐런'],
        '게리 겐슬러' : ['겐슬러', '미국 증권거래위원장', '미 증권거래위원장'],
        '일론 머스크' : ['일론'],
        '창펑 자오' : ['창펑 자오','바이낸스 대표이사'],
        '캐시 우드' : ['돈나무 언니'],
        '잭 도시' : ['트위터 CEO'],
        '월가' : ['월 가'],
        '디지털 화폐' : ['디지털화폐'],
        '디지털 원화' : ['디지털원화'],
        '디지털 위안화' : ['디지털위안화'],
        '디지털 달러' : ['디지털달러'],
        '비트코인 ETF' : ['ETF'],
        '환경파괴' : ['환경 파괴', '환경오염', '환경 오염'],
    }
    print('사전 등록 완료')
    return f_list, coin_nm_list, coin_jud_dict, prd_nm_list, prd_jud_dict, fin_nm_list, bit_men_list, csd_dict

