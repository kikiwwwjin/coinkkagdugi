# 패키지 임포트
import pandas as pd
from scipy.stats import shapiro, normaltest, kstest, spearmanr, pearsonr
import matplotlib.pyplot as plt
import seaborn as sns

# 실습 데이터 불러오기
df = pd.read_csv('C:\\Users\\wai\\Desktop\\프로젝트\\교육자료\\교육데이터\\kaggle\\test.csv')
print(df)

### 실습 1) 정규성 검정
# 검정 대상 컬럼 : 'Vintage'
print(df.loc[:,'Vintage'])

# 정규 분로를 따르는지 검정
# 가정 : 독립성, 등분산성

# 1. Shapiro-Wilks test(표본수가 2000 미만인 데이터셋에 적합한 정규성 검정)
shapiro(df.loc[:,'Vintage'])


### 실습 2) 상관계수 검정
# Pearson, Spearman 상관계수는 -1 ~ +1 범위의 값, Pearson 상관 계수가 +1이 되도록 하기 위해 한 변수가 증가하면 다른 변수가 일정한 양만큼 증가합니다.
# => 이 관계는 완전한 선을 형성합니다. 이 경우 Spearman 상관 계수도 +1 입니다.

var_tgt = 'Age'
inp_var_list = ['Region_Code', 'Annual_Premium', 'Policy_Sales_Channel', 'Vintage']
# spearmanr().correlation

# for 문으로 독립 변수 가져오기
for var in inp_var_list:
    print('#'*40)
    print('독립변수명 :',var)
    var ='Policy_Sales_Channel'
    sprmn_cor = spearmanr(df[var], df[var_tgt])
    prsn_cor = pearsonr(df[var], df[var_tgt])
    print('피어슨 상관계수 :', prsn_cor, ', 스피어만 상관계수', sprmn_cor)

    # 1000건 샘플 plot 그래프
    sample_df = df[[var, var_tgt]].sample(n=10000)
    sns.pairplot(sample_df, kind='reg', height=4)

#  -1.0과 -0.7 사이이면, 강한 음적 선형관계
#  -0.7과 -0.3 사이이면, 뚜렷한 음적 선형관계
#  -0.3과 -0.1 사이이면, 약한 음적 선형관계
#  -0.1과 +0.1 사이이면, 거의 무시될 수 있는 선형관계
#  +0.1과 +0.3 사이이면, 약한 양적 선형관계
#  +0.3과 +0.7 사이이면, 뚜렷한 양적 선형관계
#  +0.7과 +1.0 사이이면, 강한 양적 선형관계