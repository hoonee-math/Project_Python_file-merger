import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Optional
from src.core.tree_generator import TreeGenerator
from src.core.command_executor import CommandExecutor


class FileTreeFrame(ttk.Frame):
    """파일 트리 표시 및 제어를 위한 프레임 클래스"""

    def __init__(self, master, output):
        """초기화

        Args:
            master: 부모 위젯
            output: 출력 영역 위젯
        """
        super().__init__(master, padding="10")

        # 핵심 컴포넌트 (초기값 None)
        self._tree_generator: Optional[TreeGenerator] = None
        self._command_executor: Optional[CommandExecutor] = None
        self._output = output  # 출력 영역 저장

        # UI 초기화
        self._create_widgets()

    def initialize(self, root_path: str) -> None:
        """트리 생성기와 명령어 실행기 초기화

        Args:
            root_path (str): 루트 디렉토리 경로
        """
        try:
            self._tree_generator = TreeGenerator(root_path)
            self._command_executor = CommandExecutor(root_path)
        except Exception as e:
            self._show_error(f"초기화 중 오류 발생: {str(e)}")

    def _create_widgets(self) -> None:
        """위젯 생성"""
        # 기본 구조 섹션
        ttk.Label(self, text="기본 구조 출력", anchor="w").pack(fill=tk.X, pady=(0, 5))

        commands = [
            ("파일 트리 리스트", self._ps_tree),
            ("파일 트리 그래프", self._cmd_tree),
        ]

        for text, command in commands:
            ttk.Button(self, text=text, command=command).pack(fill=tk.X, pady=(0, 5))

        # 커스텀 구조 섹션
        ttk.Label(self, text="커스텀 구조 출력", anchor="w").pack(fill=tk.X, pady=(10, 5))

        commands = [
            ("파일 트리 리스트 (커스텀)", self._ps_tree_extensions),
            ("파일 트리 그래프 (커스텀)", self._custom_tree),
        ]

        for text, command in commands:
            ttk.Button(self, text=text, command=command).pack(fill=tk.X, pady=(0, 5))

    def _show_output(self, text: str) -> None:
        """출력 영역에 텍스트 표시

        Args:
            text (str): 표시할 텍스트
        """
        self._output.delete(1.0, tk.END)
        self._output.insert(tk.END, text)

    def _show_error(self, error_message: str) -> None:
        """에러 메시지 표시

        Args:
            error_message (str): 에러 메시지
        """
        self._output.delete(1.0, tk.END)
        self._output.insert(tk.END, f"Error: {error_message}")

    def _create_command_buttons(self) -> None:
        """명령어 버튼 생성"""
        # 기본 구조 버튼
        commands = [
            ("파일 트리 리스트", self._ps_tree),
            ("파일 트리 그래프", self._cmd_tree),
        ]

        for text, command in commands:
            ttk.Button(self._button_frame, text=text, command=command).pack(
                fill=tk.X, pady=(0, 5))

        # 커스텀 구조 섹션
        ttk.Label(self._button_frame, text="커스텀 구조 출력", anchor="w").pack(
            fill=tk.X, pady=(10, 5))

        commands = [
            ("파일 트리 리스트 (커스텀)", self._ps_tree_extensions),
            ("파일 트리 그래프 (커스텀)", self._custom_tree),
        ]

        for text, command in commands:
            ttk.Button(self._button_frame, text=text, command=command).pack(
                fill=tk.X, pady=(0, 5))

    def _clear_output(self) -> None:
        """출력 영역 초기화"""
        self._output.delete(1.0, tk.END)

    def _show_output(self, text: str) -> None:
        """출력 영역에 텍스트 표시

        Args:
            text (str): 표시할 텍스트
        """
        self._clear_output()
        self._output.insert(tk.END, text)

    def _show_error(self, error_message: str) -> None:
        """에러 메시지 표시

        Args:
            error_message (str): 에러 메시지
        """
        self._clear_output()
        self._output.insert(tk.END, f"Error: {error_message}")

    def _check_initialization(self) -> bool:
        """초기화 상태 확인

        Returns:
            bool: 초기화 완료 여부
        """
        if not self._tree_generator or not self._command_executor:
            self._show_error("폴더를 선택해주세요.")
            return False
        return True

    def _cmd_tree(self) -> None:
        """CMD tree 명령어로 트리 구조 출력"""
        if not self._check_initialization():
            return

        try:
            stdout, stderr = self._command_executor.cmd_tree()
            if stderr:
                self._show_error(stderr)
            else:
                self._show_output(stdout)
        except Exception as e:
            self._show_error(str(e))

    def _ps_tree(self) -> None:
        """PowerShell로 트리 구조 출력"""
        if not self._check_initialization():
            return

        try:
            stdout, stderr = self._command_executor.ps_tree()
            if stderr:
                self._show_error(stderr)
            else:
                self._show_output(stdout)
        except Exception as e:
            self._show_error(str(e))

    def _ps_tree_extensions(self, extensions: Optional[List[str]] = None) -> None:
        """PowerShell로 선택된 확장자의 파일만 출력

        Args:
            extensions (Optional[List[str]], optional): 표시할 확장자 목록.
        """
        if not self._check_initialization():
            return

        try:
            stdout, stderr = self._command_executor.ps_tree_extensions(extensions)
            if stderr:
                self._show_error(stderr)
            else:
                self._show_output(stdout)
        except Exception as e:
            self._show_error(str(e))

    def _custom_tree(self, allowed_extensions: Optional[List[str]] = None,
                     exclude_files: Optional[List[str]] = None,
                     exclude_folders: Optional[List[str]] = None) -> None:
        """커스텀 트리 구조 출력

        Args:
            allowed_extensions (Optional[List[str]], optional): 표시할 확장자 목록
            exclude_files (Optional[List[str]], optional): 제외할 파일 목록
            exclude_folders (Optional[List[str]], optional): 제외할 폴더 목록
        """
        if not self._check_initialization():
            return

        try:
            tree = self._tree_generator.generate_ascii_tree(
                allowed_extensions,
                exclude_files,
                exclude_folders
            )
            self._show_output(tree)
        except Exception as e:
            self._show_error(str(e))

    # Public Interface Methods
    def update_output(self, text: str) -> None:
        """출력 영역 업데이트 (공개 메서드)

        Args:
            text (str): 표시할 텍스트
        """
        self._show_output(text)

    def custom_tree(self, allowed_extensions: Optional[List[str]] = None,
                    exclude_files: Optional[List[str]] = None,
                    exclude_folders: Optional[List[str]] = None) -> None:
        """커스텀 트리 구조 출력 (공개 메서드)

        Args:
            allowed_extensions (Optional[List[str]], optional): 표시할 확장자 목록
            exclude_files (Optional[List[str]], optional): 제외할 파일 목록
            exclude_folders (Optional[List[str]], optional): 제외할 폴더 목록
        """
        self._custom_tree(allowed_extensions, exclude_files, exclude_folders)