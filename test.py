# import tkinter as tk
# from tkinter import filedialog

# class RegularTkWindow(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("Regular Tk Window")
#         self.geometry("300x200")

#         self.btn = tk.Button(self, text="Open File (Tk)", command=self.upload_file)
#         self.btn.pack(pady=20)

#     def upload_file(self):
#         self.after(100, self.open_file_dialog)  # Using `after` to avoid UI freezes

#     def open_file_dialog(self):
#         file_path = filedialog.askopenfilename(
#         #     defaultextension="*.*",
#             filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Audio", "*.mp3 *.wav")]
#         )
#         if file_path:  # Ensure it's not empty
#             self.on_file_selected(file_path)

#     def on_file_selected(self, file_path):
#         print("Tk Window Selected file:", file_path)

# if __name__ == "__main__":
#     app = RegularTkWindow()
#     app.mainloop()


import tkinter as tk
from tkinter import filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD

class DndTkWindow(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("TkinterDnD Window")
        self.geometry("300x200")

        self.btn = tk.Button(self, text="Open File (TkinterDnD)", command=self.upload_file)
        self.btn.pack(pady=20)

        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.on_drop)

    def upload_file(self):
        self.after(100, self.open_file_dialog)  # Delay to prevent UI freezes

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension="*.*",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Audio", "*.mp3 *.wav")]
        )
        if file_path:
            self.on_file_selected(file_path)

    def on_drop(self, event):
        file_path = event.data.strip()  # Get dropped file path
        if file_path:
            self.on_file_selected(file_path)

    def on_file_selected(self, file_path):
        print("TkinterDnD Window Selected file:", file_path)

if __name__ == "__main__":
    app = DndTkWindow()
    app.mainloop()
