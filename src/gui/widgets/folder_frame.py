import tkinter as tk
from tkinter import ttk, filedialog
import platform
import subprocess
import os
from typing import Callable


class FolderFrame(ttk.Frame):
    """폴더 선택 및 관리를 위한 프레임 클래스"""

    def __init__(self, master, on_folder_select: Callable[[str], None]):
        """
        Args:
            master: 부모 위젯
            on_folder_select (Callable[[str], None]): 폴더 선택 시 호출될 콜백
        """
        super().__init__(master, padding="10")
        self.on_folder_select = on_folder_select

        # 경로 저장 변수
        self.folder_path = tk.StringVar()
        self.folder_path.trace_add('write', self._on_path_change)

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성 및 배치"""
        self.pack(fill=tk.X, pady=(0, 0))

        # 폴더 경로 레이블
        ttk.Label(self, text="폴더 경로:").pack(side=tk.LEFT)

        # 폴더 경로 입력 필드
        ttk.Entry(self, textvariable=self.folder_path, width=50).pack(
            side=tk.LEFT, padx=(5, 10))

        # 폴더 선택 버튼
        ttk.Button(self, text="폴더 선택",
                   command=self._select_folder).pack(side=tk.LEFT)

        # 폴더 열기 버튼
        ttk.Button(self, text="폴더 열기",
                   command=self._open_folder).pack(side=tk.LEFT, padx=(10, 0))

        # 홈페이지 바로가기 버튼
        ttk.Button(self, text="홈페이지 바로가기",
                   command=self._open_website,
                   width=15,
                   style='Small.TButton').pack(side=tk.RIGHT, padx=(10, 2))

    def _select_folder(self):
        """폴더 선택 다이얼로그 표시"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    def _open_folder(self):
        """선택된 폴더를 파일 탐색기로 열기"""
        folder = self.folder_path.get()
        if folder and os.path.exists(folder):
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder])
            else:  # Linux and other Unix-like
                subprocess.Popen(["xdg-open", folder])

    def _open_website(self):
        """홈페이지 열기"""
        import webbrowser
        webbrowser.open('https://hoonee-math.github.io/web/')

    def _on_path_change(self, *args):
        """경로 변경 시 콜백 호출"""
        self.on_folder_select(self.folder_path.get())