import tkinter as tk

root = tk.Tk()
root.geometry(f"500x400+{int((1440-500)/2)}+{int((950-400)/2)}")
root.title("Typing Effect")


# txt = "Fuck you all motherfuckers"
txt = '''Jupyter Notebooks:

In the data science community, using Jupyter notebooks with %autoreload is a common workaround for achieving something close to hot reloading in an interactive environment. This doesn’t apply to Tkinter GUIs, but it’s a frequently used approach in Python development for rapid feedback.
A fully stable and comprehensive hot-reloading solution specifically for Tkinter does not yet exist as a mainstream package. This is partly because Python and Tkinter’s architecture make it challenging to implement in a way that is both smooth and cross-platform.

Building a dedicated module for hot reloading in Tkinter would be quite innovative and could fill a gap in Python GUI development. If you package it, refine it, and share it with the community, it could attract contributors or even evolve into a tool widely used by other Tkinter developers.




'''
text = ''
count = 0

label = tk.Label(root, text=txt, font=('Times New Roman', 20, 'bold'), wraplength=700, justify='left', background='red')
label.pack(expand=True)


def slider(label):
    global count, text

    if count >= len(txt):
        count -=1
        label.config(text=text)

    else:
        text += txt[count]
        label.config(text=text)
    count += 1
    label.after(100, lambda label = label :slider(label))


slider(label)


root.mainloop()