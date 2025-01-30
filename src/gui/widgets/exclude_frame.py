import tkinter as tk
from tkinter import ttk, filedialog, font
from typing import Tuple, List
from pathlib import Path


class ExcludeFrame(ttk.Frame):
    """파일/폴더 제외 설정을 위한 프레임 클래스"""

    def __init__(self, master):
        super().__init__(master)
        self.base_folder: Path = None

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성 및 배치"""
        # 제목 프레임
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, pady=(10, 5))

        ttk.Label(title_frame, text="병합에서 제외할 파일/폴더").pack(side=tk.LEFT)

        # 버튼 아이콘 폰트 설정
        button_font = font.Font(size=8)

        # 파일 선택 버튼
        ttk.Button(
            title_frame,
            text="📄",
            command=self._add_exclude_file,
            width=3,
            style='Small.TButton'
        ).pack(side=tk.RIGHT, padx=(2, 0))

        # 폴더 선택 버튼
        ttk.Button(
            title_frame,
            text="📁",
            command=self._add_exclude_folder,
            width=3,
            style='Small.TButton'
        ).pack(side=tk.RIGHT, padx=(2, 0))

        # 텍스트 영역
        self.exclude_text = tk.Text(self, height=4, wrap=tk.WORD)
        self.exclude_text.pack(fill=tk.X, pady=(5, 10))

    def set_base_folder(self, folder_path: str):
        """기준 폴더 설정

        Args:
            folder_path (str): 기준 폴더 경로
        """
        self.base_folder = Path(folder_path) if folder_path else None

    def _add_exclude_file(self):
        """제외할 파일 추가"""
        if not self.base_folder:
            return

        file_path = filedialog.askopenfilename(initialdir=self.base_folder)
        if file_path:
            file_name = Path(file_path).name
            current = self.exclude_text.get("1.0", tk.END).strip()
            new_line = f"\n{file_name}" if current else file_name
            self.exclude_text.insert(tk.END, new_line)

    def _add_exclude_folder(self):
        """제외할 폴더 추가"""
        if not self.base_folder:
            return

        folder_path = filedialog.askdirectory(initialdir=self.base_folder)
        if folder_path and self.base_folder:
            try:
                relative_path = Path(folder_path).relative_to(self.base_folder)
                relative_path_str = str(relative_path).replace('\\', '/')

                current = self.exclude_text.get("1.0", tk.END).strip()
                new_line = f"\n/{relative_path_str}" if current else f"/{relative_path_str}"
                self.exclude_text.insert(tk.END, new_line)

            except ValueError:
                from tkinter import messagebox
                messagebox.showwarning("경고", "선택한 폴더가 기본 폴더 외부에 있습니다.")

    def get_exclude_lists(self) -> Tuple[List[str], List[str]]:
        """제외 목록 반환

        Returns:
            Tuple[List[str], List[str]]: (제외할 파일 목록, 제외할 폴더 목록)
        """
        text = self.exclude_text.get("1.0", tk.END).strip()
        if not text:
            return [], []

        items = [item.strip() for item in text.split('\n') if item.strip()]
        exclude_files = [item for item in items if not item.startswith('/')]
        exclude_folders = [item[1:] for item in items if item.startswith('/')]

        return exclude_files, exclude_folders