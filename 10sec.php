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


// --- 2. 【送信実行】ボタンが押された時の処理 ---
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['send_now'])) {
    $now = date('Y-m-d H:i:s');
    
    $stmt = $pdo->prepare("SELECT * FROM notifications WHERE scheduled_at <= ? AND is_sent = 0");
    $stmt->execute([$now]);
    $rows = $stmt->fetchAll();

    if (count($rows) > 0) {
        foreach ($rows as $row) {
            $message_log .= "送信(ID:{$row['id']}): " . htmlspecialchars($row['message']) . "<br>";
            
            // JavaScriptで通知を出すために配列に保存
            $js_notifications[] = [
                'title' => '時間になりました！',
                'body' => $row['message']
            ];
            
            // 送信済みフラグを更新
            $update = $pdo->prepare("UPDATE notifications SET is_sent = 1 WHERE id = ?");
            $update->execute([$row['id']]);
        }
    } else {
        $message_log = "送信対象の通知はありません。";
    }
}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>10秒ごとにリロード</title>
</head>
<body style="font-family: sans-serif; padding: 20px;">



    <script>
    // 1. 通知許可の取得（ページ読み込み時）
    window.onload = function() {
        if (Notification.permission !== "granted") {
            Notification.requestPermission();
        }
    };

    // 2. PHPから渡された通知を表示する（リロード時用）
    const notifications = <?php echo json_encode($js_notifications); ?>;
    if (notifications.length > 0 && Notification.permission === "granted") {
        notifications.forEach(notif => {
            new Notification(notif.title, { body: notif.body });
        });
    }

    // ★ 3. 自動チェック機能（ここを追加！）
    // 60秒（60000ミリ秒）ごとに、自分自身に「送信実行」の命令を送る
    setInterval(() => {
        console.log("自動チェック中...");
        
        // フォームを自動で送信（ページをリロードしてチェックを実行）
        // 'send_now' ボタンが押されたときと同じ動作をさせます
        const form = document.createElement('form');
        form.method = 'POST';
        
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'send_now';
        input.value = '1';
        
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
        
    }, 10000); 
</script>
</body>
</html>
