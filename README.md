# すごいぞコードのQちゃん！

QRコードスキャナーアプリケーション - カメラを使用してQRコードを読み取り、新しいQRコードを生成できるPythonアプリケーション

## 機能

- リアルタイムQRコード検出
- QRコード生成
- テキスト入力と編集
- QRコード画像の保存
- セキュアな入力検証

## 必要条件

- Python 3.8以上
- Webカメラ
- Windows OS

## インストール

1. リポジトリをクローン：
```bash
git clone https://github.com/yourusername/qr-code-scanner.git
cd qr-code-scanner
```

2. 仮想環境を作成して有効化：
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. 依存関係をインストール：
```bash
pip install -r requirements.txt
```

## 使用方法

1. アプリケーションを起動：
```bash
python qr_scan.py
```

2. 機能：
   - カメラを使用してQRコードをスキャン
   - テキストを入力してQRコードを生成
   - 生成したQRコードを画像として保存
   - テキストのクリアや編集

## テスト

テストを実行：
```bash
python -m unittest test_qr_scan.py -v
```

## 制限事項

- QRコードのバージョン40、エラーレベルLの場合、最大4000文字まで対応
- カメラが必要です
- Windows OSのみ対応

## ライセンス

MITライセンス
