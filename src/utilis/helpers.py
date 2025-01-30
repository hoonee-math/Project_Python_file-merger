import os
from pathlib import Path
from typing import Optional, Union, List, Tuple


def normalize_path(path: Union[str, Path]) -> str:
    """경로를 정규화

    Args:
        path (Union[str, Path]): 정규화할 경로

    Returns:
        str: 정규화된 경로
    """
    return str(Path(path)).replace('\\', '/')


def get_file_extension(filename: str) -> str:
    """파일의 확장자를 반환

    Args:
        filename (str): 파일 이름

    Returns:
        str: 확장자 (점 포함)
    """
    return os.path.splitext(filename)[1]


def get_relative_path(path: Union[str, Path], base_path: Union[str, Path]) -> Optional[str]:
    """기준 경로에 대한 상대 경로 반환

    Args:
        path (Union[str, Path]): 대상 경로
        base_path (Union[str, Path]): 기준 경로

    Returns:
        Optional[str]: 상대 경로, 실패시 None
    """
    try:
        relative = Path(path).relative_to(Path(base_path))
        return str(relative).replace('\\', '/')
    except ValueError:
        return None


def list_files(directory: Union[str, Path],
               extensions: Optional[List[str]] = None,
               ignore_patterns: Optional[List[str]] = None) -> List[Tuple[str, str]]:
    """디렉토리 내의 파일 목록을 반환

    Args:
        directory (Union[str, Path]): 검색할 디렉토리
        extensions (Optional[List[str]], optional): 포함할 확장자 목록. Defaults to None.
        ignore_patterns (Optional[List[str]], optional): 제외할 패턴 목록. Defaults to None.

    Returns:
        List[Tuple[str, str]]: (파일 전체 경로, 파일 이름) 튜플 목록
    """
    result = []
    for root, _, files in os.walk(directory):
        for file in files:
            if ignore_patterns and any(pattern in file for pattern in ignore_patterns):
                continue

            if extensions:
                ext = get_file_extension(file)
                if ext not in extensions:
                    continue

            full_path = os.path.join(root, file)
            result.append((normalize_path(full_path), file))

    return sorted(result)