from pathlib import Path
from typing import List, Optional, TextIO
from datetime import datetime
import os
from src.core.file_manager import FileManager
from src.utils.helpers import normalize_path, get_file_extension

class FileMerger:
    """파일 병합 기능을 처리하는 클래스"""

    def __init__(self, root_path: str, file_manager: FileManager):
        self.root_path = Path(root_path)
        self.file_manager = file_manager

    def merge_files(self,
                    selected_extensions: List[str],
                    exclude_files: Optional[List[str]] = None,
                    exclude_folders: Optional[List[str]] = None,
                    encoding: str = 'utf-8') -> Optional[str]:
        """선택된 파일들을 하나의 마크다운 파일로 병합

        Args:
            selected_extensions (List[str]): 병합할 파일 확장자 목록
            exclude_files (Optional[List[str]], optional): 제외할 파일 목록
            exclude_folders (Optional[List[str]], optional): 제외할 폴더 목록
            encoding (str, optional): 파일 인코딩. Defaults to 'utf-8'.

        Returns:
            Optional[str]: 생성된 파일 경로, 실패시 None
        """
        if not selected_extensions:
            return None

        # 출력 파일명 생성
        now = datetime.now()
        date_time = now.strftime("%y%m%d-%H%M")
        folder_name = self.root_path.name
        file_name = f"{date_time}-{folder_name}-merged.md"
        output_path = self.root_path / file_name

        try:
            with open(output_path, 'w', encoding=encoding) as outfile:
                self._write_directory_content(
                    self.root_path,
                    outfile,
                    selected_extensions,
                    exclude_files or [],
                    exclude_folders or [],
                    encoding
                )
            return str(output_path)
        except Exception:
            return None

    def _write_directory_content(self,
                                 directory: Path,
                                 outfile: TextIO,
                                 selected_extensions: List[str],
                                 exclude_files: List[str],
                                 exclude_folders: List[str],
                                 encoding: str,
                                 level: int = 0) -> None:
        """디렉토리 내용을 재귀적으로 파일에 기록"""
        # .gitignore 규칙 확인
        if self.file_manager.should_ignore(str(directory)):
            return

        # 경로 정규화 및 상대 경로 계산
        normalized_directory = normalize_path(directory)
        try:
            relative_directory = str(Path(directory).relative_to(self.root_path)).replace('\\', '/')
            # 제외 폴더 확인
            if any(relative_directory.startswith(folder) for folder in exclude_folders):
                return
        except ValueError:
            return

        # 디렉토리 헤더 작성
        outfile.write(f"{'#'} 디렉토리: {normalized_directory}\n\n")

        # 항목 정렬
        entries = sorted(os.scandir(directory), key=lambda e: (not e.is_dir(), e.name.lower()))

        for entry in entries:
            # .gitignore 규칙 확인
            if self.file_manager.should_ignore(entry.path):
                continue

            if entry.is_dir():
                # 재귀적으로 하위 디렉토리 처리 (제외 폴더가 아닌 경우에만)
                rel_path = str(Path(entry.path).relative_to(self.root_path)).replace('\\', '/')
                if not any(rel_path.startswith(folder) for folder in exclude_folders):
                    self._write_directory_content(
                        Path(entry.path),
                        outfile,
                        selected_extensions,
                        exclude_files,
                        exclude_folders,
                        encoding,
                        level + 1
                    )
            else:
                # 파일명이 제외 목록에 있는지 확인
                if entry.name in exclude_files:
                    # 제외된 파일은 이름만 표시
                    outfile.write(f"{'##'} 파일 (내용 생략됨): {normalize_path(entry.path)}\n\n")
                    continue

                # 파일 확장자 확인
                ext = get_file_extension(entry.name)
                if ext in selected_extensions or (ext == '' and 'No Extension' in selected_extensions):
                    # 파일 내용 포함
                    outfile.write(f"{'##'} 파일: {normalize_path(entry.path)}\n")
                    try:
                        with open(entry.path, 'r', encoding=encoding) as infile:
                            content = infile.read()
                        outfile.write(f"```{ext[1:] if ext else ''}\n")  # 확장자에 따른 코드 블록
                        outfile.write(content)
                        outfile.write("\n```\n\n")
                    except UnicodeDecodeError:
                        outfile.write(f"(이 파일은 {encoding} 인코딩으로 읽을 수 없습니다.)\n\n")

        # 디렉토리 구분을 위한 추가 개행
        outfile.write("\n")