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


# 패키지
import pandas as pd # 범주화 및 더미변수화
from sklearn.preprocessing import LabelEncoder, OneHotEncoder # 더미변수화


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

##### 실습 ######
### 실습 데이터 불러오기
df = pd.read_csv('C:\\Users\\wai\\Desktop\\프로젝트\\교육자료\\교육데이터\\BookExample.csv')
df.dtypes
# 과제 1) v1과 v2 변수를 범주화 하기
v1_all_diff = df['v1'].max() - df['v1'].min() # v1 변수의 최대값 - 최소값(전체 구간)
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
df['v1_grade'] = pd.cut(df['v1'], bins=10, labels=labels)

# 데이터 프레임에 'v1_grade_quantile' 신용 등급(10개의 구간을 일정한 분위수로 구분함)
# 변수의 변량에 따라서 분위수를 나누는 구간이 중복가능하기 때문에 duplicates 옵션에 'drop'을 해준다.
# labels=False 옵션을 주어 낮은 구간부터 높은 구간순으로 0,1..6  +1씩 값이 증가하는 구간으로 세팅된다.
df['v1_grade_quantile'] = pd.qcut(df['v1'], q=10, duplicates='drop', labels=False) # 7개의 구간으로 나누어졌다.
# 0 등급부터 라벨링이 되기때문에 'v1_grade_quantile' 컬럼에 전체 적으로 +1을 해준다.
df['v1_grade_quantile'] = df['v1_grade_quantile'] + 1



