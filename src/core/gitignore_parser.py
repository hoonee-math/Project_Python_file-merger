import os
import re
from pathlib import Path
from typing import List, Pattern


class GitignoreParser:
    def __init__(self, root_path: str):
        """GitIgnore 파서 초기화

        Args:
            root_path (str): 프로젝트 루트 경로
        """
        self.root_path = Path(root_path)
        self.ignore_patterns: List[Pattern] = []
        self.load_gitignore()

    def load_gitignore(self) -> None:
        """GitIgnore 파일을 로드하고 패턴을 컴파일"""
        gitignore_path = self.root_path / '.gitignore'
        if not gitignore_path.exists():
            return

        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                pattern = line.strip()
                if pattern and not pattern.startswith('#'):
                    # 기본 glob 패턴을 정규식으로 변환
                    regex_pattern = self._convert_glob_to_regex(pattern)
                    try:
                        compiled_pattern = re.compile(regex_pattern)
                        self.ignore_patterns.append(compiled_pattern)
                    except re.error:
                        continue  # 잘못된 패턴은 무시

    def _convert_glob_to_regex(self, pattern: str) -> str:
        """Glob 패턴을 정규식으로 변환

        Args:
            pattern (str): Glob 패턴

        Returns:
            str: 정규식 패턴
        """
        # 시작 부분 처리
        if pattern.startswith('/'):
            pattern = pattern[1:]  # 루트 상대 경로
        elif pattern.startswith('**/'):
            pattern = f'.*?{pattern[3:]}'  # 모든 하위 디렉토리

        # 패턴 변환
        pattern = pattern.replace('.', r'\.')  # 점을 이스케이프
        pattern = pattern.replace('**', '.*?')  # 모든 하위 경로
        pattern = pattern.replace('*', '[^/]*')  # 단일 경로 내의 모든 문자
        pattern = pattern.replace('?', '[^/]')  # 단일 문자

        # 끝 부분 처리
        if pattern.endswith('/'):
            pattern = f'{pattern}.*'  # 디렉토리 내의 모든 파일

        return f'^{pattern}$'

    def should_ignore(self, path: str) -> bool:
        """주어진 경로가 gitignore 규칙에 따라 무시되어야 하는지 확인

        Args:
            path (str): 검사할 파일/디렉토리 경로

        Returns:
            bool: 무시해야 하면 True, 아니면 False
        """
        if not self.ignore_patterns:
            return False

        try:
            relative_path = str(Path(path).relative_to(self.root_path)).replace('\\', '/')

            # 각 패턴에 대해 검사
            for pattern in self.ignore_patterns:
                if pattern.search(relative_path):
                    return True

                # 디렉토리 경로도 검사
                dir_path = f"{relative_path}/"
                if pattern.search(dir_path):
                    return True

            return False

        except ValueError:
            return False  # 상대 경로를 만들 수 없는 경우