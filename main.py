#!/usr/bin/env python3
"""
File Manager Application

파일 시스템 탐색, 파일 병합, 트리 구조 시각화를 위한 GUI 애플리케이션
"""

import sys
import tkinter as tk
from pathlib import Path
from typing import Optional

from src.gui.main_window import MainWindow


class Application:
    """애플리케이션 메인 클래스"""

    def __init__(self):
        """애플리케이션 초기화"""
        self.root: Optional[tk.Tk] = None
        self.app: Optional[MainWindow] = None

    def _setup_root(self) -> None:
        """루트 윈도우 설정"""
        self.root = tk.Tk()

        # 윈도우 아이콘 설정
        icon_path = Path(__file__).parent / 'resources' / 'icons' / 'hoonee_math_icon.ico'
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        # DPI 스케일링 처리
        if sys.platform.startswith('win'):
            try:
                from ctypes import windll
                windll.shcore.SetProcessDpiAwareness(1)
            except Exception:
                pass  # DPI 설정 실패는 무시

    def _setup_exception_handler(self) -> None:
        """전역 예외 처리기 설정"""

        def handle_exception(exc_type, exc_value, exc_traceback):
            """처리되지 않은 예외 처리"""
            import traceback
            from tkinter import messagebox

            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            messagebox.showerror('오류 발생',
                                 f'예상치 못한 오류가 발생했습니다:\n\n{str(exc_value)}\n\n' +
                                 '자세한 내용은 콘솔을 확인해주세요.')
            print(f'\n{"=" * 50}\n예상치 못한 오류 발생:\n{error_msg}{"=" * 50}\n',
                  file=sys.stderr)

        sys.excepthook = handle_exception

    def run(self) -> None:
        """애플리케이션 실행"""
        try:
            self._setup_root()
            self._setup_exception_handler()

            # 메인 윈도우 생성
            self.app = MainWindow(self.root)

            # 메인 루프 시작
            self.root.mainloop()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror('시작 오류',
                                 f'애플리케이션 시작 중 오류가 발생했습니다:\n{str(e)}')
            raise


def main():
    """애플리케이션 시작점"""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()