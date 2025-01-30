import tkinter as tk
from tkinter import ttk
import os
from typing import List


class StatusBar(ttk.Frame):
    """상태바 클래스"""

    def __init__(self, master):
        super().__init__(master, relief=tk.SUNKEN, padding=(2, 2))

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성 및 배치"""
        # 왼쪽 상태 텍스트 (파일/폴더 수 표시)
        self.status_left = ttk.Label(self, anchor=tk.W)
        self.status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 오른쪽 상태 텍스트 (GitHub 링크)
        self.status_right = ttk.Label(
            self,
            text="GitHub: hoonee-math",
            anchor=tk.E
        )
        self.status_right.pack(side=tk.RIGHT)

        # 프레임을 윈도우 하단에 배치
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, folder_path: str = None, selected_extensions: List[str] = None):
        """상태 정보 업데이트

        Args:
            folder_path (str, optional): 선택된 폴더 경로. Defaults to None.
            selected_extensions (List[str], optional): 선택된 확장자 목록. Defaults to None.
        """
        if not folder_path:
            self.status_left.config(text="폴더를 선택해주세요")
            return

        file_count = 0
        folder_count = 0

        for root, dirs, files in os.walk(folder_path):
            folder_count += len(dirs)

            if selected_extensions:
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext in selected_extensions or (ext == '' and "No Extension" in selected_extensions):
                        file_count += 1
            else:
                file_count += len(files)

        status_text = f"선택된 파일: {file_count}개, 폴더: {folder_count}개"
        self.status_left.config(text=status_text)