import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
from typing import Callable, Optional
from pathlib import Path
from src.core.command_executor import CommandExecutor


class FolderFrame(ttk.Frame):
    """폴더 선택 및 관리를 위한 프레임 클래스"""

    def __init__(self, master, on_folder_select: Callable[[str], None]):
        """초기화

        Args:
            master: 부모 위젯
            on_folder_select (Callable[[str], None]): 폴더 선택 시 호출될 콜백
        """
        super().__init__(master, padding="10")

        # 콜백 함수
        self._on_folder_select_callback = on_folder_select

        # 명령어 실행기 (초기값 None)
        self._command_executor: Optional[CommandExecutor] = None

        # 경로 저장 변수
        self.folder_path = tk.StringVar()
        self.folder_path.trace_add('write', self._on_path_change)

        # UI 초기화
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """위젯 생성"""
        # 폴더 경로 레이블
        self._path_label = ttk.Label(self, text="폴더 경로:")

        # 폴더 경로 입력 필드
        self._path_entry = ttk.Entry(self, textvariable=self.folder_path, width=50)

        # 기능 버튼들
        self._select_button = ttk.Button(
            self,
            text="폴더 선택",
            command=self._select_folder
        )
        self._open_button = ttk.Button(
            self,
            text="폴더 열기",
            command=self._open_folder
        )
        self._web_button = ttk.Button(
            self,
            text="홈페이지 바로가기",
            command=self._open_website,
            width=15,
            style='Small.TButton'
        )

    def _setup_layout(self) -> None:
        """레이아웃 설정"""
        self.pack(fill=tk.X, pady=(0, 0))

        # 왼쪽 정렬 컴포넌트들
        self._path_label.pack(side=tk.LEFT)
        self._path_entry.pack(side=tk.LEFT, padx=(5, 10))
        self._select_button.pack(side=tk.LEFT)
        self._open_button.pack(side=tk.LEFT, padx=(10, 0))

        # 오른쪽 정렬 컴포넌트
        self._web_button.pack(side=tk.RIGHT, padx=(10, 2))

    def _select_folder(self) -> None:
        """폴더 선택 다이얼로그 표시"""
        try:
            folder = filedialog.askdirectory()
            if folder:
                self.folder_path.set(folder)
                self._command_executor = CommandExecutor(folder)
        except Exception as e:
            messagebox.showerror("오류", f"폴더 선택 중 오류 발생: {str(e)}")

    def _open_folder(self) -> None:
        """선택된 폴더를 파일 탐색기로 열기"""
        folder = self.folder_path.get()
        if not folder:
            messagebox.showwarning("경고", "폴더를 선택해주세요.")
            return

        if not self._command_executor:
            self._command_executor = CommandExecutor(folder)

        try:
            success = self._command_executor.open_folder(folder)
            if not success:
                messagebox.showerror("오류", "폴더를 열 수 없습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"폴더를 여는 중 오류 발생: {str(e)}")

    def _open_website(self) -> None:
        """홈페이지 열기"""
        try:
            webbrowser.open('https://hoonee-math.github.io/web/')
        except Exception as e:
            messagebox.showerror("오류", f"웹사이트를 여는 중 오류 발생: {str(e)}")

    def _on_path_change(self, *args) -> None:
        """경로 변경 시 호출되는 콜백"""
        try:
            path = self.folder_path.get()
            if path and Path(path).exists():
                self._on_folder_select_callback(path)
        except Exception as e:
            messagebox.showerror("오류", f"경로 변경 처리 중 오류 발생: {str(e)}")

    # Public Interface Methods
    def get_folder_path(self) -> str:
        """현재 선택된 폴더 경로 반환

        Returns:
            str: 폴더 경로
        """
        return self.folder_path.get()