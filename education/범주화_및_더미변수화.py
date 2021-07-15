########################################################################################################################
############################################      범주화 및 더미변수화      ##############################################
########################################################################################################################
# 더미 변수화를 시키는 이유
# 더미 변수는 기계학습에 적합한 데이터의 형태로 가공된 변수입니다.
# 학습 변수로 사용하기 위해 범주형 데이터를 수치형 데이터로만 변환을 하게 되면 서로 간의 관계성이 생성됩니다.
# 예를 들어 월요일을 1, 화요일을 2, 수요일을 3이라고 단순하게 수치형 데이터로 변환하게 되면 해당 데이터들간 1+2=3 이라는 수치적인 관계성이 존재하게 됩니다.
# 하지만 실제로는 월요일, 화요일, 수요일 간에는 그러한 수치적인 관계성은 존재하지 않습니다.
# 따라서 사실이 아닌 관계성으로 인해 잘못된 학습이 일어날 수 있으므로 서로 무관한 수 즉 더미로 만든 가변수로 변환함으로서 학습에 오류를 발생시키지 않게 할 수 있습니다.
# 요약 : 모델에 사용할 수 있는 변수는 범주형 변수가 아니고 연속형 변수여야 하는데 더미변수는 범주형 변수를 모델에 사용할 수 있는 연속형 변수스럽게 만들어주는 역할을 한다.


# 더미 변수화는 크게 2가지 방법이 있음
# pandas get_dummies vs sklearn LabelEncoder, OneHotEncoder => sklearn 패키지가 훨씬 성능이 좋음(처리 속도가 빠르다.)


# 패키지
import pandas as pd # 범주화 및 더미변수화
from sklearn.preprocessing import LabelEncoder, OneHotEncoder # 더미변수화
import numpy as np


season = pd.DataFrame({'계절' : ['봄','여름','가을','겨울']})
season_dummies = pd.get_dummies(season['계절'])
print(season_dummies)

# 리스트 객체(더미변수화 대상)
items = ['비트코인', '이더리움', '라이트코인', '폴카닷', '카르다노', '카르다노']

# 라벨링
encoder = LabelEncoder()
encoder.fit(items) # 리스트에 맞춰서 인코딩을 하겠다라는 뜻
labels = encoder.transform(items) # 인코딩 변환
print(labels) # 리스트 안에 있는 변량을 Encoding
print(encoder.classes_) # Randomize 하게 라벨링된 순서를 확인할 수 있음 (왼쪽에서부터 0~)

# 리스트 형태를 2차원 배열로 변환
ec_matrix = labels.reshape(-1,1)
print(ec_matrix, '\n', ec_matrix.shape)

# 원핫인코딩 => 더미변수화
ohe = OneHotEncoder(sparse=False)
ohe_matrix = ohe.fit_transform(ec_matrix)
print(ohe_matrix)

# 더미 2차원 행렬 => 데이터 프레임화
dummies_df = pd.DataFrame(ohe_matrix, columns=encoder.classes_)



##### 실습 ######
# 실습 데이터 불러오기
df = pd.read_csv('C:\\Users\\wai\\Desktop\\프로젝트\\교육자료\\교육데이터\\BookExample.csv')

# 실습 1) 'v1' 변수 범주화 하기
v1_all_diff = df.iloc[:,2].max() - df.iloc[:,2].min() # v1 변수의 최대값 - 최소값(전체 구간)
# v1 변수는 고객의 신용도를 나타내는 변수 입니다.
# v1 변수(신용도)를 신용등급으로 범주화 하는 작업을 해보겠습니다. (등급은 10개 등급으로 나눔)
# v1 전체구간 10등분하기(1개 구간 차이)
v1_diff = v1_all_diff/10 # 구간별 1.276


# 구간 라벨링 리스트 선언
labels = []
# 구간 개수 : 10
diff_n = 10
for x in range(1, diff_n+1):
    print(x)
    labels.append(str(x) + '등급')
print(labels) # 구간 개수에 따라 등급을 라벨링

# 데이터 프레임에 'v1_grade' 신용 등급(10개의 구간을 일정한 구간의 크기로 구분함)
# 1등급 : 최소값 <= x <= 1.276, 2등급 : 1.276 < x <= 2.552 .....
df['v1_grade'] = pd.cut(df.iloc[:,2], bins=10, labels=labels)
print(df['v1_grade'] )

# 데이터 프레임에 'v1_grade_quantile' 신용 등급(10개의 구간을 일정한 분위수로 구분함)
# 변수의 변량에 따라서 분위수를 나누는 구간이 중복가능하기 때문에 duplicates 옵션에 'drop'을 해준다.
# labels=False 옵션을 주어 낮은 구간부터 높은 구간순으로 0,1..6  +1씩 값이 증가하는 구간으로 세팅된다.
df['v1_grade_quantile'] = pd.qcut(df.iloc[:,2], q=10, duplicates='drop', labels=False) # 7개의 구간으로 나누어졌다.
# 0 등급부터 라벨링이 되기때문에 'v1_grade_quantile' 컬럼에 전체 적으로 +1을 해준다.
df['v1_grade_quantile'] = df['v1_grade_quantile'] + 1
print(df['v1_grade_quantile'])

### 실습 2) 'v31'변수(범주형 변수) 더미 변수화 하기
print(df.iloc[:,-1].unique()) # unique 확인 ['A' 'B' '0' 'C']
# 범주형 데이터는 모델의 학습 변수로 사용할 수 없다. 그래서 더미 변수화를 해주여야 사용할 수 있게 된다.
dummies_df = pd.get_dummies(df.iloc[:,-1]) # 더미 변수를 생성
result_df = pd.concat([df, dummies_df], axis=1) # 생성된 더미 변수를 원 데이터 뒤에 붙여준다.
print(result_df) # 원 데이터 뒤에 프레임 뒤에 더미 변수가 생성된 것을 확인

### 실습 3) sklearn의 LabelEncoder, OneHotEncoder 함수로 더미 변수화 하기
le = LabelEncoder()
labels = le.fit_transform(df.iloc[:,-1]) # 데이터 변량에 따른 라벨링
lb_matrix = labels.reshape(-1, 1) # 2차원 행렬로 변환
print(lb_matrix.shape)

# 원핫인코더로 더미 행렬 생성
ohe = OneHotEncoder(sparse=False)
ohe_matrix = ohe.fit_transform(lb_matrix)

# 행렬을 변수화
dummies_df_2 = pd.DataFrame(data=ohe_matrix, columns=le.classes_) # 데이터 프레임화
result_df = pd.concat([df, dummies_df_2], axis=1)













