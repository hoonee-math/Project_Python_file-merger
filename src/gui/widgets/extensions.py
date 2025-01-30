import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Set, Callable


class ExtensionsFrame(ttk.Frame):
    """파일 확장자 선택을 위한 프레임 클래스"""

    def __init__(self, master, on_selection_change: Callable[[], None]):
        """
        Args:
            master: 부모 위젯
            on_selection_change (Callable[[], None]): 선택 변경 시 호출될 콜백
        """
        super().__init__(master)
        self.on_selection_change = on_selection_change
        self.extension_vars: Dict[str, tk.BooleanVar] = {}

        self._create_widgets()

    def _create_widgets(self):
        """위젯 생성 및 배치"""
        # 레이블
        ttk.Label(self, text="파일 확장자 선택").pack(anchor='w', pady=(10, 5))

        # 체크박스를 포함할 프레임
        self.checkbox_frame = ttk.Frame(self)
        self.checkbox_frame.pack(fill=tk.BOTH, expand=True)

        # 스크롤 가능한 캔버스
        self.canvas = tk.Canvas(self.checkbox_frame)
        self.scrollbar = ttk.Scrollbar(
            self.checkbox_frame, orient="vertical",
            command=self.canvas.yview
        )

        # 실제 체크박스들이 들어갈 프레임
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # 캔버스에 프레임 추가
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 마우스 휠 이벤트 바인딩
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

        # 패킹
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        """마우스 휠 이벤트 핸들러"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def update_extensions(self, extensions: Set[str], has_no_extension: bool):
        """확장자 목록 업데이트

        Args:
            extensions (Set[str]): 확장자 집합
            has_no_extension (bool): 확장자 없는 파일 존재 여부
        """
        # 기존 체크박스 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.extension_vars.clear()

        # 전체 선택/해제 토글
        self.toggle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.scrollable_frame,
            text="전체 선택/해제",
            variable=self.toggle_var,
            command=self._toggle_all,
            style="Transparent.TCheckbutton"
        ).pack(anchor="w")

        # 확장자별 체크박스 생성
        for ext in sorted(extensions):
            var = tk.BooleanVar(value=False)
            self.extension_vars[ext] = var
            ttk.Checkbutton(
                self.scrollable_frame,
                text=ext,
                variable=var,
                command=self.on_selection_change,
                style="Transparent.TCheckbutton"
            ).pack(anchor="w")

        # 확장자 없는 파일 체크박스
        if has_no_extension:
            var = tk.BooleanVar(value=False)
            self.extension_vars["No Extension"] = var
            ttk.Checkbutton(
                self.scrollable_frame,
                text="확장자 없는 파일",
                variable=var,
                style="Transparent.TCheckbutton"
            ).pack(anchor="w")

        # 스크롤바 표시 여부 결정
        if len(extensions) + (1 if has_no_extension else 0) > 10:
            self.scrollbar.pack(side="right", fill="y")
            self.canvas.configure(height=200)
        else:
            self.scrollbar.pack_forget()
            self.canvas.configure(height=0)

        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_selected_extensions(self) -> List[str]:
        """선택된 확장자 목록 반환"""
        return [ext for ext, var in self.extension_vars.items() if var.get()]

    def _toggle_all(self):
        """전체 선택/해제 토글"""
        state = self.toggle_var.get()
        for var in self.extension_vars.values():
            var.set(state)
        self.on_selection_change()