import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import qrcode
import os


class QRCodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("すごいぞコードのQちゃん！")
        self.root.geometry("700x600")  # ウィンドウサイズを調整

        # 上部ボタンエリアのフレーム
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # QRコード生成ボタン
        self.generate_button = tk.Button(
            button_frame, text="QRコードの作成", command=self.generate_qr_code
        )
        self.generate_button.grid(row=0, column=0, padx=20)

        # カメラに戻るボタン（デフォルトで非表示）
        self.return_to_camera_button = tk.Button(
            button_frame, text="カメラに戻る", command=self.return_to_camera
        )
        self.return_to_camera_button.grid(row=0, column=1, padx=20)
        self.return_to_camera_button.grid_remove()  # 初期状態では非表示

        # 保存ボタン（QRコード生成後に表示）
        self.save_button = tk.Button(
            button_frame, text="QRコードを保存", command=self.save_qr_code
        )
        self.save_button.grid(row=0, column=2, padx=20)
        self.save_button.grid_remove()  # 初期状態では非表示

        # テキストフィールドのラベル
        self.result_label = tk.Label(root, text="スキャンまたは生成するテキスト:")
        self.result_label.pack()

        # テキストフィールドとクリアボタン用のフレーム
        text_frame = tk.Frame(root)
        text_frame.pack(pady=10)

        # クリアボタンの作成
        self.clear_button = tk.Button(
            text_frame, text="クリア", command=self.clear_text
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # スクロールバー付きテキストウィジェット
        self.result_text = tk.Text(text_frame, height=5, width=60, wrap="word")
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # スクロールバーの作成
        scroll_bar = tk.Scrollbar(text_frame, command=self.result_text.yview)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=scroll_bar.set)

        # カメラ映像表示エリア
        self.canvas = tk.Canvas(
            root, width=400, height=400
        )  # QRコードを小さめに表示するためサイズ調整
        self.canvas.pack(pady=20)

        # ビデオキャプチャのセットアップ
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise ValueError("カメラを開けませんでした")
        except Exception as e:
            messagebox.showerror("エラー", f"カメラの初期化に失敗しました: {str(e)}")
            self.root.destroy()
            return

        self.detector = cv2.QRCodeDetector()
        self.show_qr_code = False  # QRコード表示モードのフラグ
        self.qr_image = None  # 生成したQRコードの画像を保持
        self.update_frame()

    def update_frame(self):
        if not self.show_qr_code:
            try:
                # カメラからフレームを取得
                ret, frame = self.cap.read()
                if ret:
                    # フレームを反転して自然な向きに
                    frame = cv2.flip(frame, 1)

                    # OpenCVの画像をPIL画像に変換して表示
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)

                    # キャンバスサイズに合わせてリサイズ
                    img = img.resize((400, 400), Image.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)

                    # キャンバスをクリアしてから新しい画像を表示
                    self.canvas.delete("all")
                    self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
                    self.canvas.imgtk = imgtk

                    try:
                        # QRコード検出処理
                        data, vertices, _ = self.detector.detectAndDecode(frame)
                        if data:
                            self.result_text.delete("1.0", tk.END)
                            self.result_text.insert(tk.END, data)
                    except cv2.error:
                        # QRコード検出エラーは無視して続行
                        pass
            except Exception as e:
                print(f"カメラフレームの処理中にエラーが発生: {str(e)}")

        # 30ms後に再度update_frameを呼び出し
        self.root.after(30, self.update_frame)

    def generate_qr_code(self):
        # 入力値の検証を強化
        text = self.result_text.get("1.0", tk.END).strip()
        if not self.validate_input(text):
            messagebox.showwarning("セキュリティ警告", "不正な入力が検出されました")
            return

        # テキストが多すぎる場合のチェック
        max_characters = 4000  # バージョン40、エラーレベルLの場合の上限
        if len(text) > max_characters:
            messagebox.showwarning(
                "文字数エラー",
                f"テキストが長すぎます。{max_characters}文字以内にしてください。",
            )
            return

        # QRコードオブジェクトを作成し、エラーレベルと余白を指定
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # 最低エラーレベルに設定
            box_size=8,  # 表示サイズを小さくするためボックスサイズ調整
            border=4,  # 余白を小さく設定4
        )
        qr.add_data(text)  # データを追加
        qr.make(fit=True)  # データに合わせてサイズ調整

        # QRコードをカメラ映像エリアに表示する
        self.qr_image = qr.make_image(fill="black", back_color="white")
        self.show_qr_code = True  # QRコード表示モードに切り替え
        self.qr_image = self.qr_image.resize(
            (400, 400), Image.LANCZOS  # キャンバスサイズに合わせてリサイズ
        )
        qr_imgtk = ImageTk.PhotoImage(self.qr_image)
        self.canvas.create_image(0, 0, anchor="nw", image=qr_imgtk)
        self.canvas.imgtk = qr_imgtk

        # 「カメラに戻る」ボタンと「保存」ボタンを表示
        self.return_to_camera_button.grid()
        self.save_button.grid()

    def validate_input(self, text):
        # 危険な文字列やパターンをチェック
        import re

        # 例: スクリプトタグ、制御文字などをブロック
        dangerous_patterns = [
            r"<script.*?>.*?</script>",
            r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        ]
        return not any(
            re.search(pattern, text, re.IGNORECASE) for pattern in dangerous_patterns
        )

    def save_qr_code(self):
        if self.qr_image is None:
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg", filetypes=[("JPEGファイル", "*.jpg")]
            )
            if file_path:
                # パスの検証
                if not os.path.abspath(file_path).startswith(os.path.expanduser("~")):
                    messagebox.showerror("エラー", "不正なファイルパスです")
                    return

                self.qr_image.convert("RGB").save(file_path, "JPEG")
                messagebox.showinfo("保存完了", "QRコードが保存されました")
        except Exception as e:
            messagebox.showerror("エラー", f"保存中にエラーが発生しました: {str(e)}")

    def clear_text(self):
        # テキストフィールドをクリア
        self.result_text.delete("1.0", tk.END)

    def return_to_camera(self):
        # カメラ映像に戻る
        self.show_qr_code = False
        self.qr_image = None  # QRコード画像をクリア
        self.canvas.delete("all")  # キャンバスをクリア
        self.return_to_camera_button.grid_remove()
        self.save_button.grid_remove()

    def cleanup(self):
        # リソースの適切な解放
        if hasattr(self, "cap"):
            try:
                self.cap.release()
            except:
                pass

    def __del__(self):
        self.cleanup()


# アプリケーションのメイン処理
if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeScannerApp(root)
    # ウィンドウが閉じられる時の処理を追加
    root.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), root.destroy()))
    root.mainloop()
