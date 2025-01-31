import tkinter as tk
from tkinter import ttk
from typing import List, Optional
from src.core.tree_generator import TreeGenerator
from src.core.command_executor import CommandExecutor

class FileTreeFrame:
    def __init__(self, output):
        self._output = output
        self._tree_generator = None
        self._command_executor = None

    def set_use_gitignore(self, use_gitignore: bool) -> None:
        """gitignore 규칙 적용 여부 설정"""
        if self._tree_generator:
            self._tree_generator.file_manager.set_use_gitignore(use_gitignore)
        if self._command_executor:
            self._command_executor.set_use_gitignore(use_gitignore)

    def initialize(self, root_path: str) -> None:
        """트리 생성기와 명령어 실행기 초기화"""
        self._tree_generator = TreeGenerator(root_path)
        self._command_executor = CommandExecutor(root_path)

    def ps_tree(self) -> None:
        """PowerShell 트리 출력"""
        if self._command_executor:
            stdout, stderr = self._command_executor.ps_tree()
            if stderr:
                self._show_error(stderr)
            else:
                self._show_output(stdout)

    def cmd_tree(self) -> None:
        """CMD 트리 출력"""
        if self._command_executor:
            stdout, stderr = self._command_executor.cmd_tree()
            if stderr:
                self._show_error(stderr)
            else:
                self._show_output(stdout)

    def ps_tree_extensions(self, extensions: List[str] = None) -> None:
        """확장자 기반 PowerShell 트리 출력"""
        if self._command_executor:
            stdout, stderr = self._command_executor.ps_tree_extensions(extensions)
            if stderr:
                self._show_error(stderr)
            else:
                self._show_output(stdout)

    def custom_tree(self, allowed_extensions: List[str] = None) -> None:
        """커스텀 트리 출력"""
        if self._tree_generator:
            tree = self._tree_generator.generate_ascii_tree(allowed_extensions)
            self._show_output(tree)

    def _show_output(self, text: str) -> None:
        """출력 표시"""
        self._output.delete(1.0, tk.END)
        self._output.insert(tk.END, text)

    def _show_error(self, error_message: str) -> None:
        """에러 메시지 표시"""
        self._output.delete(1.0, tk.END)
        self._output.insert(tk.END, f"Error: {error_message}")