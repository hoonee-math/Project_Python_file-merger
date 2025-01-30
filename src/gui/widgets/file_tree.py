import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, List
import subprocess
from src.core.tree_generator import TreeGenerator


class FileTreeFrame(ttk.Frame):
    """파일 트리 표시 및 제어를 위한 프레임 클래스"""

    def __init__(self, master):
        super().__init__(master, padding="10")

        # 트리 생성기 (초기값 None)
        self.tree_generator: TreeGenerator = None

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성 및 배치"""
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # 버튼 영역
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, sticky="ew")

        # 기본 구조 출력 섹션
        ttk.Label(button_frame, text="기본 구조 출력", anchor="w").pack(
            fill=tk.X, pady=(0, 5))

        commands = [
            ("파일 트리 리스트", self.ps_tree),
            ("파일 트리 그래프", self.cmd_tree),
        ]

        for text, command in commands:
            ttk.Button(button_frame, text=text, command=command).pack(
                fill=tk.X, pady=(0, 5))

        # 커스텀 구조 출력 섹션
        ttk.Label(button_frame, text="커스텀 구조 출력", anchor="w").pack(
            fill=tk.X, pady=(10, 5))

        commands = [
            ("파일 트리 리스트 (커스텀)", self.ps_tree_extensions),
            ("파일 트리 그래프 (커스텀)", self.custom_tree),
        ]

        for text, command in commands:
            ttk.Button(button_frame, text=text, command=command).pack(
                fill=tk.X, pady=(0, 5))

        # 출력 영역
        self.output = scrolledtext.ScrolledText(self, wrap=tk.WORD)
        self.output.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

    def initialize(self, root_path: str):
        """트리 생성기 초기화

        Args:
            root_path (str): 루트 디렉토리 경로
        """
        self.tree_generator = TreeGenerator(root_path)

    def clear_output(self):
        """출력 영역 초기화"""
        self.output.delete(1.0, tk.END)

    def update_output(self, text: str):
        """출력 영역 업데이트

        Args:
            text (str): 표시할 텍스트
        """
        self.clear_output()
        self.output.insert(tk.END, text)

    def run_command(self, command: str):
        """시스템 명령어 실행

        Args:
            command (str): 실행할 명령어
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True
            )
            self.clear_output()
            self.output.insert(tk.END, result.stdout)
            if result.stderr:
                self.output.insert(tk.END, f"\nErrors:\n{result.stderr}")
        except Exception as e:
            self.clear_output()
            self.output.insert(tk.END, f"Error: {str(e)}")

    def cmd_tree(self):
        """CMD tree 명령어로 트리 구조 출력"""
        if not self.tree_generator:
            return
        command = f'tree "{self.tree_generator.root_path}" /F'
        self.run_command(command)

    def ps_tree(self):
        """PowerShell로 트리 구조 출력"""
        if not self.tree_generator:
            return
        command = f'powershell "Get-ChildItem -Path \'{self.tree_generator.root_path}\' -Recurse | Select-Object FullName"'
        self.run_command(command)

    def ps_tree_extensions(self, extensions: List[str] = None):
        """PowerShell로 선택된 확장자의 파일만 출력

        Args:
            extensions (List[str], optional): 표시할 확장자 목록. Defaults to None.
        """
        if not self.tree_generator:
            return

        if not extensions:
            self.ps_tree()
            return

        extension_filter = ','.join(f'*{ext}' for ext in extensions)
        command = f'powershell "Get-ChildItem -Path \'{self.tree_generator.root_path}\' -Recurse -Include {extension_filter} | Select-Object FullName"'
        self.run_command(command)

    def custom_tree(self, allowed_extensions: List[str] = None, exclude_files: List[str] = None,
                    exclude_folders: List[str] = None):
        """커스텀 트리 구조 출력

        Args:
            allowed_extensions (List[str], optional): 표시할 확장자 목록. Defaults to None.
            exclude_files (List[str], optional): 제외할 파일 목록. Defaults to None.
            exclude_folders (List[str], optional): 제외할 폴더 목록. Defaults to None.
        """
        if not self.tree_generator:
            return

        tree = self.tree_generator.generate_ascii_tree(
            allowed_extensions,
            exclude_files,
            exclude_folders
        )
        self.update_output(tree)