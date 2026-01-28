　# daily-goal
#index.php,10sec.phpを</br>
laragon/www/dailygoalの中に</br>
laragonを起動しhttp://localhost/dailygoal/index.php にアクセス


#通知データベース作成

CREATE DATABASE your_db;

#テーブル作成

CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    scheduled_at DATETIME NOT NULL, -- ここに 11:08:00 などを保存
    is_sent TINYINT(1) DEFAULT 0    -- 0:未送信, 1:送信済み
);
