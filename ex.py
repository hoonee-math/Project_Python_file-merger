import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import os


class CMDPowerShellGUI:
    def __init__(self, master):
        self.master = master
        master.title("CMD & PowerShell GUI")
        master.geometry("800x600")

        # 폴더 선택 프레임 생성
        self.create_folder_frame()

        # 확장자 입력 필드 생성
        self.create_extension_input()

        # 명령어 버튼 프레임 생성
        self.create_button_frame()

        # 결과 출력 영역 생성
        self.create_output_area()

    def create_folder_frame(self):
        # 폴더 선택을 위한 UI 요소 생성
        folder_frame = tk.Frame(self.master)
        folder_frame.pack(pady=10)

        self.folder_path = tk.StringVar()
        tk.Label(folder_frame, text="폴더 경로:").pack(side=tk.LEFT)
        tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT)
        tk.Button(folder_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.LEFT)

    def create_extension_input(self):
        # 확장자 입력을 위한 UI 요소 생성
        self.extensions_entry = tk.Entry(self.master, width=50)
        self.extensions_entry.pack(pady=5)
        tk.Label(self.master, text="출력할 확장자 (쉼표로 구분, 예: .py,.txt,.java)").pack()

    def create_button_frame(self):
        # 다양한 기능 버튼을 포함하는 프레임 생성
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        commands = [
            ("파일 트리 구조 출력 (CMD)", self.cmd_tree),
            ("파일 트리 구조 출력 (PowerShell)", self.ps_tree),
            ("파일 트리 구조 출력 (커스텀)", self.custom_tree),
            ("선택된 파일 찾기", self.find_selected_files),
            ("선택된 파일 병합", self.merge_selected_files),
            ("특정 패턴 제외 파일 찾기", self.exclude_pattern)
        ]

        for text, command in commands:
            tk.Button(button_frame, text=text, command=command).pack(fill=tk.X)

    def create_output_area(self):
        # 결과를 표시할 스크롤 가능한 텍스트 영역 생성
        self.output = scrolledtext.ScrolledText(self.master, wrap=tk.WORD)
        self.output.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def select_folder(self):
        # 폴더 선택 다이얼로그 표시
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)

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

    def get_selected_extensions(self):
        # 사용자가 입력한 확장자 목록 반환
        extensions = self.extensions_entry.get().strip()
        if not extensions:
            return None
        return [ext.strip() for ext in extensions.split(',') if ext.strip()]

    def cmd_tree(self):
        # CMD를 사용하여 파일 트리 구조 출력
        command = f'tree "{self.folder_path.get()}" /F'
        self.run_command(command)

    def ps_tree(self):
        # PowerShell을 사용하여 파일 트리 구조 출력
        extensions = self.get_selected_extensions()
        if not extensions:
            command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse | Select-Object FullName"'
        else:
            extension_filter = ','.join(f'*{ext}' for ext in extensions)
            command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse -Include {extension_filter} | Select-Object FullName"'
        self.run_command(command)

    def custom_tree(self):
        #
        self.output.delete(1.0, tk.END)
        path = self.folder_path.get()
        if os.path.exists(path):
            allowed_extensions = self.get_selected_extensions()
            tree = self.generate_tree(path, allowed_extensions)
            self.output.insert(tk.END, tree)
        else:
            self.output.insert(tk.END, "Invalid path")

    def generate_tree(self, path, allowed_extensions):
        # 재귀적으로 파일 트리 구조 생성
        def walk(path, prefix="", is_last=False):
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
            for i, entry in enumerate(entries):
                if not entry.is_dir() and allowed_extensions is not None:
                    if not any(entry.name.endswith(ext) for ext in allowed_extensions):
                        continue

                is_last_entry = (i == len(entries) - 1)
                connector = "└─ " if is_last_entry else "├─ "
                icon = "📁" if entry.is_dir() else "📄"
                yield f"{prefix}{connector}{icon} {entry.name}"

                if entry.is_dir():
                    extension = "    " if is_last_entry else "│   "
                    yield from walk(entry.path, prefix + extension, is_last_entry)

                    if not is_last_entry:
                        yield prefix + "│"

        return "\n".join(walk(path))

    def find_selected_files(self):
        # 선택된 확장자의 파일 찾기
        extensions = self.get_selected_extensions()
        if not extensions:
            command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse | Select-Object FullName"'
        else:
            extension_filter = ','.join(f'*{ext}' for ext in extensions)
            command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse -Include {extension_filter} | Select-Object FullName"'
        self.run_command(command)

    def merge_selected_files(self):
        # 선택된 확장자의 파일 내용 병합
        extensions = self.get_selected_extensions()
        if not extensions:
            messagebox.showwarning("경고", "병합할 파일 확장자를 선택해주세요.")
            return

        extension_filter = ','.join(f'*{ext}' for ext in extensions)
        output_file = os.path.join(self.folder_path.get(), f"merged_files{''.join(extensions)}.txt")

        script = f"""
        function Is-TextFile($filePath) {{
            $textExtensions = @('.txt', '.csv', '.log', '.xml', '.json', '.html', '.css', '.js', '.py', '.java', '.c', '.cpp', '.h', '.cs')
            return $textExtensions -contains [System.IO.Path]::GetExtension($filePath)
        }}

        function Process-Directory($dir) {{
            $items = Get-ChildItem -Path $dir

            "# Directory: $dir" | Out-File -Append -FilePath '{output_file}'

            $files = $items | Where-Object {{ !$_.PSIsContainer -and ($_.Extension -in ({','.join(f"'{ext}'" for ext in extensions)})) }}
            foreach ($file in $files) {{
                "" | Out-File -Append -FilePath '{output_file}'
                "## File: $($file.FullName)" | Out-File -Append -FilePath '{output_file}'
                if (Is-TextFile $file.FullName) {{
                    Get-Content $file.FullName | Out-File -Append -FilePath '{output_file}'
                }} else {{
                    "[Binary file, content not displayed]" | Out-File -Append -FilePath '{output_file}'
                }}
            }}

            $subdirs = $items | Where-Object {{ $_.PSIsContainer }}
            foreach ($subdir in $subdirs) {{
                "" | Out-File -Append -FilePath '{output_file}'
                Process-Directory $subdir.FullName
            }}
        }}

        Process-Directory '{self.folder_path.get()}'
        """

        command = f'powershell -Command "{script}"; echo "Merged files saved to {output_file}"'
        self.run_command(command)

    def exclude_pattern(self):
        # 특정 패턴을 제외한 파일 찾기
        pattern = "test"  # 이 패턴을 사용자 입력으로 변경할 수 있습니다.
        command = f'powershell "Get-ChildItem -Path \'{self.folder_path.get()}\' -Recurse | Where-Object {{ $_.Name -notmatch \'{pattern}\' }} | Select-Object FullName"'
        self.run_command(command)


if __name__ == "__main__":
    root = tk.Tk()
    app = CMDPowerShellGUI(root)
    root.mainloop()