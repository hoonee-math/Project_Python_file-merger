import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
from typing import Tuple, List, Optional
from pathlib import Path


class ExcludeFrame(ttk.Frame):
    """파일/폴더 제외 설정을 위한 프레임 클래스"""

    def __init__(self, master):
        """초기화

        Args:
            master: 부모 위젯
        """
        super().__init__(master)
        self._base_folder: Optional[Path] = None

        # UI 초기화
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self) -> None:
        """위젯 생성"""
        # 제목 프레임
        self._title_frame = ttk.Frame(self)
        self._title_label = ttk.Label(self._title_frame, text="병합에서 제외할 파일/폴더")

        # 버튼 생성
        button_font = font.Font(size=8)
        self._file_button = ttk.Button(
            self._title_frame,
            text="📄",
            command=self._add_exclude_file,
            width=3,
            style='Small.TButton'
        )
        self._folder_button = ttk.Button(
            self._title_frame,
            text="📁",
            command=self._add_exclude_folder,
            width=3,
            style='Small.TButton'
        )

        # 텍스트 영역
        self._exclude_text = tk.Text(self, height=4, wrap=tk.WORD)

    def _setup_layout(self) -> None:
        """레이아웃 설정"""
        # 제목 프레임 레이아웃
        self._title_frame.pack(fill=tk.X, pady=(10, 5))
        self._title_label.pack(side=tk.LEFT)

        # 버튼 레이아웃
        self._file_button.pack(side=tk.RIGHT, padx=(2, 0))
        self._folder_button.pack(side=tk.RIGHT, padx=(2, 0))

        # 텍스트 영역 레이아웃
        self._exclude_text.pack(fill=tk.X, pady=(5, 10))

    def _check_base_folder(self) -> bool:
        """기본 폴더 설정 여부 확인

        Returns:
            bool: 기본 폴더가 설정되어 있으면 True
        """
        if not self._base_folder:
            messagebox.showwarning("경고", "폴더를 먼저 선택해주세요.")
            return False
        return True

    def _add_text_entry(self, new_text: str) -> None:
        """텍스트 영역에 새 항목 추가

        Args:
            new_text (str): 추가할 텍스트
        """
        current = self._exclude_text.get("1.0", tk.END).strip()
        if current:
            self._exclude_text.insert(tk.END, f"\n{new_text}")
        else:
            self._exclude_text.insert(tk.END, new_text)

    def _add_exclude_file(self) -> None:
        """제외할 파일 추가"""
        if not self._check_base_folder():
            return

        try:
            file_path = filedialog.askopenfilename(initialdir=self._base_folder)
            if file_path:
                file_name = Path(file_path).name
                self._add_text_entry(file_name)
        except Exception as e:
            messagebox.showerror("오류", f"파일 추가 중 오류 발생: {str(e)}")

    def _add_exclude_folder(self) -> None:
        """제외할 폴더 추가"""
        if not self._check_base_folder():
            return

        try:
            folder_path = filedialog.askdirectory(initialdir=self._base_folder)
            if folder_path and self._base_folder:
                try:
                    relative_path = Path(folder_path).relative_to(self._base_folder)
                    relative_path_str = str(relative_path).replace('\\', '/')
                    self._add_text_entry(f"/{relative_path_str}")
                except ValueError:
                    messagebox.showwarning("경고", "선택한 폴더가 기본 폴더 외부에 있습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"폴더 추가 중 오류 발생: {str(e)}")

    def _parse_exclude_lists(self, text: str) -> Tuple[List[str], List[str]]:
        """제외 목록 파싱

        Args:
            text (str): 파싱할 텍스트

        Returns:
            Tuple[List[str], List[str]]: (제외할 파일 목록, 제외할 폴더 목록)
        """
        if not text:
            return [], []

        items = [item.strip() for item in text.split('\n') if item.strip()]
        exclude_files = [item for item in items if not item.startswith('/')]
        exclude_folders = [item[1:] for item in items if item.startswith('/')]
        return exclude_files, exclude_folders

    # Public Interface Methods
    def set_base_folder(self, folder_path: str) -> None:
        """기준 폴더 설정

        Args:
            folder_path (str): 기준 폴더 경로
        """
        self._base_folder = Path(folder_path) if folder_path else None

    def get_exclude_lists(self) -> Tuple[List[str], List[str]]:
        """제외 목록 반환

        Returns:
            Tuple[List[str], List[str]]: (제외할 파일 목록, 제외할 폴더 목록)
        """
        try:
            text = self._exclude_text.get("1.0", tk.END).strip()
            return self._parse_exclude_lists(text)
        except Exception as e:
            messagebox.showerror("오류", f"제외 목록 처리 중 오류 발생: {str(e)}")
            return [], []

    def clear_exclude_lists(self) -> None:
        """제외 목록 초기화"""
        self._exclude_text.delete("1.0", tk.END)