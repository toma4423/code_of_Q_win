"""
QRコードスキャナーアプリケーションのテストモジュール

このモジュールは、QRコードスキャナーアプリケーションの機能をテストします。
GUIテストはモック化され、コアロジックのみをテストします。
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
from tkinter import ttk
import numpy as np
import cv2
from PIL import Image, ImageTk
import os
from qr_scan import QRCodeScannerApp


# GitHub Actions環境かどうかを判定
def is_github_actions():
    """GitHub Actions環境かどうかを判定する"""
    return os.environ.get("GITHUB_ACTIONS") == "true"


class TestQRCodeScannerApp(unittest.TestCase):
    """QRコードスキャナーアプリケーションのテストクラス"""

    def setUp(self):
        """テストの前準備"""
        # Tkinterのルートウィンドウをモック化
        self.root = Mock(spec=tk.Tk)
        self.root.tk = Mock()
        self.root.winfo_exists.return_value = True

        # 必要なウィジェットをモック化
        self.mock_text = Mock(spec=tk.Text)
        self.mock_canvas = Mock(spec=tk.Canvas)
        self.mock_status_var = Mock(spec=tk.StringVar)
        self.mock_frame = Mock(spec=ttk.Frame)
        self.mock_label_frame = Mock(spec=ttk.LabelFrame)
        self.mock_scrollbar = Mock(spec=ttk.Scrollbar)

        # モックウィジェットの設定
        self.mock_text.tk = Mock()
        self.mock_canvas.tk = Mock()
        self.mock_frame.tk = Mock()
        self.mock_label_frame.tk = Mock()
        self.mock_scrollbar.tk = Mock()

        # テキストウィジェットのメソッドをモック化
        self.mock_text.get.side_effect = lambda start, end: "テストテキスト"

        # カメラのモックを設定
        self.mock_camera_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.mock_cap = Mock(spec=cv2.VideoCapture)
        self.mock_cap.read.return_value = (True, self.mock_camera_frame)
        self.mock_cap.isOpened.return_value = True

        # アプリケーションインスタンスを作成
        with patch("tkinter.Text", return_value=self.mock_text), patch(
            "tkinter.Canvas", return_value=self.mock_canvas
        ), patch("tkinter.StringVar", return_value=self.mock_status_var), patch(
            "tkinter.ttk.Frame", return_value=self.mock_frame
        ), patch(
            "tkinter.ttk.Label"
        ), patch(
            "tkinter.ttk.Button"
        ), patch(
            "tkinter.ttk.LabelFrame", return_value=self.mock_label_frame
        ), patch(
            "tkinter.ttk.Scrollbar", return_value=self.mock_scrollbar
        ), patch(
            "cv2.VideoCapture", return_value=self.mock_cap
        ), patch(
            "PIL.ImageTk.PhotoImage", return_value=Mock()
        ), patch(
            "tkinter.messagebox.showerror"
        ), patch(
            "tkinter.messagebox.showinfo"
        ), patch(
            "tkinter.messagebox.showwarning"
        ):
            self.app = QRCodeScannerApp(self.root)
            # フレーム処理スレッドを停止
            self.app.is_running = False
            if hasattr(self.app, "processing_thread"):
                self.app.processing_thread.join()

            # テキストウィジェットの参照を設定
            self.app.result_text = self.mock_text

    def tearDown(self):
        """テスト後のクリーンアップ"""
        self.app.is_running = False
        if hasattr(self.app, "processing_thread"):
            self.app.processing_thread.join()
        if hasattr(self.app, "camera"):
            self.app.camera.release()
        self.root.destroy()

    @unittest.skipIf(is_github_actions(), "GitHub Actions環境ではスキップ")
    def test_camera_initialization(self):
        """カメラ初期化のテスト"""
        with patch("cv2.VideoCapture") as mock_capture, patch(
            "tkinter.messagebox.showerror"
        ) as mock_error:
            # カメラが開けない場合のテスト
            mock_capture.return_value.isOpened.return_value = False
            self.app._setup_camera()
            mock_error.assert_called_once()

            # カメラが正常に開く場合のテスト
            mock_capture.return_value.isOpened.return_value = True
            mock_capture.return_value.read.return_value = (True, self.mock_camera_frame)
            self.app._setup_camera()
            self.assertTrue(hasattr(self.app, "cap"))

    def test_qr_code_generation(self):
        """QRコード生成機能のテスト"""
        test_text = "テストテキスト"
        self.mock_text.get.side_effect = lambda start, end: test_text

        with patch("qrcode.QRCode") as mock_qr, patch(
            "PIL.ImageTk.PhotoImage", return_value=Mock()
        ) as mock_photo:
            mock_qr_instance = MagicMock()
            mock_qr.return_value = mock_qr_instance
            mock_image = Mock()
            mock_qr_instance.make_image.return_value = mock_image

            self.app.generate_qr_code()
            mock_qr_instance.add_data.assert_called_once_with(test_text)
            mock_photo.assert_called_once()

    def test_text_validation(self):
        """テキスト入力の検証テスト"""
        # 空のテキスト（許可される）
        self.assertTrue(self.app._validate_input(""))
        # 正常なテキスト
        self.assertTrue(self.app._validate_input("テスト"))
        # 長すぎるテキスト（検証関数では長さはチェックしない）
        self.assertTrue(self.app._validate_input("a" * 4001))
        # 危険な文字列
        self.assertFalse(self.app._validate_input("<script>alert('test')</script>"))
        # 制御文字を含む文字列
        self.assertFalse(self.app._validate_input("test\x00test"))

    @unittest.skipIf(is_github_actions(), "GitHub Actions環境ではスキップ")
    def test_save_qr_code(self):
        """QRコード保存機能のテスト"""
        test_text = "テストテキスト"
        self.mock_text.get.side_effect = lambda start, end: test_text

        with patch("tkinter.filedialog.asksaveasfilename") as mock_save_dialog, patch(
            "qrcode.QRCode"
        ) as mock_qr, patch("PIL.Image.Image.save") as mock_save, patch(
            "PIL.ImageTk.PhotoImage", return_value=Mock()
        ) as mock_photo, patch(
            "os.path.expanduser", return_value="/home/user"
        ) as mock_expanduser, patch(
            "os.path.abspath", return_value="/home/user/test.jpg"
        ) as mock_abspath, patch(
            "tkinter.messagebox.showinfo"
        ) as mock_info, patch(
            "tkinter.messagebox.showerror"
        ) as mock_error:

            # QRコード生成の準備
            mock_save_dialog.return_value = "/home/user/test.jpg"
            mock_qr_instance = MagicMock()
            mock_qr.return_value = mock_qr_instance
            mock_image = MagicMock()
            mock_converted_image = MagicMock()
            mock_image.convert.return_value = mock_converted_image
            mock_qr_instance.make_image.return_value = mock_image

            # QRコードを生成して保存
            self.app.generate_qr_code()
            self.app.qr_image = mock_image
            self.app.save_qr_code()

            # 検証
            mock_image.convert.assert_called_once_with("RGB")
            mock_converted_image.save.assert_called_once_with(
                "/home/user/test.jpg", "JPEG"
            )
            mock_info.assert_called_once_with("保存完了", "QRコードが保存されました")
            mock_error.assert_not_called()

            # 不正なパスでの保存テスト
            mock_save_dialog.return_value = "/tmp/test.jpg"
            mock_abspath.return_value = "/tmp/test.jpg"
            mock_error.reset_mock()

            self.app.save_qr_code()
            mock_error.assert_called_once_with("エラー", "不正なファイルパスです")
            mock_converted_image.save.assert_called_once()  # 2回目は呼ばれないことを確認


if __name__ == "__main__":
    unittest.main()
