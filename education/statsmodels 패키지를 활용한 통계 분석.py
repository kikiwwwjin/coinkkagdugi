# 패키지 임포트
import pandas as pd
import numpy as np
from scipy.stats import shapiro, normaltest, kstest, spearmanr, pearsonr, gaussian_kde
from statsmodels.stats.anova import anova_lm
import matplotlib.pyplot as plt
import seaborn as sns

# 실습 데이터 불러오기
df = pd.read_csv('C:\\Users\\wai\\Desktop\\프로젝트\\교육자료\\교육데이터\\kaggle\\test.csv')
df = pd.read_csv('D:\\kaggle\\aug_train.csv') # 학습 데이터
test_df = pd.read_csv('D:\\kaggle\\aug_test.csv') # 테스트 데이터
print('학습데이터\n', df, '\n 테스트 데이터\n', test_df)

### 실습 1) 정규성 검정
# 참고문헌 : https://alex-blog.tistory.com/entry/t-test-ANOVA-%EC%89%BD%EA%B2%8C%EC%89%BD%EA%B2%8C-%EA%B8%B0%EC%96%B5%ED%95%98%EC%9E%90
from statsmodels.stats.diagnostic import kstest_normal
from statsmodels.stats.stattools import omni_normtest, jarque_bera

# 검정 대상 변수 : 'Vintage'
print('검정 대상 변수 \n', df.loc[:,'Vintage'])
# 실습 1-1) 콜모고로프-스미르노프 검정(Kolmogorov-Smirnov test)
print('콜모고로프-스미르노프 검정 :', kstest_normal(df.loc[:,'Vintage']))
# 실습 1-2) 옴니버스 검정(Omnibus Normality test)
print('옴니버스 검정 :', omni_normtest(df.loc[:,'Vintage']))
# 실습 1-3) 자크-베라 검정(Jarque–Bera test)
print('자크-베라 검정 :', jarque_bera(df.loc[:,'Vintage']))

### 실습 2) 등분산성 검정
# 사이파이 밖에없네


# 정규 분로를 따르는지 검정
# 가정 : 독립성, 등분산성

### 실습 3) t-검정
# 사이파이 밖에없네


from statsmodels.stats import anova # 분산분석 => 세집단 이상의 평균의 차이가 유의미한가
### 실습 2) 상관계수 검정
# Pearson, Spearman 상관계수는 -1 ~ +1 범위의 값, Pearson 상관 계수가 +1이 되도록 하기 위해 한 변수가 증가하면 다른 변수가 일정한 양만큼 증가합니다.
# => 이 관계는 완전한 선을 형성합니다. 이 경우 Spearman 상관 계수도 +1 입니다.

# 패키지 임포트
from scipy.stats import spearmanr, pearsonr
# 종속 및 독립변수 선정
var_tgt = 'Age' # 종속변수
inp_var_list = ['Region_Code', 'Annual_Premium', 'Policy_Sales_Channel', 'Vintage'] # 독립변수 리스트
# spearmanr().correlation

# for 문으로 종속변수('Age')에 대한 독립변수 리스트 상관 관계 검정
for var in inp_var_list:
    print('#'*40)
    print('독립변수명 :',var)
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

# 실습 3) 커널 밀도 추정
# 히스토그램과 같이 비모수 추정일 경우 불연속이라는 단점이 있지만, 부드러운(Smooth) 형태의 밀도함수를 추정하기 위해 사각형 kernel 대신 사용합니다.
# 참고문헌 : https://blog.naver.com/cjh226/221362816850
kernel = gaussian_kde(df['Age'], bw_method='silverman')
age_min = df['Age'].min()
age_max = df['Age'].max()
X = np.arange(age_min, age_max, 1)
K = kernel(X)
# RAW 데이터의 확률밀도 히스토그램
plt.hist(df['Age'], label='Original_Prob_Density', density=True)
# 가우시안 커널 밀도 추정
plt.plot(X, K, label='gaussian_kde')
plt.legend()
plt.show()

# 실습 4) 회귀 분석(Linear Regression)
# 참고문헌 : https://brunch.co.kr/@gimmesilver/38, https://ysyblog.tistory.com/119, https://riverzayden.tistory.com/10
# 4-1) 선형 모형(Linear Model)
import statsmodels.api as sm

model = sm.OLS.from_formula('Age ~ ' + '+'.join(inp_var_list), df).fit()
print(model.summary()) # 모델에 대한 정보 출력
# 유의미한 변수 확인 => P>|t| 값이 0.05보다 작으면 유의미한 변수
p_vars = model.pvalues.index[model.pvalues <= 0.05]
p_vars = list(p_vars[1:]) # 첫번째 변수는 Intercept(절편)으로 제외

# 유의미한 변수로 재학습
model = sm.OLS.from_formula('Age ~ ' + '+'.join(p_vars), df).fit()
pred_df = model.predict(test_df) # 종속변수(나이) 예측값
test_df['Age_Pred'] = pred_df
test_df = test_df.astype({'Age_Pred' : int}) # 정수 값으로 변환(소수점 제거)
print('결과 데이터 :\n',test_df)



# 실습 4) 일반화 선형 모델(Generalized Linear Model, GLM)
from statsmodels.genmod.generalized_linear_model import GLM # 종속변수가 정규분포하지 않은 경우를 포함하는 선형모형의 확장

# 일반화 선형 모델의 대표적인 로지스틱 회귀 모델을 구현해 보겠습니다.





