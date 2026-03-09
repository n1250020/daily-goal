# daily-goal

https://synchronistical-nongenuinely-shayne.ngrok-free.dev</br>
#ホーム画面
メニューから機能を使えるようにする</br>
機能:Gemini API
機能：ゲージからのポイント交換(竹)
機能：アプリ内の設定(色やポイントで交換したアバターの変更など)
DBの統合
カレンダーと通知機能の紐付け、その後DBと共に一つのPCにすべての機能を統合する

#django
https://qiita.com/pythonista/items/19613663ef7bb3c57d4f

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
