var ctx = document.getElementById('test2').getContext('2d');
function weekly_coin_op_idx_chart(alt_dict, ctx){
    var chart = new Chart(ctx, {
// The type of chart we want to create
        type: 'horizontalBar',
// The data for our dataset
        data: {
                labels: alt_dict.코인명,
                datasets: [{ label: '점유율',
                                       backgroundColor: 'rgba(0, 233, 214, 1)'
                                       , borderColor: 'rgba(0, 233, 214, 0.46)'
// 긍정 스코어 리스트
                                       , data: alt_dict.점유율 },
                                   ]
                       },



// Configuration options go here
        options: { responsive : false
                    , title: { display: true, text: '주간 알트코인 점유율', fontSize: 30, fontColor: '#34e8ff'}
                    , indexAxis : 'y'
                    , cornerRadius: 20
                    , legend: { labels: { fontColor: 'white', fontSize: 12 } }
                    , scales: { xAxes: [{ ticks: {fontColor: '#1de282', fontSize: '12' } }]
                    , yAxes: [{ ticks: { beginAtZero: true, fontColor: '#34e8ff', fontSize: '12' } }] } } });
}
weekly_coin_op_idx_chart(alt_dict, ctx);