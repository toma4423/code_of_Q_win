"""
QRコードスキャナーアプリケーション

このアプリケーションは以下の機能を提供します：
- カメラを使用したQRコードのスキャン
- QRコードの生成と保存
- テキストの入力と編集

主な特徴：
- リアルタイムQRコード検出
- カスタマイズ可能なQRコード生成
- 直感的なユーザーインターフェース
- セキュアな入力検証

制限事項：
- カメラが必要です
- QRコードのバージョン40、エラーレベルLの場合、最大4000文字まで対応
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import cv2
from PIL import Image, ImageTk
import qrcode
import os
import logging
from typing import Optional, Tuple
import threading
from queue import Queue

# ロギングの設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class QRCodeScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("すごいぞコードのQちゃん！")
        self.root.geometry("800x700")

        # スレッドセーフなキュー
        self.frame_queue = Queue(maxsize=2)
        self.processing_thread = None
        self.is_running = True

        self._setup_ui()
        self._setup_camera()
        self._start_processing_thread()

    def _setup_ui(self):
        """UIコンポーネントの初期化"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 上部ボタンエリア
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)

        # ボタンの作成
        self.generate_button = ttk.Button(
            button_frame, text="QRコードの作成", command=self.generate_qr_code
        )
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.return_to_camera_button = ttk.Button(
            button_frame, text="カメラに戻る", command=self.return_to_camera
        )
        self.return_to_camera_button.pack(side=tk.LEFT, padx=5)
        self.return_to_camera_button.pack_forget()

        self.save_button = ttk.Button(
            button_frame, text="QRコードを保存", command=self.save_qr_code
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.save_button.pack_forget()

        # テキストエリア
        text_frame = ttk.LabelFrame(
            main_frame, text="スキャンまたは生成するテキスト:", padding="5"
        )
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # テキストウィジェットとスクロールバー
        self.result_text = tk.Text(text_frame, height=5, wrap="word")
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.result_text.yview
        )
        self.result_text.configure(yscrollcommand=scrollbar.set)

        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # クリアボタン
        self.clear_button = ttk.Button(
            text_frame, text="クリア", command=self.clear_text
        )
        self.clear_button.pack(side=tk.BOTTOM, pady=5)

        # カメラ表示エリア
        self.canvas = tk.Canvas(main_frame, width=400, height=400)
        self.canvas.pack(pady=20)

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=5)

    def _setup_camera(self):
        """カメラの初期化"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise ValueError("カメラを開けませんでした")

            # カメラの設定
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.detector = cv2.QRCodeDetector()
            self.show_qr_code = False
            self.qr_image = None

        except Exception as e:
            logger.error(f"カメラの初期化に失敗: {str(e)}")
            messagebox.showerror("エラー", f"カメラの初期化に失敗しました: {str(e)}")
            self.root.destroy()
            return

    def _start_processing_thread(self):
        """画像処理スレッドの開始"""
        self.processing_thread = threading.Thread(
            target=self._process_frames, daemon=True
        )
        self.processing_thread.start()

    def _process_frames(self):
        """フレーム処理のメインループ"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                # フレームを反転
                frame = cv2.flip(frame, 1)

                # QRコード検出
                if not self.show_qr_code:
                    try:
                        data, vertices, _ = self.detector.detectAndDecode(frame)
                        if data:
                            self.root.after(0, self._update_text, data)
                    except cv2.error as e:
                        logger.warning(f"QRコード検出エラー: {str(e)}")

                # フレームをキューに追加
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)

            except Exception as e:
                logger.error(f"フレーム処理エラー: {str(e)}")

        self._update_display()

    def _update_display(self):
        """画面表示の更新"""
        if not self.show_qr_code and self.is_running:
            try:
                if not self.frame_queue.empty():
                    frame = self.frame_queue.get()
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame_rgb)
                    img = img.resize((400, 400), Image.LANCZOS)
                    imgtk = ImageTk.PhotoImage(image=img)

                    self.canvas.delete("all")
                    self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
                    self.canvas.imgtk = imgtk

            except Exception as e:
                logger.error(f"表示更新エラー: {str(e)}")

        if self.is_running:
            self.root.after(30, self._update_display)

    def _update_text(self, text: str):
        """テキストエリアの更新"""
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, text)
        self.status_var.set("QRコードを検出しました")

    def generate_qr_code(self):
        """QRコードの生成"""
        text = self.result_text.get("1.0", tk.END).strip()

        if not self._validate_input(text):
            messagebox.showwarning("セキュリティ警告", "不正な入力が検出されました")
            return

        if len(text) > 4000:
            messagebox.showwarning(
                "文字数エラー", "テキストが長すぎます。4000文字以内にしてください。"
            )
            return

        try:
            qr = qrcode.QRCode(
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)

            self.qr_image = qr.make_image(fill="black", back_color="white")
            self.qr_image = self.qr_image.resize((400, 400), Image.LANCZOS)

            self.show_qr_code = True
            qr_imgtk = ImageTk.PhotoImage(self.qr_image)
            self.canvas.create_image(0, 0, anchor="nw", image=qr_imgtk)
            self.canvas.imgtk = qr_imgtk

            self.return_to_camera_button.pack(side=tk.LEFT, padx=5)
            self.save_button.pack(side=tk.LEFT, padx=5)
            self.status_var.set("QRコードを生成しました")

        except Exception as e:
            logger.error(f"QRコード生成エラー: {str(e)}")
            messagebox.showerror("エラー", f"QRコードの生成に失敗しました: {str(e)}")

    def _validate_input(self, text: str) -> bool:
        """入力値の検証"""
        import re

        dangerous_patterns = [
            r"<script.*?>.*?</script>",
            r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]",
        ]
        return not any(
            re.search(pattern, text, re.IGNORECASE) for pattern in dangerous_patterns
        )

    def save_qr_code(self):
        """QRコードの保存"""
        if self.qr_image is None:
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".jpg", filetypes=[("JPEGファイル", "*.jpg")]
            )

            if file_path:
                if not os.path.abspath(file_path).startswith(os.path.expanduser("~")):
                    messagebox.showerror("エラー", "不正なファイルパスです")
                    return

                self.qr_image.convert("RGB").save(file_path, "JPEG")
                self.status_var.set("QRコードを保存しました")
                messagebox.showinfo("保存完了", "QRコードが保存されました")

        except Exception as e:
            logger.error(f"QRコード保存エラー: {str(e)}")
            messagebox.showerror("エラー", f"保存中にエラーが発生しました: {str(e)}")

    def clear_text(self):
        """テキストエリアのクリア"""
        self.result_text.delete("1.0", tk.END)
        self.status_var.set("テキストをクリアしました")

    def return_to_camera(self):
        """カメラ表示に戻る"""
        self.show_qr_code = False
        self.qr_image = None
        self.canvas.delete("all")
        self.return_to_camera_button.pack_forget()
        self.save_button.pack_forget()
        self.status_var.set("カメラ表示に戻りました")

    def cleanup(self):
        """リソースの解放"""
        self.is_running = False
        if hasattr(self, "cap"):
            try:
                self.cap.release()
            except Exception as e:
                logger.error(f"カメラ解放エラー: {str(e)}")

    def __del__(self):
        """デストラクタ"""
        self.cleanup()


if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeScannerApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.cleanup(), root.destroy()))
    root.mainloop()
