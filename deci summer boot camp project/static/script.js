function goToChat(username) {
    window.location = '/chat/' + username;
  }

  document.addEventListener('DOMContentLoaded', function() {
    var socket = io();

    socket.on('connect', function() {
    });

    socket.on('message', function(data) {
      var message = data.msg;
      var timestamp = data.timestamp;
      display_left(message, timestamp);
    });
    socket.on('message1', function(data) {
      var message = data.msg;
      var timestamp = data.timestamp;
      display_right(message, timestamp);
    });

    document.getElementById('messageForm').addEventListener('submit', function(event) {
        event.preventDefault();
        var message = document.getElementById('input').value;
        if (message.trim() === "") {
            return;
        }
        recipient = document.getElementById('name').textContent;
        socket.emit('message', { msg: message, recipient: recipient });
        var currentDateTime = new Date();
        var year = currentDateTime.getFullYear();
        var month = currentDateTime.getMonth() + 1; // getMonth() returns a zero-based value (0-11)
        var day = currentDateTime.getDate();
        var hours = currentDateTime.getHours();
        var mins = currentDateTime.getMinutes();
        var secs = currentDateTime.getSeconds();
        var time = year + "-" + month + "-" + day + " " + hours + ":" + mins + ":" + secs;
        display_left(message, time)
        document.getElementById('input').value = '';
    });

    function display_right(message, time) {
      $('#chat').append('<p class="chatright">' + message + '</div>');
      $('#chat').append('<p class="infol">' + time + '</div>');
    }
    function display_left(message, time){
      $('#chat').append('<div class="chatleft">' + message + '</div>');
      $('#chat').append('<p class="infor">' + time + '</div>');
    }
  });

let points = 0;
function updatePoints(value) {
    points += value;
    document.getElementById('points').innerText = points;
    localStorage.setItem('points', points); // Save points in localStorage
}

// Load points from localStorage if available
document.addEventListener('DOMContentLoaded', function () {
    const storedPoints = localStorage.getItem('points');
    if (storedPoints !== null) {
        points = parseInt(storedPoints);
        document.getElementById('points').innerText = points;
    }

    // إضافة إحصائيات تلوث الهواء
    const stats = document.getElementById('stats');
    stats.innerHTML = `
        <p><strong>مستوى تلوث الهواء اليومي:</strong> 75 µg/m³</p>
        <p><strong>مصادر التلوث الرئيسية:</strong> وسائل النقل (45%), المصانع (35%), مصادر أخرى (20%)</p>
        <p><strong>تأثير تلوث الهواء على الصحة:</strong> يمكن أن يسبب أمراض تنفسية مثل الربو والتهاب الشعب الهوائية، وأيضًا مشاكل قلبية وعائية.</p>
        <p><strong>نصائح لتقليل التلوث:</strong> 
            <ul>
                <li>استخدام وسائل النقل العامة أو الدراجات.</li>
                <li>زرع الأشجار والنباتات لتحسين جودة الهواء.</li>
                <li>دعم السياسات البيئية التي تهدف إلى تقليل الانبعاثات.</li>
            </ul>
        </p>
    `;
});

// التبرع
document.getElementById('donation-form').addEventListener('submit', function(event) {
    event.preventDefault();
    let amount = document.getElementById('amount').value;
    document.getElementById('donation-confirmation').style.display = 'block';
    alert(`شكراً لتبرعك بمقدار ${amount} جنيه مصري.`);
});
