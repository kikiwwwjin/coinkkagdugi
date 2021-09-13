var ctx = document.getElementById('test1').getContext('2d');
function daily_coin_pn_idx_chart(to_dict, ctx){
    var chart = new Chart(ctx, {
    // The type of chart we want to create
        type: 'horizontalBar',
    //  The data for our dataset
        data: {
                labels: to_dict.코인명,
                datasets: [{ label: '긍정 지수',
                                backgroundColor: 'rgba(0, 233, 214, 1)'
                                , borderColor: 'rgba(0, 233, 214, 0.46)'
    // 긍정 스코어 리스트
                                        , data: to_dict.스코어_긍정 },

                                { label: '부정 지수',
                                backgroundColor: 'rgba(255, 112, 53, 1)'
                                , borderColor: 'rgba(255, 112, 53, 0.41)'
    // 긍정 스코어 리스트
                                        , data: to_dict.스코어_부정 }
                            ]
                },

    // Configuration options go here
        options: { responsive : false
                , title: { display: true, text: '오늘의 코인별 긍정 및 부정 지수', fontSize: 30, fontColor: '#34e8ff'}
                , indexAxis : 'y'
                , cornerRadius: 20
                , legend: { labels: { fontColor: 'white', fontSize: 12 } }
                , scales: { xAxes: [{ ticks: {fontColor: '#1de282', fontSize: '12' } }]
                , yAxes: [{ ticks: { beginAtZero: true, fontColor: '#34e8ff', fontSize: '12' } }] } } });
}
daily_coin_pn_idx_chart(to_dict, ctx);