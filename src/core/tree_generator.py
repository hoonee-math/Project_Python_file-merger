from typing import Generator, Optional, List
from pathlib import Path
import os
from .gitignore_parser import GitignoreParser
from src.core.file_manager import FileManager

class TreeGenerator:
    """파일 트리 구조를 생성하는 클래스"""

    def __init__(self, root_path: str, file_manager: FileManager):
        self.root_path = Path(root_path)
        self.file_manager = file_manager

    def generate_ascii_tree(self,
                            allowed_extensions: Optional[List[str]] = None,
                            exclude_files: Optional[List[str]] = None,
                            exclude_folders: Optional[List[str]] = None) -> str:
        """ASCII 아트 형식의 트리 구조를 생성

        Args:
            allowed_extensions (Optional[List[str]], optional): 허용할 확장자 목록
            exclude_files (Optional[List[str]], optional): 제외할 파일 목록
            exclude_folders (Optional[List[str]], optional): 제외할 폴더 목록

        Returns:
            str: 생성된 트리 구조 문자열
        """
        tree_content = self._walk(
            self.root_path,
            allowed_extensions,
            exclude_files or [],
            exclude_folders or []
        )
        return "\n".join(tree_content)

    def _walk(self,
              path: Path,
              allowed_extensions: Optional[List[str]],
              exclude_files: List[str],
              exclude_folders: List[str],
              prefix: str = "",
              is_last: bool = False) -> Generator[str, None, None]:
        """재귀적으로 디렉토리를 순회하며 트리 구조를 생성

        Args:
            path (Path): 현재 경로
            allowed_extensions (Optional[List[str]]): 허용할 확장자 목록
            exclude_files (List[str]): 제외할 파일 목록
            exclude_folders (List[str]): 제외할 폴더 목록
            prefix (str, optional): 현재 깊이의 접두사
            is_last (bool, optional): 현재 항목이 마지막인지 여부

        Yields:
            Generator[str, None, None]: 트리 구조의 각 줄
        """
        # .gitignore 규칙 확인
        if self.file_manager.should_ignore(str(path)):
            return

        # 제외 폴더 확인
        rel_path = path.relative_to(self.root_path)
        str_rel_path = str(rel_path).replace('\\', '/')
        if any(str_rel_path.startswith(f) for f in exclude_folders):
            return

        entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
        entries = [e for e in entries if not self.file_manager.should_ignore(e.path)]

        if not entries:
            return

        for i, entry in enumerate(entries):
            is_last_entry = (i == len(entries) - 1)

            # 파일인 경우 확장자 확인
            if not entry.is_dir():
                if entry.name in exclude_files:
                    continue

                _, ext = os.path.splitext(entry.name)
                if allowed_extensions is not None:
                    if not (ext in allowed_extensions or (ext == '' and 'No Extension' in allowed_extensions)):
                        continue

            # 현재 항목의 라인 생성
            connector = "└─" if is_last_entry else "├─"
            icon = "📁" if entry.is_dir() else "📄"
            yield f"{prefix}{connector}{icon} {entry.name}{'/' if entry.is_dir() else ''}"

            # 디렉토리인 경우 재귀 호출
            if entry.is_dir():
                # 새로운 prefix 계산
                new_prefix = prefix + ("   " if is_last_entry else "│  ")
                yield from self._walk(
                    Path(entry.path),
                    allowed_extensions,
                    exclude_files,
                    exclude_folders,
                    new_prefix,
                    is_last_entry
                )

                # 마지막 항목이 아닐 경우 구분선 추가
                if not is_last_entry:
                    yield prefix + "│"