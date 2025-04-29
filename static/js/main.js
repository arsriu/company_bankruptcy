
// 결과의 퍼센트만큼 표의 색이 변경
window.onload = function() {
    var percent = parseFloat(document.querySelector('.center').textContent);
    var result = document.querySelector('#result').textContent;

    // 배경색 업데이트
    var rows = document.querySelectorAll('table tbody tr');
    rows.forEach(function(row) {
        // 모든 행의 배경색을 초기화
        row.style.backgroundColor = 'white';
        document.querySelector('#good').style.backgroundColor = 'white';
        document.querySelector('#bad').style.backgroundColor = 'white';
    });

    if (result === '긍정입니다.') {
        if (parseFloat(percent) >= 80 && parseFloat(percent) <= 100) {
            document.querySelector('.positive-grade1').style.backgroundColor = '#A2FFA2';
            document.querySelector('#good').style.backgroundColor = '#A2FFA2';
        } else if (parseFloat(percent) >= 51 && parseFloat(percent) < 80) {
            document.querySelector('.positive-grade2').style.backgroundColor = '#A2FFA2';
            document.querySelector('#good').style.backgroundColor = '#A2FFA2';
        }
    } else if (result === '부정입니다.') {
        if (parseFloat(percent) >= 51 && parseFloat(percent) <= 70) {
            document.querySelector('.negative-grade1').style.backgroundColor = '#FF5F5F';
            document.querySelector('#bad').style.backgroundColor = '#FF5F5F';
        } else if (parseFloat(percent) > 70 && parseFloat(percent) <= 80) {
            document.querySelector('.negative-grade2').style.backgroundColor = '#FF5F5F';
            document.querySelector('#bad').style.backgroundColor = '#FF5F5F';
        } else if (parseFloat(percent) > 80 && parseFloat(percent) <= 100) {
            document.querySelector('.negative-grade3').style.backgroundColor = '#FF5F5F';
            document.querySelector('#bad').style.backgroundColor = '#FF5F5F';
        }
    }
}
