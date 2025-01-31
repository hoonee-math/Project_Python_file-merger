import subprocess
from pathlib import Path
from typing import Optional, List
from src.core.file_manager import FileManager
import platform
import os

class CommandExecutor:
    """시스템 명령어 실행을 처리하는 클래스"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.file_manager = FileManager(root_path)  # FileManager 추가

    def set_use_gitignore(self, use_gitignore: bool):
        """gitignore 규칙 적용 여부 설정"""
        self.file_manager.set_use_gitignore(use_gitignore)

    def execute_command(self, command: str) -> tuple[str, str]:
        """명령어 실행

        Args:
            command (str): 실행할 명령어

        Returns:
            tuple[str, str]: (표준 출력, 표준 에러)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True
            )
            return result.stdout, result.stderr
        except Exception as e:
            return "", str(e)

    def cmd_tree(self) -> tuple[str, str]:
        """CMD tree 명령어로 트리 구조 출력"""
        # .gitignore 적용된 파일 목록 가져오기
        file_list = self.file_manager.get_file_list()
        output = "\n".join([path for path, is_dir in file_list])
        return output, ""

    def ps_tree(self) -> tuple[str, str]:
        """PowerShell로 트리 구조 출력"""
        # .gitignore 적용된 파일 목록 가져오기
        file_list = self.file_manager.get_file_list()
        output = "\n".join([path for path, is_dir in file_list])
        return output, ""

    def ps_tree_extensions(self, extensions: Optional[List[str]] = None) -> tuple[str, str]:
        """PowerShell로 선택된 확장자의 파일만 출력"""
        # .gitignore 적용된 파일 목록 가져오기 (확장자 필터링)
        file_list = self.file_manager.get_file_list(extensions=extensions)
        output = "\n".join([path for path, is_dir in file_list])
        return output, ""

    def open_folder(self, folder_path: str) -> bool:
        """폴더를 시스템 파일 탐색기로 열기

        Args:
            folder_path (str): 열 폴더 경로

        Returns:
            bool: 성공 여부
        """
        try:
            if not os.path.exists(folder_path):
                return False

            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder_path])
            else:  # Linux and other Unix-like
                subprocess.Popen(["xdg-open", folder_path])
            return True
        except Exception:
            return False