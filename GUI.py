import shutil
import customtkinter as ctk
import sounddevice as sd
import librosa
from PIL import Image, ImageTk
import os
import random
import subprocess
import threading
import tkinter as tk
from tkinter import PhotoImage, TclError
import time
from llm_processing import *
from tkinterdnd2 import TkinterDnD, DND_ALL
from pathlib import Path
import json
from datetime import datetime 
from tkinter import messagebox





class GUI(TkinterDnD.Tk):  # Multiple inheritance
    def __init__(self):
        # Initialize both parent classes
        super().__init__()
        ctk.set_appearance_mode('dark')
        self.title('Conviva 2.0')
        self.size = (1200, 700)
        self.purple_palette = [
            "#E6E6FA",  # Lavender
            "#E0B0FF",  # Mauve
            "#C8A2C8",  # Lilac
            "#9966CC",  # Amethyst
            "#7851A9",  # Royal Purple
            "#9C51B6",  # Purple Plum
            "#673AB7",  # Deep Purple
            "#614051",  # Eggplant
            "#2E003E",  # Midnight Purple
            "#9932CC",  # Dark Orchid
            "#4B0082",  # Indigo
            "#2C003E",  # Dark Grape
            "#1D0033",  # Dark Violet
            "#12002C",  # Deep Eggplant
            "#0D001A"   # Almost Black Purple
        ]

        self.file_type_colors = {
            'txt': 'blue',
            'md': 'gray',
            'png': 'blue',
            'jpg': 'blue',
            'jpeg': 'blue',
            'pdf': 'red',
            'doc': 'blue',
            'docx': 'blue',
            'xls': 'green',
            'xlsx': 'green',
            'ppt': 'purple',
            'pptx': 'purple',
            'mp3': 'yellow',
            'wav': 'yellow',
            'mp4': 'blue',
            'avi': 'green',
            'mkv': 'green',
            'zip': 'green',
            'rar': 'yellow',
            'exe': 'red',
            'bat': 'red',
            'html': 'blue',
            'htm': 'blue',
            'py': 'green',
            'js': 'blue',
            'java': 'blue'
        }
        
        self.utilities = AI_Utilties(self.gui_title_function ,Conversation(self.gui_title_function))


        self.current_page_index = 0
        self.file_tag = None
        self.pages = [ self.speech_chat, self.text_chat, ]
        self.conversation = {}
        self.current_conversation = ''

        # Define Some Other shades Of Purple.

        self.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.winfo_screenwidth()/2)-int(self.size[0]/2)}+{int(self.winfo_screenheight()/2)-int(self.size[1]/2)-50}")
        self.maxsize(1200, 700)

        self.page_frame = tk.Frame(self)
        
        self.speech_chat_frame = tk.Frame(self.page_frame)
        self.main_speech_content = tk.Frame(self.speech_chat_frame, )
        self.speech_body = tk.Frame(self.main_speech_content, background=self.purple_palette[1])

        self.text_chat_frame = tk.Frame(self.page_frame)
        self.main_text_content = tk.Frame(self.text_chat_frame, )
        self.text_body = tk.Frame(self.main_text_content, background=self.purple_palette[8])

        self.load_page()
        full_screen=False
        self.bind("<Command-b>", self.toggle_side_panel)
        self.bind("<Control-b>", self.toggle_side_panel)
        self.bind("<Configure>", self.on_resize)
        self.full_screen = False  

        self.bind("<Command-f>", self.toggle_fullscreen)
        self.bind("<Control-f>", self.toggle_fullscreen)

        self.bind("<Command-n>", self.toggle_conversation)
        self.bind("<Control-n>", self.toggle_conversation)

        self.bind("<Command-Shift-X>", self.clear_history)
        self.bind("<Control-Shift-X>", self.clear_history)

        
        self.mainloop()


    def gui_title_function(self):
        title = None
        def title_callback(input_title):
            nonlocal title
            title = input_title

        self.conversation_modal(callback=title_callback)  
        self.modal.wait_window()
        return title

    def toggle_fullscreen(self, event=None):
        self.full_screen = not self.full_screen
        self.attributes('-fullscreen', self.full_screen)

    def load_page(self):
        self.pages[self.current_page_index]()
        self.page_frame.pack(fill='both', expand=True)
        self.nav_buttons()

    def clear_page(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    def speech_chat(self):
        try:
            self.speech_chat_frame = tk.Frame(self.page_frame)
            self.side_panel_creator(self.speech_chat_frame)
            self.main_speech_content = tk.Frame(self.speech_chat_frame, )
            self.main_speech_content_content()
            self.main_speech_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            self.speech_chat_frame.pack(fill='both', expand=True)
        except:
            print("Not In Existance (Speech Chat)")

    def side_panel_creator(self, frame):
        self.side_panel_visible = True
        self.side_panel = tk.Frame(frame)
        self.side_panel_content()
        self.side_panel.place(x=0, y=0, relheight=1.0)

    def toggle_side_panel(self, e):
        if self.side_panel_visible:
            # Hide the side panel
            self.side_panel.place_configure(relwidth=0)
            if self.main_speech_content is not None and self.main_speech_content.winfo_exists():
                self.main_speech_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            if self.main_text_content is not None and self.main_text_content.winfo_exists():
                self.main_text_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            self.side_panel_visible = False
            self.main_menu_button_visible = True
            self.toggle_main_menu_button()
        else:
            # Show the side panel
            self.side_panel.place_configure(relwidth=0.3)
            if self.main_speech_content is not None and self.main_speech_content.winfo_exists():
                self.main_speech_content.place_configure(relx=0.3, relwidth=0.7, rely=0, relheight=1.0)
            if self.main_text_content is not None and self.main_text_content.winfo_exists():
                self.main_text_content.place_configure(relx=0.3, relwidth=0.7, rely=0, relheight=1.0)
            self.side_panel_visible = True
            self.main_menu_button_visible = False
            self.toggle_main_menu_button()


    def side_panel_content(self):
        self.menu_image = ctk.CTkImage(
            dark_image=Image.open("Images/Menu.png"), 
            light_image=Image.open("Images/Menu.png") 
        )

        self.new_conversation_image = ctk.CTkImage(
            dark_image=Image.open("Images/NewConversation.png"), 
            light_image=Image.open("Images/NewConversation.png") 
        )

        self.clear_history_image = ctk.CTkImage(
            dark_image=Image.open("Images/Clear.png"), 
            light_image=Image.open("Images/Clear.png") 
        )

        header = tk.Frame(self.side_panel, background=self.purple_palette[13])

        toggle_button = ctk.CTkButton(header, text='', image=self.menu_image, width=100, fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], command=lambda e=None :self.toggle_side_panel(e))
        toggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)

        new_conversation = ctk.CTkButton(header, text='', image=self.new_conversation_image, width=100, fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], command=self.toggle_conversation)
        new_conversation.place(relx=0.65, rely=0, relwidth=0.3, relheight=1.0, anchor='ne')

        clear_history = ctk.CTkButton(header, text='', image=self.clear_history_image, width=100, fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], command=self.clear_history)
        clear_history.place(relx=1, rely=0, relwidth=0.3, relheight=1.0, anchor='ne')

        header.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        self.conversations = ctk.CTkScrollableFrame(self.side_panel, fg_color=self.purple_palette[6])

        self.place_conversations_list()

        self.conversations.place(relx=0, rely=0.1, relwidth=1, relheight=1)

    def clear_history(self, e=None):
        response = messagebox.askyesno("Confirm Deletion", f'Are you sure you want to clear your history?')
        if response:
            try:
                folder_path = "Conversations"
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)  
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  
                self.utilities.conversation.conversation_history = []
                self.conversation_title.configure(text="")
                self.place_conversations_list()
                self.get_conversation_content_for_text_chat()
                self.scroll_frame_content()

            except Exception as e:
                messagebox.showerror(f"Error: {e}")

    def place_conversations_list(self):
        for widget in self.conversations.winfo_children():
            widget.destroy()

        c = self.get_conversations()
        

        for i in c:
            text = i.replace(".json", "")[45:]
            if text.startswith('.'):
                continue

            # Create a frame to hold the label and button
            conversation_frame = ctk.CTkFrame(self.conversations, fg_color="transparent", width=100)  
            conversation_frame.pack(fill='both', pady=5, padx=5)

            # Label inside the frame
            conversation_label = ctk.CTkLabel(
                conversation_frame, 
                # text=text.replace("-", " "), 
                text=self.truncate_text(text.replace("-", " "), 30), 
                fg_color=self.purple_palette[5], 
                corner_radius=10, 
                anchor="w",
                # width=100
            )
            # conversation_label.place(relx=0, rely=0, relwidth=0.7, anchor='w')
            conversation_label.pack(side="left", fill="both", expand=True, ipady=10, ipadx=10)

            # Delete button inside the frame
            delete_button = ctk.CTkButton(
                conversation_frame, 
                text="✖", 
                width=30, 
                height=30, 
                fg_color="red", 
                command=self.create_callback(self.delete_conversation, i, c)
            )
            # delete_button.place(relx=0.8, rely=0, anchor="center")
            delete_button.pack(side="right", padx=5)

            edit_button = ctk.CTkButton(
                conversation_frame, 
                text="✎", 
                width=30, 
                height=30, 
                fg_color=self.purple_palette[10], 
                command=self.create_callback(self.conversation_modal, True, i)
            )
            # edit_button.place(relx=0.9, rely=0, anchor="center")
            edit_button.pack(side="right", padx=5)

            # Bind actions to the label
            conversation_label.bind("<Button-1>", self.create_callback(self.open_conversation, i))
            
            # Context menu setup
            context_menu = tk.Menu(conversation_label, tearoff=0)
            context_menu.add_command(label="Open        ", command=self.create_callback(self.open_conversation, i))
            context_menu.add_command(label="Edit        ", command=self.create_callback(self.conversation_modal, True, i))
            context_menu.add_separator()
            context_menu.add_command(label="Delete      ", foreground='red', command=self.create_callback(self.delete_conversation, i, c))

            # Bind right-click menu to the label
            conversation_label.bind("<Double-1>", self.create_context_menu_callback(context_menu))
            conversation_label.bind("<Button-3>", self.create_context_menu_callback(context_menu))



        tk.Frame(self.conversations, height=100, background=self.purple_palette[6]).pack(fill='both')


    def truncate_text(self, text, length=20):
        return text[:length] + "..." if len(text) > length else text

    def create_callback(self, func, *args):
        def callback(*_):
            func(*args)
        return callback


    def create_context_menu_callback(self, menu):
        def callback(event):
            self.show_context_menu(event, menu)
        return callback




    def main_speech_content_content(self):
        # Load image and setup header
        self.topbar(self.main_speech_content)

        # Setup body
        self.speech_body = tk.Frame(self.main_speech_content, background=self.purple_palette[13])

        self.pulser = Pulser(self, self.speech_body, (self.purple_palette[13], self.purple_palette[13], self.purple_palette[13], self.purple_palette[13]) , corner_radius=200, border_width=2, border_color=self.purple_palette[9]).pack_frame()

        self.pulser.drop_target_register(DND_ALL)
        self.pulser.dnd_bind('<<Drop>>', self.handleDropEvent)

        
        # Initialize widgets but don't pack them yet
        self.chatbar(self.speech_body)

        self.speech_body.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)




    def topbar(self, frame):
        self.menu_image = ctk.CTkImage(
            dark_image=Image.open("Images/Menu.png"), 
            light_image=Image.open("Images/Menu.png")
        )

        header = tk.Frame(frame, background=self.purple_palette[13])
        self.maintoggle_button = ctk.CTkButton(header, text='', image=self.menu_image, width=100, 
                                            fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], 
                                            command=lambda e=None: self.toggle_side_panel(e))
        self.maintoggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)
        
        
        self.conversation_title = tk.Label(header, text='', bg=self.purple_palette[13], font=('Arial Black', 16, 'bold'))
        self.conversation_title.place(relx=1, rely=0, relwidth=0.5, relheight=1.0, anchor='ne')


        header.place(relx=0, rely=0, relwidth=1, relheight=0.1)


    def get_conversations(self):
        walk_gen = os.walk("Conversations")
        walk_list = list(walk_gen)
        root = walk_list[0][0]
        files = [os.path.join(root, i) for i in walk_list[0][2]] or []
        sorted_files = sorted(files, key=lambda x: self.extract_timestamp(x), reverse=True)
        return sorted_files

    
    def extract_timestamp(self, file_name):
        copy = file_name.replace("Conversations/", "")
        if copy.startswith("."):
            return ""
        return copy.split('_')[1] + "_" + copy.split('_')[2] + "_" + copy.split('_')[3]



    def open_conversation(self, conversation_to_open, e=None ):
        try:
            with open("Conversations/.current_conversation_file_name.txt", 'w') as f:
                f.write(conversation_to_open)

            with open(conversation_to_open, 'r') as file:
                self.utilities.conversation.conversation_history = json.load(file)
                self.conversation = self.utilities.conversation.conversation_history
                # print(json.dumps(self.utilities.conversation.conversation_history, indent=4))
            
            self.current_conversation = conversation_to_open[45:].replace('.json', "")
            self.conversation_title.configure(text=self.current_conversation.replace("-", " "))
            self.get_conversation_content_for_text_chat()
            self.auto_scroll_to_end()
        except:
            self.conversation = {}


    def get_conversation_content_for_text_chat(self):
        for item in self.scroll_frame.winfo_children():
            item.destroy()
        self.conversation = self.utilities.conversation.conversation_history
        # print("Cleared History Convo...", self.utilities.conversation.conversation_history, "\nCleared History Conversation Only: ", self.conversation)

        tk.Frame(self.scroll_frame, height=50).pack(side='top')
        for i in range(len(self.conversation)):
            if (
                self.conversation[i]['role'] == 'system' 
                or self.conversation[i]['role'] == 'tool'
            ):
                continue
            elif self.conversation[i]['role'] == 'user':
                self.input_label = ctk.CTkTextbox(
                    self.scroll_frame,
                    wrap="word",  # Similar to wraplength
                    fg_color=self.purple_palette[4],  # Background color
                    corner_radius=10,  # Rounded corners
                    font=("Arial", 14),  # Set font to match label style
                    width=int(self.wrap_length(0.5)),  # Match previous wrap length
                    height=5,  # Set height dynamically as needed
                )

                self.input_label.configure(state="normal")
                self.input_label.insert("1.0", self.conversation[i]['content'])
                self.input_label.configure(state="disabled") 
                self.adjust_textbox_height(self.input_label)
                self.input_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='e') 
            else:
                self.response_label = ctk.CTkTextbox(
                    self.scroll_frame,
                    wrap="word",  # Similar to wraplength
                    fg_color=self.purple_palette[6],  # Background color
                    corner_radius=10,  # Rounded corners
                    font=("Arial", 14),  # Set font to match label style
                    width=int(self.wrap_length(0.5)),  # Match previous wrap length
                    height=5,  # Set height dynamically as needed
                )

                self.response_label.configure(state="normal")
                self.response_label.insert("1.0", self.conversation[i]['content'])
                self.response_label.configure(state="disabled") 
                self.adjust_textbox_height(self.response_label)
                self.response_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='w') 

                
        self.auto_scroll_to_end()
        tk.Frame(self.scroll_frame, height=50).pack(side='bottom')


    def show_context_menu(self, event, menu):
        menu.post(event.x_root, event.y_root)


    def delete_conversation(self, conversation_to_delete, conversations):
        response = messagebox.askyesno("Confirm Deletion", f'Are you sure you want to delete "{conversation_to_delete.replace(".json", "")[45:].replace("-", " ")}"?')
        if response:
            try:
                os.remove(conversation_to_delete)
                conversations.remove(conversation_to_delete)
                with open("Conversations/.current_conversation_file_name.txt", 'w') as w:
                    w.write(conversations[0])
                # print(conversation_to_delete + " Deleted Successfully")
                self.place_conversations_list()
                self.scroll_frame_content()
            except Exception as e:
                messagebox.showerror(f"Error: {e}")

        

    

    def conversation_modal(self, edit=False, current_conversation_title_path="", callback=None):
        self.modal = tk.Toplevel(self)
        # Ensure it does not go fullscreen
        self.modal.withdraw()  # Hide the window while setting properties
        self.modal.attributes('-fullscreen', False)  
        self.modal.overrideredirect(False)  # Ensure normal window behavior
        
        # Make the modal the active window
        self.modal.grab_set()
        self.modal.title("")
        
        # Set size and center it
        width, height = 500, 200
        x_pos = (self.modal.winfo_screenwidth() // 2) - (width // 2)
        y_pos = (self.modal.winfo_screenheight() // 2) - (height // 2) - 50
        self.modal.geometry(f"{width}x{height}+{x_pos}+{y_pos}")

        # Show the modal after applying fixes
        self.modal.deiconify()

        self.modal.configure(bg=self.purple_palette[4])
        topFrame = tk.Frame(self.modal, background=self.purple_palette[9])
        middleFrame = tk.Frame(self.modal, )
        bottomFrame = tk.Frame(self.modal, background=self.purple_palette[10])

        topFrame.place(relx=0, rely=0, relwidth=1, relheight=0.2)
        middleFrame.place(relx=0, rely=0.2, relwidth=1, relheight=0.7)
        bottomFrame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)

        current_conversation_title = current_conversation_title_path.replace('.json', "")[45:] if not edit else "New Conversation Title"


        self.conversation_modal_title = ctk.CTkLabel(topFrame, text=current_conversation_title, fg_color=self.purple_palette[9], font=("Arial Black", 12, 'bold'), anchor='w')
        self.conversation_modal_title.pack(fill='both', expand=True, padx=10, side='left')

        
        self.conversation_modal_date = ctk.CTkLabel(topFrame, text=datetime.now().strftime("%b %d, %Y"), fg_color=self.purple_palette[9], font=("Arial Black", 12, 'bold'), anchor='e')
        self.conversation_modal_date.pack(fill='both', expand=True, padx=10, side='right')


        self.conversation_modal_text_box = ctk.CTkTextbox(middleFrame, fg_color=self.purple_palette[9], border_color=self.purple_palette[9], )
        self.textbox_placeholder("Enter Conversation Title Here...")
        self.conversation_modal_text_box.pack(fill='both', expand=True)


        self.conversation_modal_submit_button = ctk.CTkButton(bottomFrame, text="Submit", fg_color=self.purple_palette[13], hover_color=self.purple_palette[12], corner_radius=20, font=("Arial Black", 12, 'bold'), anchor='center', command=lambda: self.get_title_from_modal(edit, callback, current_conversation_title_path))
        self.conversation_modal_submit_button.pack(fill='both', pady=10, padx=10, side='right')
        

    def get_title_from_modal(self, edit, callback, current_conversation_title_path=""):
        title = self.conversation_modal_text_box.get(0.0, "end").strip()
        if title and edit:
            self.edit_title(title, current_conversation_title_path)
        if title and callback is not None:
            callback(title.replace(" ", "-"))
            print("New Title:", title)
        self.modal.destroy()

    def edit_title(self, title, current_conversation_title_path):
        path_title = current_conversation_title_path.replace("Conversations/", "").split("_")[-1].replace(".json", "")
        new_title_path = current_conversation_title_path.replace(path_title, title.replace(" ", "-"))
        os.rename(current_conversation_title_path, new_title_path)

        with open("Conversations/.current_conversation_file_name.txt", 'r+') as rw:
            curr = rw.read()
            if curr == current_conversation_title_path:
                rw.seek(0)
                rw.write(new_title_path)
                rw.truncate()
        self.place_conversations_list()
        self.scroll_frame_content()



    def textbox_placeholder(self, placeholder_text):
        self.conversation_modal_text_box.insert("1.0", placeholder_text)
        
        def clear_placeholder(event):
            if self.conversation_modal_text_box.get("1.0", "end-1c") == placeholder_text:
                self.conversation_modal_text_box.delete("1.0", "end")
        
        self.conversation_modal_text_box.bind("<FocusIn>", clear_placeholder)
        
        def set_placeholder(event):
            if self.conversation_modal_text_box.get("1.0", "end-1c") == "":
                self.conversation_modal_text_box.insert("1.0", placeholder_text)
        
        self.conversation_modal_text_box.bind("<FocusOut>", set_placeholder)

    def handleDropEvent(self, e):
        frame = e.widget  
        data = e.data.strip("{}")
        file_extension = Path(data).suffix.replace('.', '').upper()
        # Determine the label color based on file type
        color = self.file_type_colors.get(file_extension.lower(), 'gray')  # Default to gray if not found
        try:
            if not self.file_tag or not self.file_tag.winfo_exists():  # Create the label if it doesn't exist
                self.file_tag = ctk.CTkLabel(
                    self.speech_body if self.speech_body.winfo_exists() else self.text_body if self.text_body.winfo_exists() else frame,  # Or the relevant parent frame
                    font=('Arial Black', 16, 'bold'),
                    width=50,
                    height=70,
                    corner_radius=20,
                    text=file_extension,
                    fg_color=color
                )
            else:
                # Update existing label content and color
                self.file_tag.configure(text=file_extension, fg_color=color)
            # Ensure the label is visible
            self.file_tag.lift()  # Bring the label to the top
            self.file_tag.bind("<Button-1>", lambda e : self.file_tag.place_forget())
            self.place_file_tag(Size(self.winfo_screenwidth(), self.winfo_screenheight()))
        except TclError as error:
            print(f"Error handling drop event: {error}")



    def chatbar(self, frame):
        self.prompt = tk.StringVar()

        self.entry_widget = ctk.CTkEntry(frame, width=500, height=50, corner_radius=50, textvariable=self.prompt)
        self.textbox_widget = ctk.CTkTextbox(frame, width=500, height=100, corner_radius=10)


        self.entry_widget.focus_set()
        self.textbox_widget.focus_set()

        self.entry_widget.drop_target_register(DND_ALL)
        self.textbox_widget.drop_target_register(DND_ALL)

        self.entry_widget.dnd_bind('<<Drop>>', lambda e : self.handleDropEvent(e))
        self.textbox_widget.dnd_bind('<<Drop>>', lambda e : self.handleDropEvent(e))

        self.entry_widget.pack(pady=20)

        if frame == self.speech_body:
            self.entry_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<Command-Return>", self.get_prompt_from_text_box)
            self.textbox_widget.bind("<Control-Return>", self.get_prompt_from_text_box)
            self.entry_widget.bind("<Return>", self.get_prompt_from_text_box)
        if frame == self.text_body:
            self.entry_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<Command-Return>", self.get_prompt_from_text_box_text)
            self.textbox_widget.bind("<Control-Return>", self.get_prompt_from_text_box_text)
            self.entry_widget.bind("<Return>", self.get_prompt_from_text_box_text)
        



    def place_file_tag(self, e):
        if self.file_tag and self.file_tag.winfo_exists():
            width = e.width
            height = e.height
            window_width = self.winfo_width()
            window_height = self.winfo_height()
            # Check window size and reposition the label accordingly
            if window_width == width or window_height == height:
                self.file_tag.place(relx=0.28, rely=0.8)
            else:
                self.file_tag.place(relx=0.13, rely=0.8)

    def on_resize(self, event):
        # Reposition the file_tag when the window is resized
        e = Size(self.winfo_screenwidth(), self.winfo_screenheight())
        self.place_file_tag(e)

    def toggle_prompt_box(self, e):
        current_text = self.prompt.get()
        current_textbox_content = self.textbox_widget.get("1.0", tk.END).strip()

        # Switch to the textbox if text length exceeds 4
        if len(current_text) >= 75 and self.entry_widget.winfo_ismapped():
            # Switch to the textbox
            self.entry_widget.pack_forget()
            self.textbox_widget.delete("1.0", tk.END)  
            self.textbox_widget.insert("1.0", current_text)  # Insert new text
            self.textbox_widget.focus_set()
            self.textbox_widget.pack(pady=20)

        # Switch back to the entry widget if text length drops below 4
        elif len(current_textbox_content) < 75 and self.textbox_widget.winfo_ismapped():
            # Switch back to the entry widget
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.prompt.set(current_textbox_content)  
            self.entry_widget.pack(pady=20)

    def toggle_main_menu_button(self):
        if self.main_menu_button_visible:
            self.maintoggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0) 
        else:
            self.maintoggle_button.place_forget()

    def get_prompt_from_text_box(self, e):
        if self.entry_widget.winfo_ismapped(): 
            self.user_prompt = self.prompt.get()
            self.pulser.speech(ai_function_execution(self.user_prompt, tools, available_functions, self.utilities))
            self.prompt.set("")
        else:
            self.user_prompt = self.textbox_widget.get("1.0", tk.END).strip()
            self.pulser.speech(ai_function_execution(self.user_prompt, tools, available_functions, self.utilities))
            self.textbox_widget.delete("1.0", tk.END) 
            self.prompt.set("")
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.entry_widget.pack(pady=20)
        




    def text_chat(self):
        try:
            self.text_chat_frame = tk.Frame(self.page_frame)
            self.side_panel_creator(self.text_chat_frame)
            self.main_text_content = tk.Frame(self.text_chat_frame, )
            self.main_text_content_content()
            self.main_text_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            self.text_chat_frame.pack(fill='both', expand=True)
        except:
            print("Not In Existance (Text Chat)")




    def main_text_content_content(self):
        self.topbar(self.main_text_content)

        # Setup body
        self.text_body = tk.Frame(self.main_text_content, background=self.purple_palette[13])

        self.scroll_frame = ctk.CTkScrollableFrame(self.text_body, corner_radius=0, fg_color=self.purple_palette[13])
        

        self.scroll_frame.drop_target_register(DND_ALL)
        self.scroll_frame.dnd_bind('<<Drop>>', self.handleDropEvent)


        tk.Frame(self.scroll_frame, height=50, bg=self.purple_palette[13]).pack(side='top')
        self.scroll_frame_content()


        self.scroll_frame.pack(fill='both', expand=True)

        self.bind("<Command-Up>", self.scroll_to_top)
        self.bind("<Command-Down>", self.auto_scroll_to_end)
        self.bind("<Control-Up>", self.scroll_to_top)
        self.bind("<Control-Down>", self.auto_scroll_to_end)


        self.chatbar(self.text_body)

        self.button_frame = ctk.CTkFrame(self.text_body, corner_radius=50, width=60, height=60, fg_color=self.purple_palette[9])

        self.button_frame.place(relx=.85, rely=.8)
        self.button_frame.pack_propagate(False) 

        self.button_frame.bind("<Button-1>", self.scroll_button_method)

        self.scroll_button = ctk.CTkButton(self.button_frame, text="▲", font=("Segoe UI Symbol", 24), width=0, height=60, fg_color=self.purple_palette[9], hover_color=self.purple_palette[9], command=self.scroll_button_method)
        self.scroll_button.pack()

        self.text_body.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
        


    def scroll_frame_content(self):
        try:
            with open("Conversations/.current_conversation_file_name.txt", 'r') as f:
                current_file = f.read()
            self.open_conversation(conversation_to_open=current_file)
        except:
            pass
 
    



    def toggle_conversation(self, e=None):
        self.utilities.conversation.move_file = True
        self.utilities.conversation.create_new_conversation()
        print("New Conversation Should Start here!!!")
        self.utilities.conversation.move_file = False
        self.place_conversations_list()
        self.scroll_frame_content()

    



    def get_prompt_from_text_box_text(self, e):
        if not self.conversation or not self.utilities.conversation.conversation_history:
            self.toggle_conversation()
        if self.entry_widget.winfo_ismapped(): 
            self.user_prompt = self.prompt.get()
            self.prompt.set("")
        else:
            self.user_prompt = self.textbox_widget.get("1.0", tk.END).strip()
            self.textbox_widget.delete("1.0", tk.END) 
            self.prompt.set("")
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.entry_widget.pack(pady=20)

        self.input_label = ctk.CTkTextbox(
                    self.scroll_frame,
                    wrap="word",
                    fg_color=self.purple_palette[4], 
                    corner_radius=10,  
                    font=("Arial", 14),  
                    width=int(self.wrap_length(0.5)),  
                    height=5,  
                )

        self.input_label.configure(state="normal")
        self.input_label.insert("1.0", self.user_prompt)
        self.input_label.configure(state="disabled") 
        self.adjust_textbox_height(self.input_label)
        self.input_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='e') 
        
        self.response_label = ctk.CTkTextbox(
            self.scroll_frame,
            wrap="word",  # Similar to wraplength
            fg_color=self.purple_palette[6],  # Background color
            corner_radius=10,  # Rounded corners
            font=("Arial", 14),  # Set font to match label style
            width=int(self.wrap_length(0.5)),  # Match previous wrap length
            height=5,  # Set height dynamically as needed
        )

        # self.response_label.configure(state="disabled")
        self.response_label.configure(state="normal")
        self.response_label.insert("1.0",  ai_function_execution(self.user_prompt, tools, available_functions, self.utilities))
        self.response_label.configure(state="disabled") 
        self.adjust_textbox_height(self.response_label)
        self.response_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='w') 


        
        # self.slider(self.response_label)
        self.auto_scroll_to_end()



    def scroll_button_method(self, e=None):
        direction = self.scroll_button.cget('text')
        if direction == '▲':
            self.scroll_to_top()
            self.scroll_button.configure(text = '▼')
        else:
            self.auto_scroll_to_end()
            self.scroll_button.configure(text = '▲')



    def adjust_textbox_height(self, textbox):
        """Dynamically resize the textbox height based on its content, like a Label."""
        text_content = textbox.get("1.0", "end").strip()

        if not text_content:
            textbox.configure(height=1)
            return

        # Get the pixel width of the textbox
        textbox_width = textbox.winfo_width()  

        if textbox_width == 1:  # Sometimes width is 1 before rendering, so skip
            textbox.after(10, lambda: self.adjust_textbox_height(textbox))
            return

        # Estimate character width using font size (assuming monospaced font)
        char_width = 7  # Adjust based on actual font width in pixels
        max_chars_per_line = textbox_width // char_width

        # Count how many lines the text will take up
        lines = 0
        for paragraph in text_content.split("\n"):
            lines += max(1, -(-len(paragraph) // max_chars_per_line))  # Ceiling division

        # Approximate line height
        line_height = 18  # Depends on font size
        padding = 0  # Extra space

        new_height = ((lines * line_height) + padding) 
        new_height -= (0.1 * new_height)
        textbox.configure(height=new_height)
        self.auto_scroll_to_end()




    def auto_scroll_to_end(self, e=None):
        self.scroll_frame._scrollbar.set(*self.scroll_frame._parent_canvas.yview())
        self.scroll_frame._parent_canvas.configure(yscrollcommand=self.scroll_frame._scrollbar.set, scrollregion=self.scroll_frame._parent_canvas.bbox('all'))
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def scroll_to_top(self, event=None):
        self.scroll_frame._parent_canvas.yview_moveto(0.0)

    def wrap_length(self, rel_width):
        return rel_width * self.winfo_width()
        
    def nav_buttons(self):
        for idx in range(2):
            nav_button = ctk.CTkButton(
                self.page_frame, 
                text='Page ' + str(idx + 1), 
                command=lambda idx=idx: self.change_page(idx), 
                fg_color=self.purple_palette[-1],
                hover_color=self.purple_palette[4]
            )
            nav_button.pack(side='left', expand=True)

    def change_page(self, idx):
        self.clear_page(self.page_frame)
        self.set_current_page_index(idx)
        self.pages[self.current_page_index]()
        self.page_frame.pack(fill='both', expand=True)
        self.nav_buttons()

    def set_current_page_index(self, index):
        self.current_page_index = index

    def toast(self, message, position="top"):
        # Create a topmost window for the toast notification
        toast_window = tk.Toplevel(self)
        toast_window.attributes('-fullscreen', False)
        toast_window.grab_set()
        toast_window.overrideredirect(True)  # Remove window borders

        # Set a temporary position to allow proper size calculation
        toast_window.geometry("+0+0")

        # Create a label widget for the message
        toast_label = tk.Label(
            toast_window, text=message, bg=self.purple_palette[4], fg="white",
            font=("Arial", 12, "bold"), padx=10, pady=5
        )
        toast_label.pack()

        # Update to get actual dimensions
        toast_window.update_idletasks()  # Forces geometry recalculation
        toast_width = toast_window.winfo_width()
        toast_height = toast_window.winfo_height()

        # Get main window position & size
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        window_x = self.winfo_x()
        window_y = self.winfo_y()

        # Recalculate centered position
        x_pos = window_x + (window_width // 2) - (toast_width // 2)
        if position == "top":
            y_pos = window_y + 30  # Offset from top
        else:  # Bottom
            y_pos = window_y + window_height - toast_height - 30  # Offset from bottom

        # Apply final position
        toast_window.geometry(f"{toast_width}x{toast_height}+{x_pos}+{y_pos}")

        # Destroy the toast window after 2 seconds
        self.after(2000, toast_window.destroy)


    

    def color_palette(self):
        # Create a topmost window for the toast notification
        toast_window = tk.Toplevel(self)
        toast_window.attributes('-fullscreen', False)  
        toast_window.grab_set()

        toast_window.geometry("400x400+300+300")
        

        # Create a label widget for the message

        sk = ctk.CTkScrollableFrame(toast_window)

        for idx, i in enumerate(self.purple_palette):
            toast_label = tk.Label(sk, text=f"Color {i}, Index {idx}", bg=i, fg="white", font=("Arial", 12, "bold"), padx=10, pady=20, )
            toast_label.pack(fill='both')
        sk.pack(fill="both", expand=True)





            






class Pulser(ctk.CTkFrame):
    """
    A class representing a pulsing animation frame with audio playback capabilities.

    Attributes:
        parent (tk.Tk): The parent window.
        speed (int): The speed of the GIF animation.
        speaking (bool): The speaking state of the Pulser.
        color (str): The foreground color of the frame.
        output_file (str): The audio output file.
        y (ndarray): The audio data.
        sr (int): The sample rate of the audio.
    """
    def __init__(self, parent: tk.Tk, container, bg_corners, border_width: int = 2, border_color: str = 'black', 
                 corner_radius: int = 200, fg_color: str = 'black', width: int = 350, 
                 height: int = 350, speed: int = 50):
        """
        Initialize the Pulser class.

        Args:
            parent (tk.Tk): The parent window.
            border_width (int): The width of the border. Defaults to 2.
            border_color (str): The color of the border. Defaults to 'black'.
            corner_radius (int): The radius of the corners. Defaults to 200.
            fg_color (str): The foreground color. Defaults to 'black'.
            width (int): The width of the frame. Defaults to 350.
            height (int): The height of the frame. Defaults to 350.
            speed (int): The speed of the GIF animation. Defaults to 50.
        """
        self.parent = parent
        background_corner_colors = bg_corners or (self.parent.purple_palette[1], self.parent.purple_palette[1], self.parent.purple_palette[1], self.parent.purple_palette[1]) 
        super().__init__(container, border_width=border_width, border_color=border_color, 
                         corner_radius=corner_radius, fg_color=fg_color, width=width, 
                         height=height, background_corner_colors=background_corner_colors)
        self.speed = speed
        self.speaking = False
        self.color = fg_color
        self.output_file = os.path.join(os.getcwd(), 'Sound', 'prompt.aiff')
        self.y, self.sr = librosa.load(self.output_file, sr=None)

        self._create_gif_section()

    def _play(self) -> None:
        """
        Play the audio file and toggle the speaking state.

        Returns:
            None
        """
        self.speaking = not self.speaking
        sd.play(self.y, self.sr)
        sd.wait()
        self.speaking = not self.speaking

    def pack_frame(self) -> 'Pulser':
        """
        Pack the frame and prevent propagation.

        Returns:
            Pulser: The instance of the Pulser class.
        """
        self.pack(expand=True)
        self.pack_propagate(False)
        return self

    def speech(self, text: str) -> None:
        """
        Convert the text to speech and play it.

        Args:
            text (str): The text to be converted to speech.

        Returns:
            None
        """
        

        subprocess.run(["say", "-v", "Daniel", "-o", os.path.join(os.getcwd(), 'Sound', 'prompt.aiff'), text])

        try:
            # say(True, text)
            self.y, self.sr = librosa.load(self.output_file, sr=None)
        except Exception as e:
             print(f"Error loading audio file: {e}")

        self._toggle_speech()

    def _toggle_speech(self) -> None:
        """
        Toggle the speech playback in a separate thread.

        Returns:
            None
        """
        threading.Thread(target=self._play).start()

    def _create_gif_section(self) -> None:
        """
        Create the section for displaying the GIF.

        Returns:
            None
        """
        gif_div_ctk = tk.Label(self, text='', background='black')
        # self._play_gif(gif_div_ctk, self._get_frames(os.path.join(os.getcwd(), 'Images', 'conviva-orb.gif')))
        self._play_gif(gif_div_ctk, self._get_frames('Images/GIF2.gif'))
        gif_div_ctk.pack(expand=True)

    def _get_frames(self, img_path: str) -> list:
        """
        Get the frames from the GIF image.

        Args:
            img_path (str): The path to the GIF image.

        Returns:
            list: The frames of the GIF image.
        """
        frames = []
        try:
            with Image.open(img_path) as img:
                while True:
                    try:
                        img.seek(img.tell() + 1)
                        frames.append(img.copy())
                    except EOFError:
                        break
        except Exception as e:
            print("Error:", e)
        return frames

    def _play_gif(self, container: tk.Label, frames: list) -> None:
        """
        Play the GIF animation.

        Args:
            container (tk.Label): The label to display the GIF.
            frames (list): The frames of the GIF image.

        Returns:
            None
        """
        total_delay = 50
        for frame in frames:
            self.parent.after(total_delay, self._next_frame, frame, container, frames)
            total_delay += self.speed
        self.parent.after(total_delay, self._next_frame, frame, container, frames, True)

    def _next_frame(self, frame: Image, container: tk.Label, frames: list, restart: bool = False) -> None:
        """
        Display the next frame of the GIF animation.

        Args:
            frame (Image): The current frame to display.
            container (tk.Label): The label to display the frame.
            frames (list): The frames of the GIF image.
            restart (bool, optional): Whether to restart the animation. Defaults to False.

        Returns:
            None
        """
        if self.speaking:
            x = random.randint(200, 250)
        else:
            x = 200

        # Ensure the container exists and is still valid
        if container.winfo_exists():
            if restart:
                self.parent.after(1, self._play_gif, container, frames)
            
            # Resize and configure the image
            photo_image = ImageTk.PhotoImage(frame.resize((x, x)))
            
            try:
                container.configure(image=photo_image)
                container.image = photo_image  # Keep a reference to avoid garbage collection
            except tk.TclError as e:
                print(f"TclError when configuring image: {e}")
        else:
            pass


class Size:
    def __init__(self, width, height):
        self.width = width
        self.height = height






if __name__ == "__main__":
    GUI()



# TODO Add Logic to create, edit and delete any conversation in the conversation menu. ---DONE
# TODO Finally start working on the functionality for the speech chat page.
# TODO Work on reading files
# TODO Also, work on making it possible to scrape sites asynchronously and return the data.
# TODO Add a mechanism to handle low or bad internet connectivity.