########################################################################################################################
###################################################### python 스케일링 ##################################################
########################################################################################################################


import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler, MinMaxScaler, MaxAbsScaler, RobustScaler
import matplotlib.pyplot as plt

# 0. scaling 할 numpy 선언
scale_data = np.array([-150,-110,-30,0,20,30,110,120,130,150])


# 1. StandardScaler : 평균을 0, 분산을 1로 변경됩니다.(이상치에 영향이 큽니다.)
standardscaler = StandardScaler()
print(scale_data, ',', standardscaler)
std_scaling = standardscaler.fit_transform(scale_data.reshape(-1,1))
print(std_scaling)
# plt.hist(std_scaling, bins=std_scaling.shape[0])
# plt.show()

# 2. MinmaxScaler : 모든 feature가 0과 1 사이에 위치하게 만듭니다.(이상치가 있을경우 다른 값들이 매우 압축된 범위에서만 움직이게 됩니다.)
minmaxscaler = MinMaxScaler()
mm_scaling = minmaxscaler.fit_transform(scale_data.reshape(-1,1))
print(mm_scaling)


# 3. MaxAbsScaler : 절대값이 0~1사이에 매핑되도록 합니다. 즉 -1~1 사이로 재조정됩니다.
# 양수 데이터로만 구성된 특징 데이터 셋에서는 MinMaxScaler와 유사하게 동작하며, 큰 이상치에 민감할 수 있습니다.
maxabsscaler = MaxAbsScaler()
maxabs_scaling = maxabsscaler.fit_transform(scale_data.reshape(-1,1))
print(maxabs_scaling)

# 4. RobustScaler : 모든 특성들이 같은 크기를 갖는다는 점에서 StandardScaler와 비슷하지만, 평균과 분산 대신 median과 quantile을 사용합니다.
# 아웃라이어(이상치)에 영향을 최소화한 기법입니다. 중앙값(median)과 IQR(Interquantile range)을 사용하기 때문에 StandardScaler와 비교해보면
# IQR = Q3 - Q1 : 즉, 25퍼센타일과 75퍼센타일의 값들을 다룬다.
# 표준화 후 동일한 값을 더 넓게 분포시키고 있음을 확인 할 수 있습니다.
robustscaler = RobustScaler()
rb_scaling = robustscaler.fit_transform(scale_data.reshape(-1,1))
print(rb_scaling)
# plt.hist(rb_scaling, bins=rb_scaling.shape[0])

### 실습 ###

