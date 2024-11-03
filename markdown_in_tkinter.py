import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Selectable Text in Label")

# Create a Text widget styled as a Label
text_widget = tk.Text(root, wrap="word", font=("Arial", 12), height=1, bg=root.cget("bg"), borderwidth=0)
text_widget.pack(pady=10)

# Insert some text
text_widget.insert(tk.END, "This is some copyable text. You can select and copy this text.")
text_widget.config(state=tk.DISABLED)  # Make it read-only

# Allow selection of text
def enable_selection(event):
    text_widget.config(state=tk.NORMAL)
    text_widget.tag_add("sel", "1.0", "end")  # Select all text
    text_widget.mark_set("insert", "1.0")  # Move cursor to start
    text_widget.see("insert")  # Scroll to insert
    text_widget.config(state=tk.DISABLED)  # Make it read-only again

# Bind left mouse button click to enable text selection
text_widget.bind("<Button-1>", enable_selection)

root.mainloop()
