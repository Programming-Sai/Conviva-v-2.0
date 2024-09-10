import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES

# Create the main application window
root = TkinterDnD.Tk()  # Use TkinterDnD.Tk() instead of tk.Tk()
root.title("Drag and Drop Files")
root.geometry("500x300")

# Define what happens when a file is dropped
def drop(event):
    file_path = event.data
    label.config(text=f"File Dropped:\n{file_path}")
    print("\n\n", file_path, "\n\n")

# Create a label widget where files can be dropped
label = tk.Label(root, text="Drag and drop a file here", bg="lightgray", width=50, height=10)
label.pack(padx=20, pady=20)

# Bind the drop event to the label widget
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', drop)

# Run the application
root.mainloop()
