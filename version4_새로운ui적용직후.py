import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import subprocess
import os
import platform  # 0921-5-3
from datetime import datetime  # 0921-6-1


class CMDPowerShellGUI:
    # 0921-7-1 새로운 ui 적용을 위해 삭제
    # def __init__(self, master):
    #     self.master = master
    #     master.title("CMD & PowerShell GUI")
    #     master.geometry("800x600")
    #
    #     # 폴더 선택 프레임
    #     folder_frame = tk.Frame(master)
    #     folder_frame.pack(pady=10)
    #
    #     self.folder_path = tk.StringVar()
    #     tk.Label(folder_frame, text="폴더 경로:").pack(side=tk.LEFT)
    #     tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT)
    #     tk.Button(folder_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.LEFT)
    #     tk.Button(folder_frame, text="폴더 열기", command=self.open_folder).pack(side=tk.LEFT)  # 0921-5-1
    #
    #     # 명령어 버튼 프레임
    #     button_frame = tk.Frame(master)
    #     button_frame.pack(pady=10)
    #
    #     commands = [
    #         ("파일 트리 구조 출력 (PowerShell)", self.ps_tree),
    #         ("파일 트리 구조 출력 (CMD)", self.cmd_tree),
    #         ("파일 트리 구조 출력 (커스텀 PowerShell)", self.ps_tree_extensions),
    #         ("파일 트리 구조 출력 (커스텀 CMD)", self.custom_tree),  # 새로운 버튼 추가
    #         # ("특정 패턴 제외 파일 찾기", self.exclude_pattern)    # 0921-4-1 주석처리 및 삭제
    #     ]
    #
    #     # 커스텀 트리 출력시 선택한 확장자만 출력되도록 변경 0921-1-1
    #     tk.Label(master, text="커스텀 출력시 출력할 확장자 (쉼표로 구분, 예: .py .txt .java)").pack(pady=(20,0))
    #     self.extensions_entry = tk.Entry(master, width=50)
    #     self.extensions_entry.pack(pady=(0,20))
    #
    #     # 병합할 파일 확장자 선택 # 0921-2-1
    #     self.merge_extensions = tk.StringVar()
    #     tk.Label(master, text="병합할 파일 확장자 (쉼표로 구분, 예: .java, .py):").pack()
    #     self.merge_extensions_entry = tk.Entry(master, textvariable=self.merge_extensions, width=50)
    #     self.merge_extensions_entry.pack(pady=(0,20))
    #
    #     # 제외할 파일 선택# 0921-2-1
    #     self.exclude_files = tk.StringVar()
    #     tk.Label(master, text="병합에서 제외할 파일 (쉼표로 구분):").pack()
    #     self.exclude_files_entry = tk.Entry(master, textvariable=self.exclude_files, width=50)
    #     self.exclude_files_entry.pack(pady=(0,20))
    #
    #     # 병합 버튼 추가# 0921-2-1
    #     tk.Button(master, text="파일 병합", command=self.merge_files).pack(pady=10)
    #
    #
    #     for text, command in commands:
    #         tk.Button(button_frame, text=text, command=command).pack(fill=tk.X)
    #
    #     # 결과 출력 영역
    #     self.output = scrolledtext.ScrolledText(master, wrap=tk.WORD)
    #     self.output.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # 0921-7-2 새로운 ui 적용을 위해 추가
    def __init__(self, master):
        self.master = master
        master.title("Modern File Manager")
        master.geometry("900x600")
        master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 색상 설정
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#4a86e8', foreground='white', font=('Helvetica', 10))
        self.style.map('TButton', background=[('active', '#619ff0')])
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))

        self.create_widgets()

    # 0921-7-3 새로운 ui 적용을 위해 추가
    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20 20 20 0")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 폴더 선택 프레임
        folder_frame = ttk.Frame(main_frame, padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 20))

        self.folder_path = tk.StringVar()
        ttk.Label(folder_frame, text="폴더 경로:").pack(side=tk.LEFT)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(folder_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.LEFT)
        ttk.Button(folder_frame, text="폴더 열기", command=self.open_folder).pack(side=tk.LEFT, padx=(10, 0))

        # 하단 프레임 (명령어 버튼 + 입력 영역 + 결과 출력)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # 명령어 버튼 프레임
        button_frame = ttk.Frame(bottom_frame, padding="0 0 20 0")
        button_frame.pack(side=tk.LEFT, fill=tk.Y)

        commands = [
            ("파일 트리 구조 출력 (PowerShell)", self.ps_tree),
            ("파일 트리 구조 출력 (CMD)", self.cmd_tree),
            ("파일 트리 구조 출력 (커스텀 PowerShell)", self.ps_tree_extensions),
            ("파일 트리 구조 출력 (커스텀 CMD)", self.custom_tree),
        ]

        for text, command in commands:
            ttk.Button(button_frame, text=text, command=command, width=25).pack(pady=(0, 10))

        # 입력 및 결과 프레임
        input_output_frame = ttk.Frame(bottom_frame)
        input_output_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 입력 영역
        input_frame = ttk.Frame(input_output_frame)
        input_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(input_frame, text="커스텀 출력시 출력할 확장자:").pack(anchor='w')
        self.extensions_entry = ttk.Entry(input_frame, width=50)
        self.extensions_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="병합할 파일 확장자:").pack(anchor='w')
        self.merge_extensions = tk.StringVar()
        self.merge_extensions_entry = ttk.Entry(input_frame, textvariable=self.merge_extensions, width=50)
        self.merge_extensions_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(input_frame, text="병합에서 제외할 파일:").pack(anchor='w')
        self.exclude_files = tk.StringVar()
        self.exclude_files_entry = ttk.Entry(input_frame, textvariable=self.exclude_files, width=50)
        self.exclude_files_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(input_frame, text="파일 병합", command=self.merge_files).pack(anchor='w')

        # 결과 출력 영역
        self.output = scrolledtext.ScrolledText(input_output_frame, wrap=tk.WORD, height=15)
        self.output.pack(fill=tk.BOTH, expand=True)

    def select_folder(self):
        # 폴더 선택 다이얼로그 표시
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

    # 0921-5-2
    def open_folder(self):
        folder = self.folder_path.get()
        if folder and os.path.exists(folder):
            if platform.system() == "Windows":
                os.startfile(folder)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", folder])
            else:  # Linux and other Unix-like
                subprocess.Popen(["xdg-open", folder])
        else:
            messagebox.showerror("오류", "유효한 폴더를 선택해주세요.")

    def run_command(self, command):
        # 주어진 명령어를 실행하고 결과를 출력 영역에 표시
        try:
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, result.stdout)
            if result.stderr:
                self.output.insert(tk.END, "\nErrors:\n" + result.stderr)
        except Exception as e:
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Error: {str(e)}")

    # 0921-1-2 커스텀 트리 출력시 출력할 확장자를 입력받아서 리스트에 저장
    def get_selected_extensions(self):
        # 이 부분은 GUI에서 선택된 확장자를 반환하도록 구현해야 합니다.
        extensions = self.extensions_entry.get().strip()
        if not extensions:
            return None  # 입력이 없으면 모든 파일 표시
        return [ext.strip() for ext in extensions.split(' ') if ext.strip()]

    # 0921-2-2
    def get_merge_extensions(self):
        extensions = self.merge_extensions.get().strip()
        if not extensions:
            return None
        return [ext.strip() for ext in extensions.split(',') if ext.strip()]

    # 0921-2-3
    def get_exclude_files(self):
        files = self.exclude_files.get().strip()
        if not files:
            return []
        return [file.strip() for file in files.split(',') if file.strip()]

    def cmd_tree(self):
        # CMD를 사용하여 파일 트리 구조 출력
        command = f'tree "{self.folder_path.get()}" /F'
        self.run_command(command)

    def ps_tree(self):
        # PowerShell을 사용하여 파일 트리 구조 출력
        command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse | Select-Object FullName"'
        self.run_command(command)

    def ps_tree_extensions(self):
        # 0921-1-3 get_selected_extensions에 의해 선택된 확장자만 파워쉘로 표시
        extensions = self.get_selected_extensions()
        if not extensions:
            # 선택된 확장자가 없으면 모든 파일 표시
            command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse | Select-Object FullName"'
        else:
            # 선택된 확장자만 표시
            extension_filter = ','.join(f'*{ext}' for ext in extensions)
            command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse -Include {extension_filter} | Select-Object FullName"'

        self.run_command(command)

    def custom_tree(self):
        # 수정: allowed_extensions 매개변수 추가 커스텀 방식으로 파일 트리 구조 출력
        self.output.delete(1.0, tk.END)
        path = self.folder_path.get()
        if os.path.exists(path):
            # 수정: allowed_extensions 전달 (실제 구현에 맞게 수정 필요)
            allowed_extensions = self.get_selected_extensions()
            tree = self.generate_tree(path, allowed_extensions)
            self.output.insert(tk.END, tree)
        else:
            self.output.insert(tk.END, "Invalid path")

    # 수정: 함수 시그니처 변경 및 내용 전체 수정
    def generate_tree(self, path, allowed_extensions):
        def walk(path, prefix="", is_last=False):
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))

            for i, entry in enumerate(entries):
                if not entry.is_dir() and allowed_extensions is not None:
                    if not any(entry.name.endswith(ext) for ext in allowed_extensions):
                        continue

                is_last_entry = (i == len(entries) - 1)

                if is_last_entry:
                    connector = "└─"
                else:
                    connector = "├─"

                icon = "📁" if entry.is_dir() else "📄"
                yield f"{prefix}{connector}{icon} {entry.name}{'/' if entry.is_dir() else ''}"

                if entry.is_dir():
                    # 수정: 항상 올바른 prefix를 사용하도록 변경
                    new_prefix = prefix + ("    " if is_last_entry else "│  ")
                    yield from walk(entry.path, new_prefix, is_last_entry)

                    # 수정: 폴더의 내용이 끝난 후 빈 줄 추가 (마지막 폴더가 아닐 경우)
                    if not is_last_entry:
                        yield prefix + "│"

        return "\n".join(walk(path))

    # 0921-2-4
    def merge_files(self):
        selected_extensions = self.get_selected_extensions()
        merge_extensions = self.get_merge_extensions()
        exclude_files = self.get_exclude_files()

        if not merge_extensions:
            messagebox.showwarning("경고", "병합할 파일 확장자를 선택해주세요.")
            return

        # 0921-6-2 저장할 파일 명 변경을 위해 추가
        now = datetime.now()  # 0921-6-3 현재 날짜
        date_time = now.strftime("%y%m%d-%H%M")  # 0921-6-4 시간
        folder_name = os.path.basename(self.folder_path.get())  # 0921-6-5 선택된 폴더 이름 추출
        file_name = f"{date_time}-{folder_name}-merged.md"  # 0921-6-6 새로운 파일 이름 생성

        output_file = os.path.join(self.folder_path.get(), file_name)
        encoding = 'utf-8'

        try:
            with open(output_file, 'w', encoding=encoding) as outfile:
                self.write_directory_content(self.folder_path.get(), outfile, selected_extensions, merge_extensions,
                                             exclude_files, encoding)

            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"병합된 파일이 {output_file}에 저장되었습니다.")
        except Exception as e:
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"파일 병합 중 오류 발생: {str(e)}")

    # 0921-2-5
    def write_directory_content(self, directory, outfile, selected_extensions, merge_extensions, exclude_files,
                                encoding, level=0):
        outfile.write(f"{'#'} 디렉토리: {directory}\n\n")

        for entry in sorted(os.scandir(directory), key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.is_dir():
                self.write_directory_content(entry.path, outfile, selected_extensions, merge_extensions, exclude_files,
                                             encoding, level + 1)
            elif entry.is_file():
                _, ext = os.path.splitext(entry.name)
                if selected_extensions is None or ext in selected_extensions:
                    if entry.name not in exclude_files:
                        outfile.write(f"{'##'} 파일: {entry.path}\n")
                        if ext in merge_extensions:
                            outfile.write(f"```{ext[1:]}\n")  # 확장자 표시
                            with open(entry.path, 'r', encoding=encoding) as infile:
                                outfile.write(infile.read())
                            outfile.write("\n```\n\n")
                    else:
                        outfile.write(f"{'##'} 파일 (내용 생략됨): {entry.path}\n\n")

        outfile.write("\n")

    # 0921-4-2 주석처리 및 삭제
    # def exclude_pattern(self):
    #     pattern = "test"  # 이 패턴을 사용자 입력으로 변경할 수 있습니다.
    #     command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse | Where-Object {{ $_.Name -notmatch \'{pattern}\' }} | Select-Object FullName"'
    #     self.run_command(command)


if __name__ == "__main__":
    root = tk.Tk()
    app = CMDPowerShellGUI(root)
    root.mainloop()