import tkinter as tk
from gui import FutoshikiGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = FutoshikiGUI(root)
    if app.input_files: 
        app.preview_input()
    root.mainloop()