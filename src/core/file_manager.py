from pathlib import Path
from typing import Set, List, Tuple, Optional
import os
from src.utils.helpers import normalize_path, get_file_extension
from .gitignore_parser import GitignoreParser


class FileManager:
    """파일 시스템 작업을 처리하는 클래스"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.gitignore_parser = GitignoreParser(root_path)

    def analyze_extensions(self) -> Tuple[Set[str], bool]:
        """디렉토리 내의 모든 파일 확장자를 분석

        Returns:
            Tuple[Set[str], bool]: (확장자 집합, 확장자 없는 파일 존재 여부)
        """
        extensions = set()
        has_no_extension = False

        for root, _, files in os.walk(self.root_path):
            # .gitignore 규칙 확인
            if self.gitignore_parser.should_ignore(root):
                continue

            for file in files:
                file_path = os.path.join(root, file)
                if self.gitignore_parser.should_ignore(file_path):
                    continue

                _, ext = os.path.splitext(file)
                if ext:
                    extensions.add(ext)
                else:
                    has_no_extension = True

        return extensions, has_no_extension

    def get_file_list(self,
                      extensions: Optional[List[str]] = None,
                      exclude_files: Optional[List[str]] = None,
                      exclude_folders: Optional[List[str]] = None) -> List[Tuple[str, bool]]:
        """조건에 맞는 파일 목록을 반환

        Args:
            extensions (Optional[List[str]], optional): 포함할 확장자 목록
            exclude_files (Optional[List[str]], optional): 제외할 파일 목록
            exclude_folders (Optional[List[str]], optional): 제외할 폴더 목록

        Returns:
            List[Tuple[str, bool]]: (파일 경로, 디렉토리 여부) 목록
        """
        result = []
        exclude_files = set(exclude_files or [])
        exclude_folders = set(exclude_folders or [])

        for root, dirs, files in os.walk(self.root_path):
            # .gitignore 규칙 확인
            if self.gitignore_parser.should_ignore(root):
                continue

            rel_path = Path(root).relative_to(self.root_path)
            str_rel_path = str(rel_path).replace('\\', '/')

            # 제외 폴더 확인
            if any(str_rel_path.startswith(f) for f in exclude_folders):
                continue

            # 디렉토리 추가
            if str_rel_path != '.':
                result.append((normalize_path(root), True))

            # 파일 추가
            for file in files:
                if file in exclude_files:
                    continue

                file_path = os.path.join(root, file)
                if self.gitignore_parser.should_ignore(file_path):
                    continue

                if extensions:
                    ext = get_file_extension(file)
                    if ext not in extensions and not (ext == '' and 'No Extension' in extensions):
                        continue

                result.append((normalize_path(file_path), False))

        return sorted(result, key=lambda x: (not x[1], x[0].lower()))

    def read_file_content(self, file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """파일 내용을 읽어서 반환

        Args:
            file_path (str): 파일 경로
            encoding (str, optional): 인코딩. Defaults to 'utf-8'.

        Returns:
            Optional[str]: 파일 내용, 실패시 None
        """
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            return None

    def write_file(self, file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """파일에 내용을 기록

        Args:
            file_path (str): 파일 경로
            content (str): 기록할 내용
            encoding (str, optional): 인코딩. Defaults to 'utf-8'.

        Returns:
            bool: 성공 여부
        """
        try:
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception:
            return False