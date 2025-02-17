# コードのQちゃん README

「コードのQちゃん」は、QRコードの読み取りと生成が簡単に行える便利なアプリケーションです。カメラを使ってQRコードをスキャンしたり、テキストから新しいQRコードを作成したりすることができます。

## 特徴

-   **QRコードのスキャン:** パソコンのカメラを使って、QRコードをリアルタイムでスキャンできます。
-   **QRコードの生成:** 入力したテキストからQRコードを生成し、画像として保存できます。
-   **使いやすいインターフェース:** 直感的な操作で、誰でも簡単に利用できます。
-   **自動スキャン:** カメラにQRコードをかざすだけで、自動的にスキャンして内容を表示します。
-   **クリアボタン:** テキスト入力エリアの内容を一発で消去できます。
-   **保存機能:** 生成したQRコードをJPEG画像として保存できます。
-   **長文対応:** 長いテキストからでもQRコードを作成可能！

## 使い方

1.  **アプリケーションの起動:** ダウンロードした「コードのQちゃん.exe」を実行してアプリケーションを起動します。
2.  **QRコードのスキャン:**
    -   カメラが起動し、画面に映像が表示されます。
    -   スキャンしたいQRコードをカメラにかざします。
    -   自動的にQRコードが読み取られ、内容がテキストエリアに表示されます。
3.  **QRコードの生成:**
    -   テキストエリアにQRコードにしたい文字を入力します。
    -   「QRコードの作成」ボタンをクリックします。
    -   入力したテキストからQRコードが生成され、画面に表示されます。
    -   「QRコードを保存」ボタンで、QRコードを画像として保存できます。
    -   「カメラに戻る」ボタンで、カメラ映像に戻ります。
4.  **テキストのクリア:**
    -   「クリア」ボタンをクリックすると、テキストエリアの内容が消去されます。

## 注意点

-   **カメラの使用:** QRコードのスキャンには、パソコンに接続されたカメラが必要です。
-   **文字数制限:** 生成できるQRコードの文字数には上限があります。長いテキストは複数に分けるなどの工夫が必要です。
-   **保存形式:** 生成されたQRコードはJPEG形式で保存されます。

## 開発環境（参考情報）

このアプリケーションは、以下の技術を用いて開発されました。

-   **プログラミング言語:** Python
-   **ライブラリ:**
    -   Tkinter: GUI（ユーザーインターフェース）の構築
    -   OpenCV: カメラ映像の取得とQRコードの検出
    -   Pillow (PIL): 画像処理
    -   qrcode: QRコードの生成

---

「コードのQちゃん」を使って、QRコードをもっと身近に、便利に活用しましょう！
