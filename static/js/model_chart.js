var ctx = document.getElementById('model_chart').getContext('2d');
function model_chart(bit_score_dict, ctx){
    var chart = new Chart(ctx, {
// The type of chart we want to create
        type: 'line',
// The data for our dataset
        data: {
                labels: bit_score_dict.등록시간,
                datasets: [{ label: '종가',
                                       backgroundColor: 'rgba(0, 233, 214, 1)'
                                       , borderColor: 'rgba(0, 233, 214, 1)'
                                       // y축 높이 선으로 매우기
                                       , fill : false
                                       // 선굵기
                                       , borderWidth : 1
                                       // 꼭지점 제거
                                       , pointRadius: 0
                                        // 실제값 '종가'
                                       , data: bit_score_dict.종가 },
                           { label: '전통모델_예측값',
                                       backgroundColor: 'rgba(221, 58, 123, 1)'
                                       , borderColor: 'rgba(221, 58, 123, 1)'
                                       // y축 높이 선으로 매우기
                                       , fill : false
                                       // 선굵기
                                       , borderWidth : 1
                                       // 꼭지점 제거
                                       , pointRadius: 0
                                        // 실제값 '종가'
                                       , data: bit_score_dict.전통모델_예측값 },
                           { label: 'DNN_예측값',
                                       backgroundColor: 'rgba(255, 255, 6, 1)'
                                       , borderColor: 'rgba(255, 255, 6, 1)'
                                       // y축 높이 선으로 매우기
                                       , fill : false
                                       // 선굵기
                                       , borderWidth : 1
                                       // 꼭지점 제거
                                       , pointRadius: 0
                                        // 실제값 '종가'
                                       , data: bit_score_dict.DNN_예측값 },
                           { label: 'LSTM_예측값',
                                       backgroundColor: 'rgba(236, 95, 45, 1)'
                                       , borderColor: 'rgba(236, 95, 45, 1)'
                                       // y축 높이 선으로 매우기
                                       , fill : false
                                       // 선굵기
                                       , borderWidth : 1
                                       // 꼭지점 제거
                                       , pointRadius: 0
                                        // 실제값 '종가'
                                       , data: bit_score_dict.LSTM_예측값 }






                             ]




              },



// Configuration options go here
        options: { responsive : false
                    , title: { display: true, text: '일별 종가 모델별 예측값 및 실제값', fontSize: 30, fontColor: '#34e8ff'}
                    , legend: { labels: { fontColor: 'white', fontSize: 12 } }
                    , scales: {
                                xAxes: [{ ticks : { fontColor: '#1de282', fontSize: '12' } }]
                                , yAxes: [{ ticks : { fontColor: '#34e8ff', fontSize: '12' } }]
                                }
                  } });
}
model_chart(bit_score_dict, ctx);