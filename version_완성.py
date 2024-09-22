import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, ttk, font
import subprocess
import os
import platform  # 0921-5-3
from datetime import datetime #0921-6-1
from pathlib import Path

class CMDPowerShellGUI:
    # 0921-7-2 새로운 ui 적용을 위해 추가
    def __init__(self, master):
        self.master = master
        master.title("File Manager without CMD")
        master.geometry("1200x800")
        master.configure(bg="#f0f0f0")

        self.base_folder = None  # 0922-6-4 기본 폴더 경로를 저장할 변수

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 색상 설정
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', background='#4a86e8', foreground='white', font=('Helvetica', 10))
        self.style.map('TButton', background=[('active', '#619ff0')])
        self.style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
        self.style.configure('TEntry', font=('Helvetica', 10))
        self.style.configure("Transparent.TCheckbutton", background="#f0f0f0") # 0922-3-1 체크박스 스타일 설정

        # 작은 버튼 스타일 설정
        self.style.configure('Small.TButton', font=('Helvetica', 8))

        self.create_widgets()
        self.create_status_bar()  # 추가


    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 폴더 선택 프레임 (최상단)
        folder_frame = ttk.Frame(main_frame, padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 0))

        self.folder_path = tk.StringVar()
        ttk.Label(folder_frame, text="폴더 경로:").pack(side=tk.LEFT)
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(folder_frame, text="폴더 선택", command=self.select_folder).pack(side=tk.LEFT)
        ttk.Button(folder_frame, text="폴더 열기", command=self.open_folder).pack(side=tk.LEFT, padx=(10, 0))

        # 하단 프레임 (왼쪽 컨트롤 + 오른쪽 출력)
        # bottom_frame = ttk.Frame(main_frame)
        # bottom_frame.pack(fill=tk.BOTH, expand=True)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        bottom_frame.columnconfigure(1, weight=1)  # 오른쪽 열에 가중치 부여
        bottom_frame.rowconfigure(0, weight=1)  # 행에 가중치 부여


        # 왼쪽 프레임 (버튼 + 입력)
        # left_frame = ttk.Frame(bottom_frame, padding="10")
        # left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        left_frame = ttk.Frame(bottom_frame, padding="10", width=250)  # 너비 고정
        left_frame.grid(row=0, column=0, sticky="nsew")
        left_frame.grid_propagate(False)  # 크기 고정

        # 왼쪽 프레임 내용 설정
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=0)  # 버튼 영역
        left_frame.rowconfigure(1, weight=1)  # 입력 영역
        left_frame.rowconfigure(2, weight=0)  # 파일 병합 버튼

        # 버튼 영역
        # button_frame = ttk.Frame(left_frame)
        # button_frame.pack(fill=tk.X, pady=(0, 20))
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(button_frame, text="기본 구조 출력", anchor="w").pack(fill=tk.X, pady=(0, 5))
        commands = [
            ("파일 트리 리스트", self.ps_tree),
            ("파일 트리 그래프", self.cmd_tree),
        ]

        # 0922-1-3 커스텀 구조 출력 문구 추가를 위해 삽입
        for text, command in commands:
            ttk.Button(button_frame, text=text, command=command).pack(fill=tk.X, pady=(0, 5))

        ttk.Label(button_frame, text="커스텀 구조 출력", anchor="w").pack(fill=tk.X, pady=(10, 5))
        commands = [
            ("파일 트리 리스트 (커스텀)", self.ps_tree_extensions),
            ("파일 트리 그래프 (커스텀)", self.custom_tree),
        ]

        for text, command in commands:
            ttk.Button(button_frame, text=text, command=command).pack(fill=tk.X, pady=(0, 5))

        # 입력 영역
        input_frame = ttk.Frame(left_frame)
        input_frame.grid(row=1, column=0, sticky="nsew")

        # 0922-2-1 스크롤 가능한 체크박스 프레임 checkbox_canvas
        ttk.Label(input_frame, text="파일 확장자 선택").pack(anchor='w', pady=(10, 5))
        self.checkbox_frame = ttk.Frame(input_frame)
        self.checkbox_frame.pack(fill=tk.BOTH, expand=True)

        self.checkbox_canvas = tk.Canvas(self.checkbox_frame)  # 0922-3-2 확장자 종류 수에 따른 동적인 스크롤 적용, 높이 제한 height=200 삭제
        # self.checkbox_frame = ttk.Frame(self.checkbox_canvas)  # 0922-3-3 scrollable_frame 으로 대체
        self.checkbox_scrollbar = ttk.Scrollbar(self.checkbox_frame, orient="vertical", command=self.checkbox_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.checkbox_canvas)  # 0922-3-4 scrollable_frame 으로 대체

        # self.checkbox_canvas.pack(side="left", fill="both", expand=True)  # 0922-3-5 scrollable_frame 으로 대체
        # self.checkbox_scrollbar.pack(side="right", fill="y")  # 0922-3-5 scrollable_frame 으로 대체
        self.scrollable_frame.bind(  # 0922-3-6 scrollable_frame bind
            "<Configure>",
            lambda e: self.checkbox_canvas.configure(
                scrollregion=self.checkbox_canvas.bbox("all")
            )
        )

        self.checkbox_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")  # 0922-3-7 scrollable_frame 으로 대체
        self.checkbox_canvas.configure(yscrollcommand=self.checkbox_scrollbar.set)

        # self.checkbox_frame.bind("<Configure>", lambda e: self.checkbox_canvas.configure(
        #     scrollregion=self.checkbox_canvas.bbox("all")))
        #  0922-3-8 마우스 휠 이벤트 바인딩
        self.checkbox_canvas.bind("<MouseWheel>", self._on_mousewheel)

        self.checkbox_canvas.pack(side="left", fill="both", expand=True)#  0922-3-9
        self.checkbox_scrollbar.pack(side="right", fill="y")#  0922-3-10

        # 0922-2-7 병합할 파일 확장자를 get_selected_extensions 에서 받아서 사용하도록 수정, 버튼 삭제
        # # 병합할 파일 확장자 (기존 코드 유지)
        # ttk.Label(input_frame, text="병합할 파일 확장자:").pack(anchor='w')
        # self.merge_extensions = tk.StringVar()
        # self.merge_extensions_entry = ttk.Entry(input_frame, textvariable=self.merge_extensions)
        # self.merge_extensions_entry.pack(fill=tk.X, pady=(0, 10))

        # 병합에서 제외할 파일/폴더 프레임
        exclude_frame = ttk.Frame(input_frame)
        exclude_frame.pack(fill=tk.X, pady=(10, 5))

        ttk.Label(exclude_frame, text="병합에서 제외할 파일/폴더").pack(side=tk.LEFT)

        # 작은 아이콘 버튼 생성
        button_font = font.Font(size=8)
        ttk.Button(exclude_frame, text="📄", command=self.add_exclude_file, width=3, style='Small.TButton').pack(
            side=tk.RIGHT, padx=(2, 0))
        ttk.Button(exclude_frame, text="📁", command=self.add_exclude_folder, width=3, style='Small.TButton').pack(
            side=tk.RIGHT, padx=(2, 0))

        # 텍스트 입력 영역 (여러 줄 입력 가능)
        self.exclude_files = tk.Text(input_frame, height=4, wrap=tk.WORD)
        self.exclude_files.pack(fill=tk.X, pady=(5, 10))

        # 파일 병합 버튼
        self.merge_button = ttk.Button(left_frame, text="파일 병합", command=self.merge_files)
        self.merge_button.grid(row=2, column=0, sticky="ew", pady=(5, 0))

        # 오른쪽 프레임 (결과 출력)
        # right_frame = ttk.Frame(bottom_frame, padding="10")
        # right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame = ttk.Frame(bottom_frame, padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")

        # 결과 출력 영역
        self.output = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)  # 하단에 여백 추가


    def select_folder(self):
        # 폴더 선택 다이얼로그 표시
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.base_folder = Path(folder)  # 선택된 폴더를 기본 경로로 설정
            self.analyze_folder_extensions(folder)  # 0922-2-2
            self.update_status() # 0922-7 상태 업데이트를 위해 추가

    # 0922-2-3 analyze_folder_extensions 추가, 폴더 선택 시 동적으로 체크박스를 생성
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

    # 0922-3-11 _on_mousewheel 함수 추가
    def _on_mousewheel(self, event):
        self.checkbox_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # 0922-3-12 수정
    # 0922-2-4 create_extension_checkboxes 추가, 폴더 선택 시 동적으로 체크박스를 생성
    def create_extension_checkboxes(self, extensions, has_no_extension):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.extension_vars = {}

        # 0922-5-1 전체 선택/해제 토글 버튼 추가
        self.toggle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.scrollable_frame, text="전체 선택/해제", variable=self.toggle_var,
                        command=self.toggle_all, style="Transparent.TCheckbutton").pack(anchor="w")

        for ext in extensions:
            var = tk.BooleanVar(value=False) # 0922-5-2 기본값을 False로 변경
            self.extension_vars[ext] = var
            ttk.Checkbutton(self.scrollable_frame, text=ext, variable=var,
                            command=self.update_status,
                            style="Transparent.TCheckbutton").pack(anchor="w")

        if has_no_extension:
            var = tk.BooleanVar(value=False) # 0922-5-2 기본값을 False로 변경
            self.extension_vars["No Extension"] = var
            ttk.Checkbutton(self.scrollable_frame, text="확장자 없는 파일", variable=var, style="Transparent.TCheckbutton").pack(anchor="w") # 0922-3-14 style="Transparent.TCheckbutton" 추가

        # 0922-3-14 확장자가 10개 이상일 때만 스크롤바 표시
        if len(extensions) + (1 if has_no_extension else 0) > 10:
            self.checkbox_scrollbar.pack(side="right", fill="y")
            self.checkbox_canvas.configure(height=200)  # 캔버스 높이 제한
        else:
            self.checkbox_scrollbar.pack_forget()
            self.checkbox_canvas.configure(height=0)  # 높이 제한 해제

        self.checkbox_canvas.update_idletasks()
        self.checkbox_canvas.configure(scrollregion=self.checkbox_canvas.bbox("all"))

    def toggle_all(self):   # 0922-5-3
        state = self.toggle_var.get()
        for var in self.extension_vars.values():
            var.set(state)
        self.update_status() # 0922-7 상태 업데이트를 위해 추가

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
        # 0922-2-5 get_selected_extensions 함수 전체 수정
        # # 이 부분은 GUI에서 선택된 확장자를 반환하도록 구현해야 합니다.
        # extensions = self.extensions_entry.get().strip()
        # if not extensions:
        #     return None  # 입력이 없으면 모든 파일 표시
        # return [ext.strip() for ext in extensions.split(' ') if ext.strip()]

        # 0922-2-6 get_selected_extensions 새로운 코드, 체크된 확장자만 반환
        return [ext for ext, var in self.extension_vars.items() if var.get()]


    # 0921-2-2
    def get_merge_extensions(self):
        extensions = self.merge_extensions.get().strip()
        if not extensions:
            return None
        return [ext.strip() for ext in extensions.split(',') if ext.strip()]

    # 0922-6-2
    def add_exclude_file(self):
        file_path = filedialog.askopenfilename(initialdir=self.base_folder)
        if file_path:
            file_name = os.path.basename(file_path)  # 파일명과 확장자만 가져오기
            current = self.exclude_files.get("1.0", tk.END).strip()
            if current:
                self.exclude_files.insert(tk.END, f"\n{file_name}")
            else:
                self.exclude_files.insert(tk.END, file_name)

    # 0922-6-3
    def add_exclude_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.base_folder)
        if folder_path and self.base_folder:
            try:
                relative_path = Path(folder_path).relative_to(self.base_folder)
                relative_path_str = str(relative_path).replace('\\', '/')  # Windows 경로 구분자 변경
                current = self.exclude_files.get("1.0", tk.END).strip()
                if current:
                    self.exclude_files.insert(tk.END, f"\n/{relative_path_str}")
                else:
                    self.exclude_files.insert(tk.END, f"/{relative_path_str}")
            except ValueError:
                messagebox.showwarning("경고", "선택한 폴더가 기본 폴더 외부에 있습니다.")

    # 0921-2-3
    def get_exclude_files(self):
        files = self.exclude_files.get("1.0", tk.END).strip()
        if not files:
            return [], []   # 0922-4-1
        items = [item.strip() for item in files.split('\n') if item.strip()]     # 0922-4-2
        exclude_files = [item for item in items if not item.startswith('/')]    # 0922-4-3
        exclude_folders = [item[1:] for item in items if item.startswith('/')]  # 0922-4-4
        return exclude_files, exclude_folders   # 0922-4-5

    # 0922-4-6
    def is_excluded(self, path, exclude_files, exclude_folders):
        file_name = os.path.basename(path)
        if file_name in exclude_files:
            return True

        relative_path = os.path.relpath(path, self.folder_path.get())
        relative_path = relative_path.replace('\\', '/')  # Windows 경로 구분자 변경
        for folder in exclude_folders:
            if relative_path.startswith(folder):
                return True

        return False

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
        # merge_extensions = self.get_merge_extensions()    # 0922-2-9 selected_extensions 만 사용하여 merege 진행
        exclude_files, exclude_folders = self.get_exclude_files()

        if not selected_extensions: # 0922-2-10
            messagebox.showwarning("경고", "병합할 파일 확장자를 선택해주세요.")
            return

        # 0921-6-2 저장할 파일 명 변경을 위해 추가
        now = datetime.now()    #0921-6-3 현재 날짜
        date_time = now.strftime("%y%m%d-%H%M") #0921-6-4 시간
        folder_name = os.path.basename(self.folder_path.get())  #0921-6-5 선택된 폴더 이름 추출
        file_name = f"{date_time}-{folder_name}-merged.md" #0921-6-6 새로운 파일 이름 생성

        output_file = os.path.join(self.folder_path.get(), file_name)
        encoding = 'utf-8'

        try:
            with open(output_file, 'w', encoding=encoding) as outfile:
                self.write_directory_content(self.folder_path.get(), outfile, selected_extensions, exclude_files, exclude_folders, encoding) # 0922-2-11 merge_extensions 삭제
                # 0922-4-9 exclude_folders 추가
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"병합된 파일이 {output_file}에 저장되었습니다.")
            self.update_status()
        except Exception as e:
            self.output.delete(1.0, tk.END)
            self.output.insert(tk.END, f"파일 병합 중 오류 발생: {str(e)}")

    # 0921-2-5 # 0922-4-8 반복문 전체 수정
    def write_directory_content(self, directory, outfile, selected_extensions, exclude_files, exclude_folders, encoding,
                                level=0):
        normalized_directory = directory.replace('\\', '/')  # 경로 정규화
        relative_directory = os.path.relpath(normalized_directory, self.folder_path.get()).replace('\\', '/')

        if relative_directory in exclude_folders:
            return  # 제외된 폴더면 완전히 건너뛰기

        outfile.write(f"{'#'} 디렉토리: {normalized_directory}\n\n")

        for entry in sorted(os.scandir(directory), key=lambda e: (not e.is_dir(), e.name.lower())):
            normalized_path = entry.path.replace('\\', '/')  # 경로 정규화
            relative_path = os.path.relpath(normalized_path, self.folder_path.get()).replace('\\', '/')

            if entry.is_dir():
                self.write_directory_content(entry.path, outfile, selected_extensions, exclude_files, exclude_folders,
                                             encoding, level + 1)
            elif entry.is_file():
                _, ext = os.path.splitext(entry.name)
                if ext in selected_extensions:
                    if entry.name in exclude_files:
                        outfile.write(f"{'##'} 파일 (내용 생략됨): {normalized_path}\n\n")
                    else:
                        outfile.write(f"{'##'} 파일: {normalized_path}\n")
                        try:
                            with open(entry.path, 'r', encoding=encoding) as infile:
                                content = infile.read()
                            outfile.write(f"```{ext[1:]}\n")  # 확장자 표시
                            outfile.write(content)
                            outfile.write("\n```\n\n")
                        except UnicodeDecodeError:
                            outfile.write(f"(이 파일은 {encoding} 인코딩으로 읽을 수 없습니다.)\n\n")

        outfile.write("\n")

    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.master, relief=tk.SUNKEN, padding=(2, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_left = ttk.Label(self.status_bar, anchor=tk.W)
        self.status_left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.status_right = ttk.Label(self.status_bar, text="제작자: hoonee-math", anchor=tk.E)
        self.status_right.pack(side=tk.RIGHT)

        self.update_status()

    def update_status(self):
        if not self.folder_path.get():
            self.status_left.config(text="폴더를 선택해주세요")
            return

        selected_extensions = self.get_selected_extensions()
        file_count = 0
        folder_count = 0

        for root, dirs, files in os.walk(self.folder_path.get()):
            folder_count += len(dirs)
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in selected_extensions or (ext == '' and "No Extension" in selected_extensions):
                    file_count += 1

        status_text = f"선택된 파일: {file_count}개, 폴더: {folder_count}개"
        self.status_left.config(text=status_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = CMDPowerShellGUI(root)
    root.mainloop()