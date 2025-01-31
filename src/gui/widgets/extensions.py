import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Set, Callable, Optional


class ExtensionsFrame(ttk.Frame):
    """파일 확장자 선택을 위한 프레임 클래스"""

    def __init__(self, master, on_selection_change: Callable[[], None]):
        """초기화

        Args:
            master: 부모 위젯
            on_selection_change (Callable[[], None]): 선택 변경 시 호출될 콜백
        """
        super().__init__(master)
        self._on_selection_change_callback = on_selection_change
        self._extension_vars: Dict[str, tk.BooleanVar] = {}
        self._toggle_var: Optional[tk.BooleanVar] = None

        # UI 초기화
        self._create_widgets()
        self._setup_layout()
        self._setup_event_bindings()

    def _create_widgets(self) -> None:
        """위젯 생성"""
        # 레이블
        self._title_label = ttk.Label(self, text="파일 확장자 선택")

        # 체크박스를 포함할 프레임
        self._checkbox_frame = ttk.Frame(self)

        # 스크롤 가능한 캔버스
        self._canvas = tk.Canvas(self._checkbox_frame)
        self._scrollbar = ttk.Scrollbar(
            self._checkbox_frame,
            orient="vertical",
            command=self._canvas.yview
        )

        # 실제 체크박스들이 들어갈 프레임
        self._scrollable_frame = ttk.Frame(self._canvas)

    def _setup_layout(self) -> None:
        """레이아웃 설정"""
        # 메인 레이블
        self._title_label.pack(anchor='w', pady=(10, 5))

        # 체크박스 프레임
        self._checkbox_frame.pack(fill=tk.BOTH, expand=True)

        # 캔버스와 스크롤바
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.pack(side="right", fill="y")

        # 스크롤 가능한 프레임을 캔버스에 추가
        self._canvas.create_window(
            (0, 0),
            window=self._scrollable_frame,
            anchor="nw"
        )

    def _setup_event_bindings(self) -> None:
        """이벤트 바인딩 설정"""
        self._scrollable_frame.bind(
            "<Configure>",
            self._on_frame_configure
        )
        self._canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)

    def _on_frame_configure(self, event=None) -> None:
        """프레임 크기 변경 시 스크롤 영역 업데이트"""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_mousewheel(self, event) -> None:
        """마우스 휠 이벤트 처리"""
        try:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            # 일부 시스템에서는 event.delta가 다르게 동작할 수 있음
            pass

    def _create_checkboxes(self, extensions: Set[str], has_no_extension: bool) -> None:
        """체크박스 생성

        Args:
            extensions (Set[str]): 확장자 집합
            has_no_extension (bool): 확장자 없는 파일 존재 여부
        """
        # 기존 체크박스 제거
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()

        self._extension_vars.clear()

        # 전체 선택/해제 토글
        self._toggle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self._scrollable_frame,
            text="전체 선택/해제",
            variable=self._toggle_var,
            command=self._toggle_all,
            style="Transparent.TCheckbutton"
        ).pack(anchor="w")

        # 확장자별 체크박스
        for ext in sorted(extensions):
            var = tk.BooleanVar(value=False)
            self._extension_vars[ext] = var
            ttk.Checkbutton(
                self._scrollable_frame,
                text=ext,
                variable=var,
                command=self._on_selection_change_callback,
                style="Transparent.TCheckbutton"
            ).pack(anchor="w")

        # 확장자 없는 파일 체크박스
        if has_no_extension:
            var = tk.BooleanVar(value=False)
            self._extension_vars["No Extension"] = var
            ttk.Checkbutton(
                self._scrollable_frame,
                text="확장자 없는 파일",
                variable=var,
                style="Transparent.TCheckbutton"
            ).pack(anchor="w")

    def _update_scrollbar_visibility(self, item_count: int) -> None:
        """스크롤바 표시 여부 업데이트

        Args:
            item_count (int): 항목 수
        """
        if item_count > 10:
            self._scrollbar.pack(side="right", fill="y")
            self._canvas.configure(height=200)
        else:
            self._scrollbar.pack_forget()
            self._canvas.configure(height=0)

        self._canvas.update_idletasks()
        self._on_frame_configure()

    def _toggle_all(self) -> None:
        """전체 선택/해제 토글"""
        if not self._toggle_var:
            return

        try:
            state = self._toggle_var.get()
            for var in self._extension_vars.values():
                var.set(state)
            self._on_selection_change_callback()
        except Exception as e:
            messagebox.showerror("오류", f"선택 상태 변경 중 오류 발생: {str(e)}")

    # Public Interface Methods
    def update_extensions(self, extensions: Set[str], has_no_extension: bool) -> None:
        """확장자 목록 업데이트

        Args:
            extensions (Set[str]): 확장자 집합
            has_no_extension (bool): 확장자 없는 파일 존재 여부
        """
        try:
            # 이전 선택 상태 저장
            previous_selections = {
                ext: var.get()
                for ext, var in self._extension_vars.items()
            }

            # 새로운 체크박스 생성
            self._create_checkboxes(extensions, has_no_extension)
            self._update_scrollbar_visibility(len(extensions) + (1 if has_no_extension else 0))

            # 이전 선택 상태 복원 (새로운 확장자는 기본값 False)
            for ext, var in self._extension_vars.items():
                if ext in previous_selections:
                    var.set(previous_selections[ext])

            # 전체 선택/해제 상태 업데이트
            if self._toggle_var:
                all_selected = all(var.get() for var in self._extension_vars.values())
                self._toggle_var.set(all_selected)

        except Exception as e:
            messagebox.showerror("오류", f"확장자 목록 업데이트 중 오류 발생: {str(e)}")
    def get_selected_extensions(self) -> List[str]:
        """선택된 확장자 목록 반환

        Returns:
            List[str]: 선택된 확장자 목록
        """
        try:
            return [ext for ext, var in self._extension_vars.items() if var.get()]
        except Exception as e:
            messagebox.showerror("오류", f"선택된 확장자 확인 중 오류 발생: {str(e)}")
            return []