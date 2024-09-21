import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
import subprocess
import os


class CMDPowerShellGUI:
    def __init__(self, master):
        self.master = master
        master.title("CMD & PowerShell GUI")
        master.geometry("800x600")

        # 폴더 선택 프레임
        folder_frame = tk.Frame(master)
        folder_frame.pack(pady=10)

        self.folder_path = tk.StringVar()
        tk.Label(folder_frame, text="폴더 경로:").pack(side=tk.LEFT)
        tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT)
        tk.Button(folder_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.LEFT)

        # 명령어 버튼 프레임
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

        commands = [
            ("파일 트리 구조 출력 (PowerShell)", self.ps_tree),
            ("파일 트리 구조 출력 (CMD)", self.cmd_tree),
            ("파일 트리 구조 출력 (커스텀 PowerShell)", self.ps_tree_extensions),
            ("파일 트리 구조 출력 (커스텀 CMD)", self.custom_tree),  # 새로운 버튼 추가
            ("Java 파일 찾기", self.find_java_files),
            ("Java 파일 병합", self.merge_java_files),
            ("특정 패턴 제외 파일 찾기", self.exclude_pattern)
        ]

        # 커스텀 트리 출력시 선택한 확장자만 출력되도록 변경 0921-1-1
        self.extensions_entry = tk.Entry(master, width=50)
        self.extensions_entry.pack(pady=5)
        tk.Label(master, text="커스텀 출력시 출력할 확장자 (쉼표로 구분, 예: .py .txt .java)").pack()

        # 병합할 파일 확장자 선택 # 0921-2-1
        self.merge_extensions = tk.StringVar()
        tk.Label(master, text="병합할 파일 확장자 (쉼표로 구분, 예: .java, .py):").pack()
        self.merge_extensions_entry = tk.Entry(master, textvariable=self.merge_extensions, width=50)
        self.merge_extensions_entry.pack(pady=5)

        # 제외할 파일 선택# 0921-2-1
        self.exclude_files = tk.StringVar()
        tk.Label(master, text="병합에서 제외할 파일 (쉼표로 구분):").pack()
        self.exclude_files_entry = tk.Entry(master, textvariable=self.exclude_files, width=50)
        self.exclude_files_entry.pack(pady=5)

        # 병합 버튼 추가# 0921-2-1
        tk.Button(master, text="파일 병합", command=self.merge_files).pack(pady=10)

        # 확장자 체크박스 프레임 # 0921-3-1
        self.extensions_frame = tk.Frame(master)
        self.extensions_frame.pack(pady=10)
        self.extension_vars = {}

        # 스크롤 가능한 프레임 생성 # 0921-3-2
        self.canvas = tk.Canvas(self.extensions_frame)
        self.scrollbar = ttk.Scrollbar(self.extensions_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        # 0921-3-3
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # 0921-3-4
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 명령어 버튼 프레임 # 0921-3-5
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)
        # 0921-3-6
        commands = [
            ("파일 트리 구조 출력 (커스텀)", self.custom_tree),
            ("파일 병합", self.merge_files),
        ]

        for text, command in commands:
            tk.Button(button_frame, text=text, command=command).pack(fill=tk.X)

        # 결과 출력 영역
        self.output = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.output.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def select_folder(self):
        # 폴더 선택 다이얼로그 표시
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.analyze_folder_extensions(folder)  # 0921-3-7

    def analyze_folder_extensions(self, folder):  # 0921-3-8
        extensions = set()
        has_no_extension = False

        for root, _, files in os.walk(folder):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext:
                    extensions.add(ext)
                else:
                    has_no_extension = True

        self.create_extension_checkboxes(sorted(extensions), has_no_extension)

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

    # 0921-3-9 get_selected_extensions을 체크박스로 만들면서 추가
    def create_extension_checkboxes(self, extensions, has_no_extension):
        # 기존 체크박스 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.extension_vars = {}

        # 확장자별 체크박스 생성
        for ext in extensions:
            var = tk.BooleanVar(value=True)
            self.extension_vars[ext] = var
            ttk.Checkbutton(self.scrollable_frame, text=ext, variable=var).pack(anchor="w")

        # 확장자 없는 파일 체크박스
        if has_no_extension:
            var = tk.BooleanVar(value=True)
            self.extension_vars["No Extension"] = var
            ttk.Checkbutton(self.scrollable_frame, text="확장자 없는 파일", variable=var).pack(anchor="w")

    # 0921-3-10
    # 0921-1-2 커스텀 트리 출력시 출력할 확장자를 입력받아서 리스트에 저장
    def get_selected_extensions(self):
        # 0921-3-11 삭제
        # # 이 부분은 GUI에서 선택된 확장자를 반환하도록 구현해야 합니다.
        # extensions = self.extensions_entry.get().strip()
        # if not extensions:
        #     return None  # 입력이 없으면 모든 파일 표시
        # return [ext.strip() for ext in extensions.split(' ') if ext.strip()]
        return [ext for ext, var in self.extension_vars.items() if var.get()]  # 0921-3-12 추가

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
        allowed_extensions = self.get_selected_extensions()
        self.output.delete(1.0, tk.END)
        path = self.folder_path.get()
        if os.path.exists(path):
            # 수정: allowed_extensions 전달 (실제 구현에 맞게 수정 필요)
            tree = self.generate_tree(path, allowed_extensions)
            self.output.insert(tk.END, tree)
        else:
            self.output.insert(tk.END, "Invalid path")

    # 수정: 함수 시그니처 변경 및 내용 전체 수정
    def generate_tree(self, path, allowed_extensions):
        # 0921-3-13 삭제
        # def walk(path, prefix="", is_last=False):
        #     entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
        #
        #     for i, entry in enumerate(entries):
        #         if not entry.is_dir() and allowed_extensions is not None:
        #             if not any(entry.name.endswith(ext) for ext in allowed_extensions):
        #                 continue
        #
        #         is_last_entry = (i == len(entries) - 1)
        #
        #         if is_last_entry:
        #             connector = "└─"
        #         else:
        #             connector = "├─"
        #
        #         icon = "📁" if entry.is_dir() else "📄"
        #         yield f"{prefix}{connector}{icon} {entry.name}{'/' if entry.is_dir() else ''}"
        #
        #         if entry.is_dir():
        #             # 수정: 항상 올바른 prefix를 사용하도록 변경
        #             new_prefix = prefix + ("    " if is_last_entry else "│  ")
        #             yield from walk(entry.path, new_prefix, is_last_entry)
        #
        #             # 수정: 폴더의 내용이 끝난 후 빈 줄 추가 (마지막 폴더가 아닐 경우)
        #             if not is_last_entry:
        #                 yield prefix + "│"
        #
        # return "\n".join(walk(path))

        # 0921-3-14 추가
        def walk(path, prefix="", is_last=False):
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))

            for i, entry in enumerate(entries):
                _, ext = os.path.splitext(entry.name)
                ext = ext if ext else "No Extension"

                if not entry.is_dir() and ext not in allowed_extensions:
                    continue

                is_last_entry = (i == len(entries) - 1)
                connector = "└─" if is_last_entry else "├─"
                icon = "📁" if entry.is_dir() else "📄"
                yield f"{prefix}{connector}{icon} {entry.name}"

                if entry.is_dir():
                    new_prefix = prefix + ("    " if is_last_entry else "│   ")
                    yield from walk(entry.path, new_prefix, is_last_entry)

        return "\n".join(walk(path))

    def find_java_files(self):
        command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse -Include *.java | Select-Object FullName"'
        self.run_command(command)

    # def merge_java_files(self):
    #     output_file = os.path.join(self.folder_path.get(), "merged_java_files.txt")
    #     command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse -Include *.java | ForEach-Object {{ \\"# $($_)\\"; Get-Content $_.FullName -Encoding UTF8 ; \\"\\" }} | Set-Content \'{output_file}\'"; echo "Merged files saved to {output_file}"'
    #
    #     self.run_command(command)

    def merge_java_files(self):
        output_file = os.path.join(self.folder_path.get(), "merged_java_files.txt")
        encoding = 'utf-8'  # 기본 인코딩 설정

        try:
            with open(output_file, 'w', encoding=encoding) as outfile:
                for root, dirs, files in os.walk(self.folder_path.get()):
                    for file in files:
                        if file.endswith('.java'):
                            file_path = os.path.join(root, file)
                            outfile.write(f"# {file_path}\n")
                            with open(file_path, 'r', encoding=encoding) as infile:
                                outfile.write(infile.read())
                            outfile.write("\n\n")

            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Merged files saved to {output_file}")
        except Exception as e:
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"Error merging files: {str(e)}")

    # 0921-2-4
    def merge_files(self):
        # 0921-3-15 삭제
        # selected_extensions = self.get_selected_extensions()
        # merge_extensions = self.get_merge_extensions()
        # exclude_files = self.get_exclude_files()
        #
        # if not merge_extensions:
        #     messagebox.showwarning("경고", "병합할 파일 확장자를 선택해주세요.")
        #     return
        #
        # output_file = os.path.join(self.folder_path.get(), "merged_files.txt")
        # encoding = 'utf-8'
        #
        # try:
        #     with open(output_file, 'w', encoding=encoding) as outfile:
        #         self.write_directory_content(self.folder_path.get(), outfile, selected_extensions, merge_extensions,
        #                                      exclude_files, encoding)
        #
        #     self.output.delete(1.0, tk.END)
        #     self.output.insert(tk.END, f"병합된 파일이 {output_file}에 저장되었습니다.")
        # except Exception as e:
        #     self.output.delete(1.0, tk.END)
        #     self.output.insert(tk.END, f"파일 병합 중 오류 발생: {str(e)}")

        # 0921-3-16 추가
        selected_extensions = self.get_selected_extensions()
        output_file = os.path.join(self.folder_path.get(), "merged_files.txt")
        encoding = 'utf-8'

        try:
            with open(output_file, 'w', encoding=encoding) as outfile:
                self.write_directory_content(self.folder_path.get(), outfile, selected_extensions, encoding)

            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"병합된 파일이 {output_file}에 저장되었습니다.")
        except Exception as e:
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"파일 병합 중 오류 발생: {str(e)}")

    # 0921-3-17 삭제
    # 0921-2-5###
    # def write_directory_content(self, directory, outfile, selected_extensions, merge_extensions, exclude_files,
    #                             encoding, level=0):
    #     outfile.write(f"{'#' * (level + 1)} 디렉토리: {directory}\n")
    #
    #     for entry in sorted(os.scandir(directory), key=lambda e: (not e.is_dir(), e.name.lower())):
    #         if entry.is_dir():
    #             self.write_directory_content(entry.path, outfile, selected_extensions, merge_extensions, exclude_files,
    #                                          encoding, level + 1)
    #         elif entry.is_file():
    #             _, ext = os.path.splitext(entry.name)
    #             if selected_extensions is None or ext in selected_extensions:
    #                 if entry.name not in exclude_files:
    #                     outfile.write(f"{'#' * (level + 2)} 파일: {entry.path}\n")
    #                     if ext in merge_extensions:
    #                         outfile.write(f"```{ext[1:]}\n")  # 확장자 표시
    #                         with open(entry.path, 'r', encoding=encoding) as infile:
    #                             outfile.write(infile.read())
    #                         outfile.write("\n```\n")
    #                 else:
    #                     outfile.write(f"{'#' * (level + 2)} 파일 (내용 생략됨): {entry.path}\n")
    #
    #     outfile.write("\n")

    # 0921-3-18 추가
    def write_directory_content(self, directory, outfile, selected_extensions, encoding, level=0):
        outfile.write(f"{'#' * (level + 1)} 디렉토리: {directory}\n")

        for entry in sorted(os.scandir(directory), key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.is_dir():
                self.write_directory_content(entry.path, outfile, selected_extensions, encoding, level + 1)
            elif entry.is_file():
                _, ext = os.path.splitext(entry.name)
                ext = ext if ext else "No Extension"
                if ext in selected_extensions:
                    outfile.write(f"{'#' * (level + 2)} 파일: {entry.path}\n")
                    outfile.write(f"```{ext[1:] if ext != 'No Extension' else ''}\n")
                    with open(entry.path, 'r', encoding=encoding) as infile:
                        outfile.write(infile.read())
                    outfile.write("\n```\n")

        outfile.write("\n")

    def exclude_pattern(self):
        pattern = "test"  # 이 패턴을 사용자 입력으로 변경할 수 있습니다.
        command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse | Where-Object {{ $_.Name -notmatch \'{pattern}\' }} | Select-Object FullName"'
        self.run_command(command)


if __name__ == "__main__":
    root = tk.Tk()
    app = CMDPowerShellGUI(root)
    root.mainloop()