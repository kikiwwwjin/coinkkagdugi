// 2개의 Dictionary 사용
// 1. bit_dict : 30일 기준의 긍부정 지수 => 30일을 기준으로 잡기위한 dict
// 2. bit_binance_dict : 바이낸스 기준의 각 종 Price 및 index => 종가 index 필요

var ctx = document.getElementById('test3').getContext('2d');
var chart = new Chart(ctx, {
// The type of chart we want to create
    type: 'line',
// The data for our dataset
    data: {
            labels: bit_dict.등록시간,
            datasets: [{ label: '긍부정 지수',
                           backgroundColor: 'rgba(82, 255, 200, 0.3)'
                           , borderColor: 'rgba(82, 255, 200, 1.5)'
// 스코어 합계 리스트
                                   , data: bit_dict.스코어_SCALING },
                        { label: '종가 지수',
                           backgroundColor: 'rgba(247, 58, 73, 0.3)'
                           , borderColor: 'rgba(247, 58, 73, 1.5)'
// 긍정 스코어 리스트
                                   , data: bit_binance_dict.종가_SCALING }

                       ]
           },
// Configuration options go here
    options: {  responsive : false
            , title: { display: true, text: '일별로 보는 비트코인에 대한 긍부정 지수'
            , fontSize: 30, fontColor: '#34e8ff' }
            , legend: { labels: { fontColor: 'white', fontSize: 10 } }
            , scales: { xAxes: [{ ticks: { fontColor: '#1de282', fontSize: '10' } }]
            , yAxes: [{ ticks: { beginAtZero: true, fontColor: '#34e8ff', fontSize: '15' } }] } } });