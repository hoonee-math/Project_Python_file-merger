import os
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """기존 빌드 파일 정리"""
    dirs_to_clean = ['build', 'dist']
    files_to_clean = ['*.spec']

    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    for pattern in files_to_clean:
        for file in Path('.').glob(pattern):
            file.unlink()


def build():
    """실행 파일 빌드"""
    # PyInstaller 명령 실행
    subprocess.run([
        'pyinstaller',
        '--name=FileMerger',
        '--windowed',  # GUI 모드
        '--onefile',  # 단일 실행 파일
        '--icon=resources/icons/hoonee_math_icon.ico',
        '--add-data=resources/icons/*;resources/icons',
        'main.py'
    ], check=True)


if __name__ == '__main__':
    clean_build()
    build()