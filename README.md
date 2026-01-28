# daily-goal
#ホーム画面
メニューから機能を使えるようにする</br>
機能:OpenAI API
機能：ゲージからのポイント交換(竹)
機能：アプリ内の設定(色の変更)


#通知データベース作成

CREATE DATABASE your_db;

#テーブル作成

CREATE TABLE notifications (</br>
    id INT AUTO_INCREMENT PRIMARY KEY,</br>
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    scheduled_at DATETIME NOT NULL, -- ここに 11:08:00 などを保存
    is_sent TINYINT(1) DEFAULT 0    -- 0:未送信, 1:送信済み
);
