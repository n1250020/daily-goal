<?php
// 日本時間に設定
date_default_timezone_set('Asia/Tokyo');

// --- 1. データベース接続設定 ---
$host = 'localhost';
$dbname = 'your_db'; // 自分のDB名に合わせてください
$user = 'root';
$pass = ''; 

try {
    $pdo = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    exit('データベース接続失敗: ' . $e->getMessage());
}

$message_log = ""; 
$js_notifications = []; // JavaScriptへ渡す通知リスト

// --- 3. 【通知をセット】ボタンが押された時の処理 ---
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['set_notification'])) {
    $set_time = $_POST['scheduled_time'];
    $set_message = $_POST['notification_message'];
    $set_user_id = 1;

    if (!empty($set_time) && !empty($set_message)) {
        $stmt = $pdo->prepare("INSERT INTO notifications (user_id, message, scheduled_at, is_sent) VALUES (?, ?, ?, 0)");
        $stmt->execute([$set_user_id, $set_message, $set_time]);
        $message_log = "通知を予約しました。";
    }
}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>カレンダー</title>
<style>
    progress {
        width: 100%;
        height: 125px;
        margin: 20px 0;
        accent-color: #2ecc71; /* ゲージの色 */
    }
table {
    border-collapse: collapse;
}
th,td{
border: 1px solid #000;
width: 40px;
height: 40px;
text-align: center;
}
.sun{color:red;}
.sat{color:blue;}
</style>
</head>
<body>

    <div>
        <button onclick="location.href='AI.php'">AI</button>
        <button onclick="location.href='calendar.php'">カレンダー</button>
        <button onclick="location.href='schedule.php'">予定</button>
        <button onclick="location.href='chara.php'">アバター</button>
    </div>


    <div class="container">
        <div class="level-badge">Lv. <span id="level">1</span></div>
    
        <progress id="myGauge" value="0" max="100"></progress>
    
        <button onclick="gainExp()">目標達成！（確認用）</button>
        <div id="message" class="message"></div>
    
<h2 style="text-align:right;">2026年1月</h2>

<table>
<tr>
<th class="sun">日</th>
<th>月</th>
<th>火</th>
<th>水</th>
<th>木</th>
<th>金</th>
<th class="sat">土</th>
</tr>
<tr><td></td><td></td><td></td><td></td><td>1</td><td>2</td><td class='sat'>3</td></tr><tr><td class='sun'>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td class='sat'>10</td></tr><tr><td class='sun'>11</td><td>12</td><td>13</td><td>14</td><td>15</td><td>16</td><td class='sat'>17</td></tr><tr><td class='sun'>18</td><td>19</td><td>20</td><td>21</td><td>22</td><td>23</td><td class='sat'>24</td></tr><tr><td class='sun'>25</td><td>26</td><td>27</td><td>28</td><td>29</td><td>30</td><td class='sat'>31</td></tr>
</table>
<div style="max-width: 600px; margin: auto;">
        <h2>🔔 通知予約（カレンダーの日付をクリックして登録）</h2>
        <form method="post" style="background: #f9f9f9; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <label>予定時刻:<br>
                <input placeholder="2016-08-07 05:04:34" name="scheduled_time" step="1" required>
            </label><br><br>
            <label>メッセージ:<br>
                <textarea name="notification_message" required style="width: 100%;"></textarea>
            </label><br><br>
            <button type="submit" name="set_notification">セットする</button>
        </form>

    </div>
<script>
    let lv = 1;
    const gauge = document.getElementById('myGauge');
    const levelText = document.getElementById('level');
    const message = document.getElementById('message');

    function gainExp() {
        // 1回のクリックで増える量
        const amount = 20; 
        gauge.value += amount;

        // 満タン判定
        if (gauge.value >= gauge.max) {
            levelUp();
        }
    }

    function levelUp() {
        lv++;
        levelText.innerText = lv;
        
        // ゲージをリセット
        gauge.value = 0;
        
        // 演出：メッセージを表示
        message.innerText = "LEVEL UP!!";
        setTimeout(() => { message.innerText = ""; }, 1000);

        // おまけ：レベルが上がるごとに最大値を増やして難易度を上げる
        // gauge.max += 50; 
    }
</script>
</body>
</html>
