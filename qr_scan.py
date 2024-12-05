import tkinter as tk
from tkinter import messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import qrcode


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
        self.cap = cv2.VideoCapture(0)
        self.detector = cv2.QRCodeDetector()
        self.show_qr_code = False  # QRコード表示モードのフラグ
        self.qr_image = None  # 生成したQRコードの画像を保持
        self.update_frame()

    def update_frame(self):
        if not self.show_qr_code:
            # カメラからフレームを取得
            ret, frame = self.cap.read()
            if ret:
                # OpenCVの画像をPIL画像に変換して表示
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
                self.canvas.imgtk = imgtk

                # 自動スキャン処理
                data, vertices, _ = self.detector.detectAndDecode(frame)
                if data:
                    self.result_text.delete("1.0", tk.END)
                    self.result_text.insert(tk.END, data)
        # 30ms後に再度update_frameを呼び出し（ループの継続）
        self.root.after(30, self.update_frame)

    def generate_qr_code(self):
        # テキストフィールドの内容からQRコードを生成
        text = self.result_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning(
                "入力エラー", "テキストフィールドに文字を入力してください"
            )
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

    def save_qr_code(self):
        # QRコードの画像を保存する
        if self.qr_image is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg", filetypes=[("JPEGファイル", "*.jpg")]
            )
            if file_path:
                self.qr_image.convert("RGB").save(file_path, "JPEG")
                messagebox.showinfo("保存完了", "QRコードが保存されました")

    def clear_text(self):
        # テキストフィールドをクリア
        self.result_text.delete("1.0", tk.END)

    def return_to_camera(self):
        # カメラ映像に戻る
        self.show_qr_code = False
        self.return_to_camera_button.grid_remove()  # 「カメラに戻る」ボタンを非表示
        self.save_button.grid_remove()  # 「保存」ボタンも非表示

    def __del__(self):
        # ウィンドウを閉じるときにカメラリソースを解放
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()


# アプリケーションのメイン処理
if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeScannerApp(root)
    root.mainloop()
