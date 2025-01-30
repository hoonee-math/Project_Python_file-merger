import tkinter as tk
from tkinter import ttk
import os
from typing import List, Optional, Tuple
from pathlib import Path


class StatusBar(ttk.Frame):
    """상태바 클래스"""

    def __init__(self, master):
        """초기화

        Args:
            master: 부모 위젯
        """
        super().__init__(master, relief=tk.SUNKEN, padding=(2, 2))

        # UI 초기화
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """위젯 생성"""
        # 왼쪽 상태 텍스트 (파일/폴더 수 표시)
        self._status_left = ttk.Label(self, anchor=tk.W)

        # 오른쪽 상태 텍스트 (GitHub 링크)
        self._status_right = ttk.Label(
            self,
            text="GitHub: hoonee-math",
            anchor=tk.E
        )

    def _setup_layout(self) -> None:
        """레이아웃 설정"""
        # 레이블 배치
        self._status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._status_right.pack(side=tk.RIGHT)

        # 프레임을 윈도우 하단에 배치
        self.pack(side=tk.BOTTOM, fill=tk.X)

    def _count_files_and_folders(self,
                                 folder_path: str,
                                 selected_extensions: Optional[List[str]] = None) -> Tuple[int, int]:
        """파일과 폴더 수 계산

        Args:
            folder_path (str): 폴더 경로
            selected_extensions (Optional[List[str]], optional): 선택된 확장자 목록. Defaults to None.

        Returns:
            Tuple[int, int]: (파일 수, 폴더 수)
        """
        try:
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

            return file_count, folder_count
        except Exception:
            return 0, 0

    def _format_status_text(self, file_count: int, folder_count: int) -> str:
        """상태 텍스트 포맷팅

        Args:
            file_count (int): 파일 수
            folder_count (int): 폴더 수

        Returns:
            str: 포맷팅된 상태 텍스트
        """
        return f"선택된 파일: {file_count}개, 폴더: {folder_count}개"

    # Public Interface Methods
    def update_status(self, folder_path: Optional[str] = None,
                      selected_extensions: Optional[List[str]] = None) -> None:
        """상태 정보 업데이트

        Args:
            folder_path (Optional[str], optional): 선택된 폴더 경로. Defaults to None.
            selected_extensions (Optional[List[str]], optional): 선택된 확장자 목록. Defaults to None.
        """
        if not folder_path:
            self._status_left.config(text="폴더를 선택해주세요")
            return

        file_count, folder_count = self._count_files_and_folders(
            folder_path,
            selected_extensions
        )
        status_text = self._format_status_text(file_count, folder_count)
        self._status_left.config(text=status_text)

    def show_message(self, message: str) -> None:
        """임시 메시지 표시

        Args:
            message (str): 표시할 메시지
        """
        self._status_left.config(text=message)

    def clear_status(self) -> None:
        """상태바 초기화"""
        self._status_left.config(text="")