
# 폴더의 확장자를 분석해서 체크박스를 만들려면 다음 코드를 적용시키면 된다!

import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk
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

        # 확장자 체크박스 프레임
        self.extensions_frame = tk.Frame(master)
        self.extensions_frame.pack(pady=10)
        self.extension_vars = {}

        # 스크롤 가능한 프레임 생성
        self.canvas = tk.Canvas(self.extensions_frame)
        self.scrollbar = ttk.Scrollbar(self.extensions_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 명령어 버튼 프레임
        button_frame = tk.Frame(master)
        button_frame.pack(pady=10)

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
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.analyze_folder_extensions(folder)

    def analyze_folder_extensions(self, folder):
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

    def get_selected_extensions(self):
        return [ext for ext, var in self.extension_vars.items() if var.get()]

    def custom_tree(self):
        allowed_extensions = self.get_selected_extensions()
        self.output.delete(1.0, tk.END)
        path = self.folder_path.get()
        if os.path.exists(path):
            tree = self.generate_tree(path, allowed_extensions)
            self.output.insert(tk.END, tree)
        else:
            self.output.insert(tk.END, "Invalid path")

    def generate_tree(self, path, allowed_extensions):
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

    def merge_files(self):
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

if __name__ == "__main__":
    root = tk.Tk()
    app = CMDPowerShellGUI(root)
    root.mainloop()