"""
QRコードスキャナーアプリケーションのテストモジュール

このモジュールでは、QRコードスキャナーアプリケーションの各機能をテストします。
主なテスト項目：
- UIコンポーネントの初期化
- カメラ機能
- QRコード生成
- テキスト処理
- ファイル保存
"""

import unittest
import tkinter as tk
from unittest.mock import MagicMock, patch
import cv2
import numpy as np
from PIL import Image
import qr_scan


class TestQRCodeScannerApp(unittest.TestCase):
    """QRコードスキャナーアプリケーションのテストクラス"""

    def setUp(self):
        """各テストケースの前処理"""
        self.root = tk.Tk()
        # カメラのモックを作成
        self.mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with patch("cv2.VideoCapture") as mock_cap:
            mock_cap.return_value.read.return_value = (True, self.mock_frame)
            mock_cap.return_value.isOpened.return_value = True
            self.app = qr_scan.QRCodeScannerApp(self.root)
        self.app.cap = MagicMock()
        self.app.cap.read.return_value = (True, self.mock_frame)
        # フレーム処理スレッドを停止
        self.app.is_running = False
        if self.app.processing_thread:
            self.app.processing_thread.join()

    def tearDown(self):
        """各テストケースの後処理"""
        try:
            if hasattr(self.app, "cap"):
                self.app.cap.release()
            if hasattr(self.app, "root"):
                self.app.root.quit()
                self.app.root.destroy()
        except:
            pass

    def test_ui_initialization(self):
        """UIコンポーネントの初期化テスト"""
        # メインフレームの存在確認
        self.assertTrue(hasattr(self.app.root, "children"))
        self.assertIsInstance(self.app.canvas, tk.Canvas)
        self.assertIsInstance(self.app.result_text, tk.Text)
        self.assertIsInstance(self.app.status_var, tk.StringVar)

    def test_camera_initialization(self):
        """カメラ初期化のテスト"""
        with patch("cv2.VideoCapture") as mock_cap:
            # 正常なカメラ初期化
            mock_cap.return_value.isOpened.return_value = True
            self.app._setup_camera()
            self.assertTrue(hasattr(self.app, "cap"))

            # カメラ初期化失敗
            mock_cap.return_value.isOpened.return_value = False
            with patch("tkinter.messagebox.showerror") as mock_error:
                self.app._setup_camera()
                mock_error.assert_called_once()

    def test_text_validation(self):
        """テキスト入力の検証テスト"""
        # 正常なテキスト
        valid_text = "テスト123"
        self.assertTrue(self.app._validate_input(valid_text))

        # 危険なパターンを含むテキスト
        dangerous_text = "<script>alert('test')</script>"
        self.assertFalse(self.app._validate_input(dangerous_text))

        # 日本語テキスト
        japanese_text = "こんにちは世界"
        self.assertTrue(self.app._validate_input(japanese_text))

    def test_qr_code_generation(self):
        """QRコード生成機能のテスト"""
        test_text = "テストQRコード"
        self.app.result_text.insert("1.0", test_text)
        self.app.generate_qr_code()

        # QRコードが生成されたことを確認
        self.assertIsNotNone(self.app.qr_image)
        self.assertEqual(self.app.status_var.get(), "QRコードを生成しました")

    def test_text_clear(self):
        """テキストクリア機能のテスト"""
        test_text = "クリアテスト"
        self.app.result_text.insert("1.0", test_text)
        self.app.clear_text()

        self.assertEqual(self.app.result_text.get("1.0", tk.END).strip(), "")
        self.assertEqual(self.app.status_var.get(), "テキストをクリアしました")

    def test_text_length_limit(self):
        """テキスト長制限のテスト"""
        # 制限を超えるテキスト
        long_text = "a" * 4001
        self.app.result_text.insert("1.0", long_text)
        self.app.generate_qr_code()

        # QRコードが生成されないことを確認
        self.assertFalse(self.app.show_qr_code)
        self.assertIsNone(self.app.qr_image)

    def test_save_qr_code(self):
        """QRコード保存機能のテスト"""
        with patch("tkinter.filedialog.asksaveasfilename") as mock_save:
            mock_save.return_value = "test.png"
            test_text = "保存テスト"
            self.app.result_text.insert("1.0", test_text)
            self.app.generate_qr_code()
            self.app.save_qr_code()

            self.assertEqual(self.app.status_var.get(), "QRコードを保存しました")

    def test_camera_return(self):
        """カメラ表示への戻り機能のテスト"""
        self.app.return_to_camera()
        self.assertFalse(self.app.show_qr_code)
        self.assertEqual(self.app.status_var.get(), "カメラ表示に戻りました")


if __name__ == "__main__":
    unittest.main()
