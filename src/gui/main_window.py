import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

from tkinter import ttk, scrolledtext
from src.core.file_manager import FileManager
from src.core.merger import FileMerger
from src.gui.widgets.folder_frame import FolderFrame
from src.gui.widgets.extensions import ExtensionsFrame
from src.gui.widgets.file_tree import FileTreeFrame
from src.gui.widgets.exclude_frame import ExcludeFrame
from src.gui.status_bar import StatusBar


class MainWindow:
    """메인 윈도우 클래스"""

    def __init__(self, master):
        self.master = master
        self.master.title("File Manager without CMD v1.0")
        self.master.geometry("1200x800")
        self.master.configure(bg="#f0f0f0")

        # 스타일 설정
        self._setup_styles()

        # 컴포넌트 생성
        self._create_widgets()

        # 상태바 생성
        self.status_bar = StatusBar(self.master)

        # 파일 관리자 (초기값 None)
        self.file_manager = None
        self.merger = None

    def _setup_styles(self):
        """스타일 설정"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 기본 스타일
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton',
                             background='#4a86e8',
                             foreground='white',
                             font=('Helvetica', 10))
        self.style.map('TButton',
                       background=[('active', '#619ff0')])
        self.style.configure('TLabel',
                             background='#f0f0f0',
                             font=('Helvetica', 10))
        self.style.configure('TEntry',
                             font=('Helvetica', 10))

        # 체크박스 스타일
        self.style.configure("Transparent.TCheckbutton",
                             background="#f0f0f0")

        # 작은 버튼 스타일
        self.style.configure('Small.TButton',
                             font=('Helvetica', 8))

    def _create_widgets(self):
        """위젯 생성 및 배치"""
        # 메인 프레임
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 폴더 선택 프레임
        self.folder_frame = FolderFrame(main_frame, self._on_folder_select)

        # 하단 프레임 (좌우 분할)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.rowconfigure(0, weight=1)

        # 왼쪽 프레임
        left_frame = ttk.Frame(bottom_frame, width=250)
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.grid_propagate(False)

        # 오른쪽 출력 영역을 먼저 생성
        self.output_frame = ttk.Frame(bottom_frame)
        self.output_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.output = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)

        # 트리 버튼 영역 (output 전달)
        self.file_tree = FileTreeFrame(left_frame, self.output)
        self.file_tree.pack(fill=tk.X, pady=(0, 10))

        # 확장자 선택 영역
        self.extensions_frame = ExtensionsFrame(
            left_frame,
            self._on_extension_selection_change
        )
        self.extensions_frame.pack(fill=tk.BOTH, expand=True)

        # 제외 설정 영역
        self.exclude_frame = ExcludeFrame(left_frame)
        self.exclude_frame.pack(fill=tk.X)

        # 병합 버튼
        self.merge_button = ttk.Button(
            left_frame,
            text="파일 병합",
            command=self._merge_files
        )
        self.merge_button.pack(fill=tk.X, pady=(5, 0))

    def _on_folder_select(self, folder_path: str):
        """폴더 선택 시 호출되는 콜백

        Args:
            folder_path (str): 선택된 폴더 경로
        """
        if not folder_path:
            return

        # 파일 관리자 초기화
        self.file_manager = FileManager(folder_path)
        self.merger = FileMerger(folder_path)

        # 파일 트리 초기화
        self.file_tree.initialize(folder_path)

        # 제외 프레임 초기화
        self.exclude_frame.set_base_folder(folder_path)

        # 확장자 분석 및 업데이트
        extensions, has_no_extension = self.file_manager.analyze_extensions()
        self.extensions_frame.update_extensions(extensions, has_no_extension)

        # 상태바 업데이트
        self.status_bar.update_status(folder_path)

    def _on_extension_selection_change(self):
        """확장자 선택 변경 시 호출되는 콜백"""
        folder_path = self.folder_frame.folder_path.get()
        selected_extensions = self.extensions_frame.get_selected_extensions()
        self.status_bar.update_status(folder_path, selected_extensions)

    def _merge_files(self):
        """파일 병합 실행"""
        if not self.merger:
            messagebox.showwarning("경고", "폴더를 선택해주세요.")
            return

        selected_extensions = self.extensions_frame.get_selected_extensions()
        if not selected_extensions:
            messagebox.showwarning("경고", "병합할 파일 확장자를 선택해주세요.")
            return

        exclude_files, exclude_folders = self.exclude_frame.get_exclude_lists()

        output_path = self.merger.merge_files(
            selected_extensions,
            exclude_files,
            exclude_folders
        )

        if output_path:
            self.file_tree.update_output(
                f"병합된 파일이 {output_path}에 저장되었습니다."
            )
            self.status_bar.update_status(
                self.folder_frame.folder_path.get(),
                selected_extensions
            )
        else:
            messagebox.showerror("오류", "파일 병합 중 오류가 발생했습니다.")