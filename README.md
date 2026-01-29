# daily-goal
#index.php,10sec.phpを</br>
c:/laragon/www の中に dailygoal フォルダを作成しその中に2つを入れる</br>
laragonを起動しhttp://localhost/dailygoal/index.php にアクセス


#通知データベース作成

CREATE DATABASE your_db;

#テーブル作成

CREATE TABLE notifications (</br>
    id INT AUTO_INCREMENT PRIMARY KEY,</br>
    user_id INT NOT NULL,</br>
    message TEXT NOT NULL,</br>
    scheduled_at DATETIME NOT NULL, -- ここに 11:08:00 などを保存</br>
    is_sent TINYINT(1) DEFAULT 0    -- 0:未送信, 1:送信済み</br>
);
