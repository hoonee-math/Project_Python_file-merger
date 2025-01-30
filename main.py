import tkinter as tk
from src.gui.main_window import MainWindow

def main():
    """메인 애플리케이션 실행"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()