import os
import json
import shutil
import random
import pyttsx3
import librosa
import threading
import subprocess
import tkinter as tk
import sounddevice as sd
from pathlib import Path
import customtkinter as ctk
from llm_processing import *
from datetime import datetime 
from tkinter import messagebox
from PIL import Image, ImageTk
from tkinter import PhotoImage, TclError
from tkinterdnd2 import TkinterDnD, DND_ALL
from tkinter import filedialog




class GUI(TkinterDnD.Tk):
# class GUI(tk.Tk):

# Init functions
    def __init__(self):
        # Initialize both parent classes
        super().__init__()
        ctk.set_appearance_mode('dark')
        self.title('Conviva 2.0')
        self.size = (1200, 700)
        self.settings=self.load_settings()
        self.purple_palette = [
            "#E6E6FA",  # Lavender              0
            "#E0B0FF",  # Mauve                 1
            "#C8A2C8",  # Lilac                 2
            "#9966CC",  # Amethyst              3
            "#7851A9",  # Royal Purple          4
            "#9C51B6",  # Purple Plum           5
            "#673AB7",  # Deep Purple           6
            "#614051",  # Eggplant              7
            "#2E003E",  # Midnight Purple       8
            "#9932CC",  # Dark Orchid           9
            "#4B0082",  # Indigo                10
            "#2C003E",  # Dark Grape            11
            "#1D0033",  # Dark Violet           12
            "#12002C",  # Deep Eggplant         13
            "#0D001A"   # Almost Black Purple   14
        ]

        self.file_type_colors = {
            'png': 'blue',
            'jpg': 'blue',
            'jpeg': 'blue',
            'mp3': 'green',
            'wav': 'green',
        }
        
        self.utilities = AI_Utilties(self.gui_title_function ,Conversation(self.gui_title_function))


        self.current_page_index = self.settings.get('default-screen', 0)
        self.side_panel_visible = self.settings.get('sidebar-open', False)
        self.speech_voice = self.settings.get('default-voice', 'Daniel')

        # self.preview_voice(self.speech_voice, "This is a Test")

        self.file_tag = None
        self.pages = [ self.speech_chat, self.text_chat, ]
        self.conversation = {}
        self.current_conversation = ''
        self.extra_func_args={}

        # Define Some Other shades Of Purple.

        self.geometry(f"{self.size[0]}x{self.size[1]}+{int(self.winfo_screenwidth()/2)-int(self.size[0]/2)}+{int(self.winfo_screenheight()/2)-int(self.size[1]/2)-50}")
        self.minsize(1200, 700)

        self.page_frame = tk.Frame(self)
        
        self.speech_chat_frame = tk.Frame(self.page_frame)
        self.main_speech_content = tk.Frame(self.speech_chat_frame, )
        self.speech_body = tk.Frame(self.main_speech_content, background=self.purple_palette[1])


        self.text_chat_frame = tk.Frame(self.page_frame)
        self.main_text_content = tk.Frame(self.text_chat_frame, )
        self.text_body = tk.Frame(self.main_text_content, background=self.purple_palette[8])

        self.pulser = Pulser(self, self.speech_body, (self.purple_palette[13], self.purple_palette[13], self.purple_palette[13], self.purple_palette[13]) , corner_radius=200, border_width=2, border_color=self.purple_palette[9]).pack_frame()

        
        self.load_page()

        self.toggle_side_panel()

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

        self.bind("<Command-u>", self.upload_file)
        self.bind("<Control-u>", self.upload_file)

        self.menubar()
        self.mainloop()


# Basic Utils
    def load_page(self):
        """
        Loading the current page and setting up navigation.
        """
        self.pages[self.current_page_index]()  # Running the function associated with the current page
        self.page_frame.pack(fill='both', expand=True)  # Expanding the frame to fit the window
        # self._nav_buttons()  # Displaying navigation buttons

    def topbar(self, frame):
        """
        Creating the top bar with a menu button and title label.

        Args:
            frame (tk.Frame): The parent frame where the top bar is being placed.
        """
        # Loading the menu button image
        self.menu_image = ctk.CTkImage(
            dark_image=Image.open("Images/Menu.png"), 
            light_image=Image.open("Images/Menu.png")
        )

        # Creating the header frame with a background color
        header = tk.Frame(frame, background=self.purple_palette[13])

        # Creating the menu toggle button and placing it in the header
        self.maintoggle_button = ctk.CTkButton(
            header, text='', image=self.menu_image, width=100, 
            fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], 
            command=lambda e=None: self.toggle_side_panel(e)
        )
        self.maintoggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)

        # Adding a title label to the header
        self.conversation_title = tk.Label(
            header, text='', bg=self.purple_palette[13], 
            font=('Arial Black', 16, 'bold')
        )
        self.conversation_title.place(relx=1, rely=0, relwidth=0.5, relheight=1.0, anchor='ne')

        # Placing the header at the top of the frame
        header.place(relx=0, rely=0, relwidth=1, relheight=0.1)

    def load_settings(self):
        """
        Loading settings from a JSON file, or using defaults if the file is missing.

        Returns:
            dict: The settings data.
        """
        data = {
            'default-screen': 0,
            'default-voice': 'Daniel',
            'sidebar-open': False,
        }

        try:
            with open('settings.json', 'r') as r:
                data = json.load(r)  # Reading settings from the file
        except:
            self.set_settings(data)  # Creating the file with default settings if it doesn't exist

        return data  # Returning the loaded or default settings

    def clear_page(self, frame):
        """
        Removing all widgets from the given frame.

        Args:
            frame (tk.Frame): The frame to clear.
        """
        for child in frame.winfo_children():
            child.destroy()  # Destroying each child widget inside the frame

    def set_settings(self, data):
        """
        Saving settings data to a JSON file.

        Args:
            data (dict): The settings data to save.
        """
        with open('settings.json', 'w') as w:
            json.dump(data, w, indent=4)  # Writing the settings to a file with indentation

    def gui_title_function(self):
        """
        Opening a modal to get a title input from the user.

        Returning:
            str or None: The user-provided title or None if no input is given.
        """
        title = None  # Setting up a placeholder for storing user input

        def title_callback(input_title):
            """Capturing the title from the modal and storing it."""
            nonlocal title
            title = input_title  # Storing the received title

        # Opening a modal dialog and passing the callback to handle user input
        self.conversation_modal(callback=title_callback)

        # Waiting for the modal to close before returning the title
        self.modal.wait_window()

        return title  # Returning the collected title (or None if no input)

    def toggle_fullscreen(self, event=None):
        """
        Toggling fullscreen mode on and off.
        
        Args:
            event (optional): Event parameter for binding (not used here).
        """
        self.full_screen = not self.full_screen  # Flipping the fullscreen state
        self.attributes('-fullscreen', self.full_screen)  # Applying the new state


# Menu Bar Section and its Associated functions.
    def menubar(self):
        """
        Creating the menu bar with different sections for file operations, view settings,
        configurations, and help options.
        """
        current_os = platform.system()  # Detecting the operating system
        menu_bar = tk.Menu(self)  # Creating the main menu bar

        # ---- File Menu ----
        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(
            label='Upload File (Image/Audio)',
            accelerator="Cmd+U" if current_os == 'Darwin' else "Ctrl+U",
            command=self.upload_file
        )
        file_menu.add_separator()  # Adding a separator for visual clarity
        file_menu.add_command(
            label='Clear Conversation History',
            accelerator="Cmd+Shift+X" if current_os == 'Darwin' else "Ctrl+Shift+X",
            command=self.clear_history
        )
        file_menu.add_command(
            label='Create New Conversation',
            accelerator="Cmd+N" if current_os == 'Darwin' else "Ctrl+N",
            command=self.toggle_conversation
        )
        file_menu.add_separator()  # Adding a separator for visual clarity
        file_menu.add_command(
            label='Quit',
            accelerator="Cmd+Q" if current_os == 'Darwin' else "Ctrl+Q",
            command=self.destroy
        )
        menu_bar.add_cascade(label='File', menu=file_menu)  # Adding the file menu to the menu bar

        # ---- View Menu ----
        view_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu.add_command(label='Orb Screen', command=lambda page_num=0: self.change_page(page_num))
        view_menu.add_command(label='Chat Screen', command=lambda page_num=1: self.change_page(page_num))
        view_menu.add_separator()
        view_menu.add_command(
            label='Full Screen',
            accelerator="Cmd+F" if current_os == 'Darwin' else "Ctrl+F",
            command=self.toggle_fullscreen
        )
        view_menu.add_command(
            label='Toggle Sidebar',
            accelerator="Cmd+B" if current_os == 'Darwin' else "Ctrl+B",
            command=self.toggle_side_panel
        )
        menu_bar.add_cascade(label='View', menu=view_menu)  # Adding the view menu to the menu bar

        # ---- Configuration Menu ----
        config_menu = tk.Menu(menu_bar, tearoff=False)

        # Default Screen Selection
        screen_menu = tk.Menu(config_menu, tearoff=False)
        self.default_screen = tk.IntVar(value=self.settings.get("default-screen", 0))
        screen_menu.add_radiobutton(
            label='Orb Screen',
            variable=self.default_screen,
            value=0,
            command=lambda: self.set_default_screen(0)
        )
        screen_menu.add_radiobutton(
            label='Chat Screen',
            variable=self.default_screen,
            value=1,
            command=lambda: self.set_default_screen(1)
        )
        config_menu.add_cascade(label='Select Default Screen', menu=screen_menu)
        config_menu.add_separator()

        # Voice Selection
        self.voice_submenu = tk.Menu(config_menu, tearoff=False)
        voices = self.pulser.voices()
        self.current_voice = tk.StringVar(value=self.settings.get("default-voice", ""))

        for voice in voices:
            voice_name = voice['name']
            single_voice_menu = tk.Menu(self.voice_submenu, tearoff=False)

            # Adding a preview option for each voice
            single_voice_menu.add_command(
                label="Preview",
                command=lambda v=voice_name, t=voice['description']: self.preview_voice(v, t)
            )

            # Allowing the user to set a default voice
            single_voice_menu.add_radiobutton(
                label="Set as Default",
                variable=self.current_voice,
                value=voice_name,
                command=lambda v=voice_name: self.set_default_voice(v)
            )

            self.voice_submenu.add_cascade(label=voice_name, menu=single_voice_menu)
        self.update_menu_labels(self.settings.get("default-voice", ""))

        config_menu.add_cascade(label="Select Default Voice", menu=self.voice_submenu)

        config_menu.add_separator()

        # Sidebar Visibility Option
        self.var = tk.BooleanVar(value=self.settings.get("sidebar-open", True))
        config_menu.add_checkbutton(
            label='Keep Sidebar',
            onvalue=True,
            offvalue=False,
            variable=self.var,
            command=lambda: self.set_sidebar_state(self.var.get())
        )
        menu_bar.add_cascade(label='Configuration', menu=config_menu)  # Adding the config menu

        # ---- Help Menu ----
        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(
            label='Read The Docs',
            command=lambda url='https://github.com/Programming-Sai/Conviva-v-2.0/blob/main/README.md': webbrowser.open(url)
        )
        help_menu.add_command(
            label='Raise an Issue',
            command=lambda url='https://github.com/Programming-Sai/Conviva-v-2.0/issues': webbrowser.open(url)
        )
        menu_bar.add_cascade(label='Help', menu=help_menu)  # Adding the help menu

        # Applying the menu bar to the app
        self.config(menu=menu_bar)

    def open_file_dialog(self):
        file_path = filedialog.askopenfilename(
            defaultextension="*.*",
            filetypes=[("Images", "*.png *.jpg *.jpeg"), ("Audio", "*.mp3 *.wav")]
        )
        if file_path:
            self.on_file_selected(file_path)

    def change_page(self, idx):
        """
        Switches to a new page by clearing the current page and loading the selected one.
        Also toggles the sidebar state.
        """
        self.clear_page(self.page_frame)  # Clear the existing content
        self.set_current_page_index(idx)  # Update the page index
        self.pages[self.current_page_index]()  # Load the new page
        self.page_frame.pack(fill='both', expand=True)  # Ensure the new page is displayed
        self.side_panel_visible = not self.side_panel_visible  # Toggle sidebar state
        self.toggle_side_panel()  # Apply the sidebar change
        # self._nav_buttons()  # Update navigation buttons

    def upload_file(self, e=None):
        self.after(100, self.open_file_dialog)  # Delay to prevent UI freezes

    def set_sidebar_state(self, state):
        """
        Updates and saves the sidebar visibility state.
        """
        self.settings = self.load_settings()  # Load current settings
        self.side_panel_visible = state  # Update sidebar visibility
        self.toggle_side_panel()  # Apply visibility change
        self.settings["sidebar-open"] = state  # Store in settings
        self.set_settings(self.settings)  # Save the updated settings

    def preview_voice(self, voice, text):
        """
        Plays a preview of the selected voice using the given text.
        """
        self.pulser.speech(text, voice)

    def on_file_selected(self, file_path):
        self.focus_force()
        print("Selected file:", file_path)
        data = file_path
        file_extension = Path(data).suffix.replace('.', '').upper()  # Getting the file extension in uppercase
        
       
        # Getting the color associated with the file type
        color = self.file_type_colors.get(file_extension.lower(), 'gray') 
        
        try:
            # Checking if the file tag label exists or needs to be created
            if not self.file_tag or not self.file_tag.winfo_exists():  
                self.file_tag = ctk.CTkLabel(
                    self.speech_body if self.speech_body.winfo_exists() else self.text_body, # if self.text_body.winfo_exists() else frame,  
                    font=('Arial Black', 16, 'bold'),
                    width=50,
                    height=70,
                    corner_radius=20,
                    text=file_extension,
                    fg_color=color
                )
            else:
                # Updating the label text and color if it already exists
                self.file_tag.configure(text=file_extension, fg_color=color)
            
            # Bringing the label to the top of the UI
            self.file_tag.lift()
            self.file_tag.bind("<Button-1>", lambda e: self.destroy_tag())
            
            # Positioning the file tag on the screen
            self.place_file_tag(Size(self.winfo_screenwidth(), self.winfo_screenheight()))
            
            # Sending the file to the LLM for processing
            self.send_file_to_llm(data, file_extension)
        except TclError as error:
            print(f"Error handling drop event: {error}")

    def set_default_voice(self, voice_name):
        """
        Updates and saves the default voice setting.
        """
        self.settings = self.load_settings()  # Load current settings
        self.speech_voice = voice_name  # Update the voice setting
        self.settings["default-voice"] = voice_name  # Store in settings
        self.set_settings(self.settings)  # Save the updated settings
        self.update_menu_labels(voice_name)

    def set_current_page_index(self, index):
        """
        Sets the current page index.
        """
        self.current_page_index = index

    def set_default_screen(self, screen_name):
        """
        Updates and saves the default screen setting.
        """
        self.settings = self.load_settings()  # Load current settings
        self.current_page_index = screen_name  # Update the current page index
        self.settings["default-screen"] = screen_name  # Store in settings
        self.set_settings(self.settings)  # Save the updated settings

    def update_menu_labels(self, selected_voice):
        """Update submenu labels to indicate the selected voice."""
        for i in range(self.voice_submenu.index("end") + 1):  # Iterate through menu indices
            label = self.voice_submenu.entrycget(i, "label")  # Get current label
            if label:
                voice_name = label.replace("✅ ", "")  # Remove existing checkmark if present
                new_label = f"✅ {voice_name}" if voice_name == selected_voice else voice_name
                self.voice_submenu.entryconfig(i, label=new_label)  # Update label



# Side bar Section and its Associated Functions
    def side_panel_creator(self, frame):
        """
        Creating and adding a side panel to the specified frame.
        This initializes the sidebar and sets up its content.
        """
        self.side_panel = tk.Frame(frame)  # Creating the side panel frame
        self.side_panel_content()  # Populating the side panel with UI elements
        self.side_panel.place(x=0, y=0, relheight=1.0)  # Positioning the panel

    def toggle_side_panel(self, e=None):
        """
        Toggling the visibility of the side panel.
        This adjusts the layout dynamically to either hide or show the sidebar.
        """
        if self.side_panel_visible:
            # Hiding the side panel
            self.side_panel.place_configure(relwidth=0)
            if self.main_speech_content is not None and self.main_speech_content.winfo_exists():
                self.main_speech_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            if self.main_text_content is not None and self.main_text_content.winfo_exists():
                self.main_text_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)
            self.side_panel_visible = False
            self.main_menu_button_visible = True
            self.toggle_main_menu_button()
        else:
            # Showing the side panel
            self.side_panel.place_configure(relwidth=0.3)
            if self.main_speech_content is not None and self.main_speech_content.winfo_exists():
                self.main_speech_content.place_configure(relx=0.3, relwidth=0.7, rely=0, relheight=1.0)
            if self.main_text_content is not None and self.main_text_content.winfo_exists():
                self.main_text_content.place_configure(relx=0.3, relwidth=0.7, rely=0, relheight=1.0)
            self.side_panel_visible = True
            self.main_menu_button_visible = False
            self.toggle_main_menu_button()

    def side_panel_content(self):
        """
        Populating the side panel with header buttons and a conversation list.
        This sets up the UI elements within the sidebar.
        """
        # Loading images for sidebar buttons
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

        # Creating the sidebar header
        header = tk.Frame(self.side_panel, background=self.purple_palette[13])

        # Adding buttons to the header
        toggle_button = ctk.CTkButton(header, text='', image=self.menu_image, width=100, fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], command=lambda e=None: self.toggle_side_panel(e))
        toggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0)

        new_conversation = ctk.CTkButton(header, text='', image=self.new_conversation_image, width=100, fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], command=self.toggle_conversation)
        new_conversation.place(relx=0.65, rely=0, relwidth=0.3, relheight=1.0, anchor='ne')

        clear_history = ctk.CTkButton(header, text='', image=self.clear_history_image, width=100, fg_color=self.purple_palette[13], hover_color=self.purple_palette[7], command=self.clear_history)
        clear_history.place(relx=1, rely=0, relwidth=0.3, relheight=1.0, anchor='ne')

        header.place(relx=0, rely=0, relwidth=1, relheight=0.1)

        # Creating the conversation list section
        self.conversations = ctk.CTkScrollableFrame(self.side_panel, fg_color=self.purple_palette[6])
        self.place_conversations_list()
        self.conversations.place(relx=0, rely=0.1, relwidth=1, relheight=1)

    def clear_history(self, e=None):
        """
        Clearing all stored conversations after user confirmation.
        This removes all conversation files and updates the UI accordingly.
        """
        response = messagebox.askyesno("Confirm Deletion", "Are you sure you want to clear your history?")
        if response:
            try:
                folder_path = "Conversations"
                # Deleting all conversation files
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.remove(file_path)  
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  
                # Resetting conversation history
                self.utilities.conversation.conversation_history = []
                self.conversation_title.configure(text="")
                self.place_conversations_list()
                self.get_conversation_content_for_text_chat()
                self.scroll_frame_content()
            except Exception as e:
                messagebox.showerror(f"Error: {e}")

    def place_conversations_list(self):
        """
        Updating and displaying the list of conversations in the sidebar.
        This dynamically refreshes the UI with existing conversation history.
        """
        for widget in self.conversations.winfo_children():
            widget.destroy()

        c = self.get_conversations()
        
        for i in c:
            text = i.replace(".json", "")[45:]
            if text.startswith('.'):
                continue

            # Creating a frame to hold the label and buttons
            conversation_frame = ctk.CTkFrame(self.conversations, fg_color="transparent", width=100)  
            conversation_frame.pack(fill='both', pady=5, padx=5)

            # Adding the conversation label
            conversation_label = ctk.CTkLabel(
                conversation_frame, 
                text=self.truncate_text(text.replace("-", " "), 30), 
                fg_color=self.purple_palette[7 if i == self.current_conversation_file() else 5], 
                corner_radius=10, 
                anchor="w",
            )
            conversation_label.pack(side="left", fill="both", expand=True, ipady=10, ipadx=10)

            # Adding delete button
            delete_button = ctk.CTkButton(
                conversation_frame, 
                text="✖", 
                width=30, 
                height=30, 
                fg_color="red", 
                command=self.create_callback(self.delete_conversation, i, c)
            )
            delete_button.pack(side="right", padx=5)

            # Adding edit button
            edit_button = ctk.CTkButton(
                conversation_frame, 
                text="✎", 
                width=30, 
                height=30, 
                fg_color=self.purple_palette[10], 
                command=self.create_callback(self.conversation_modal, True, i)
            )
            edit_button.pack(side="right", padx=5)

            # Binding actions to the label
            conversation_label.bind("<Button-1>", self.create_callback(self.open_conversation, i))
            
            # Creating context menu for conversation actions
            context_menu = tk.Menu(conversation_label, tearoff=0)
            context_menu.add_command(label="Open        ", command=self.create_callback(self.open_conversation, i))
            context_menu.add_command(label="Edit        ", command=self.create_callback(self.conversation_modal, True, i))
            context_menu.add_separator()
            context_menu.add_command(label="Delete      ", foreground='red', command=self.create_callback(self.delete_conversation, i, c))

            # Binding right-click menu to the label
            conversation_label.bind("<Double-1>", self.create_context_menu_callback(context_menu))
            conversation_label.bind("<Button-3>", self.create_context_menu_callback(context_menu))

        # Adding a spacer at the bottom
        tk.Frame(self.conversations, height=100, background=self.purple_palette[6]).pack(fill='both')

    def truncate_text(self, text, length=20):
        """
        Truncating text to the specified length and appending '...' if it exceeds the limit.
        This ensures UI elements remain properly formatted.
        """
        return text[:length] + "..." if len(text) > length else text

    def create_callback(self, func, *args):
        """
        Creating a callback function with pre-defined arguments.
        This allows binding events without passing extra parameters manually.
        """
        def callback(*_):
            func(*args)
        return callback

    def create_context_menu_callback(self, menu):
        """
        Creates a callback function for displaying a context menu.

        Args:
            menu (tk.Menu): The menu to be shown.

        Returns:
            function: A callback function to display the context menu.
        """
        def callback(event):
            self.show_context_menu(event, menu)
        return callback

    def toggle_main_menu_button(self):
        """
        Toggles the visibility of the main menu button.
        If visible, places it in the UI. Otherwise, hides it.
        """
        if self.main_menu_button_visible:
            self.maintoggle_button.place(relx=0, rely=0, relwidth=0.3, relheight=1.0) 
        else:
            self.maintoggle_button.place_forget()

    def toggle_conversation(self, e=None):
        """
        Starts a new conversation and refreshes the conversation list.

        Args:
            e (event, optional): Event parameter (used in bindings). Defaults to None.
        """
        self.utilities.conversation.move_file = True
        self.utilities.conversation.create_new_conversation()
        print("New Conversation Should Start here!!!")
        self.utilities.conversation.move_file = False
        self.place_conversations_list()
        self.scroll_frame_content()

    def show_context_menu(self, event, menu):
        """
        Displays a context menu at the mouse cursor's position.

        Args:
            event (tk.Event): The event object containing mouse position.
            menu (tk.Menu): The context menu to display.
        """
        menu.post(event.x_root, event.y_root)

    def delete_conversation(self, conversation_to_delete, conversations):
        """
        Deletes a selected conversation file after user confirmation.
        Updates the current conversation file reference if needed.

        Args:
            conversation_to_delete (str): The file path of the conversation to delete.
            conversations (list): List of all conversation file paths.
        """
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

    def get_conversations(self):
        """
        Retrieves and sorts conversation files based on extracted timestamps.

        Returns:
            list: A list of conversation file paths sorted by timestamp in descending order.
        """
        # Walking through the "Conversations" directory to get all files
        walk_gen = os.walk("Conversations")
        walk_list = list(walk_gen)
        root = walk_list[0][0]

        # Collecting file paths in the directory
        files = [os.path.join(root, i) for i in walk_list[0][2]] or []

        # Sorting files based on extracted timestamps (newest first)
        sorted_files = sorted(files, key=lambda x: self.extract_timestamp(x), reverse=True)
        return sorted_files

    def extract_timestamp(self, file_name):
        """
        Extracts the timestamp from a conversation file name.

        Args:
            file_name (str): The file path of the conversation.

        Returns:
            str: Extracted timestamp in the format 'YYYY_MM_DD'.
        """
        copy = file_name.replace("Conversations/", "")

        # Returning empty string if it's a hidden file
        if copy.startswith("."):
            return ""
        
        # Extracting and returning the timestamp
        return copy.split('_')[1] + "_" + copy.split('_')[2] + "_" + copy.split('_')[3]

    def current_conversation_file(self):
        """
        Retrieves the file path of the currently active conversation.

        Returns:
            str: The path of the current conversation file.
        """
        # Reading the current conversation file reference from storage
        with open("Conversations/.current_conversation_file_name.txt", 'r') as f:
                data = f.read()
        return data

    def open_conversation(self, conversation_to_open, e=None ):
        """
        Opens a selected conversation file, loads its content, and updates the UI.

        Args:
            conversation_to_open (str): The file path of the conversation to open.
            e (event, optional): Event parameter (used in bindings). Defaults to None.
        """
        try:
            # Updating the current conversation file reference
            with open("Conversations/.current_conversation_file_name.txt", 'w') as f:
                f.write(conversation_to_open)

            # Loading the conversation history from the file
            with open(conversation_to_open, 'r') as file:
                self.utilities.conversation.conversation_history = json.load(file)
                self.conversation = self.utilities.conversation.conversation_history

            # Extracting and formatting the conversation title for display
            self.current_conversation = conversation_to_open[45:].replace('.json', "")
            self.conversation_title.configure(text=self.current_conversation.replace("-", " "))

            # Refreshing the conversation list and updating the chat window
            self.place_conversations_list()
            self.get_conversation_content_for_text_chat()
            self.auto_scroll_to_end()
        except:
            # Resetting conversation data in case of an error
            self.conversation = {}




# Speech (Orb) Chat Page

    def speech_chat(self):
        # """
        # Initializes and displays the speech chat interface.
        # """
        # try:
            # Creating the main frame for speech chat
            self.speech_chat_frame = tk.Frame(self.page_frame)

            # Adding side panel to the speech chat frame
            self.side_panel_creator(self.speech_chat_frame)

            # Creating the main content frame for speech chat
            self.main_speech_content = tk.Frame(self.speech_chat_frame)

            # Setting up the speech chat content
            self.main_speech_content_content()

            # Placing the main speech content to occupy the entire frame
            self.main_speech_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)

            # Packing the speech chat frame to make it visible
            self.speech_chat_frame.pack(fill='both', expand=True)
        # except:
            # Handling cases where speech chat does not exist
            # print("Not In Existence (Speech Chat)")

    def main_speech_content_content(self):
        """
        Sets up the UI components for the speech chat content.
        """
        # Loading the top bar/header
        self.topbar(self.main_speech_content)

        # Creating the body section for speech chat
        self.speech_body = tk.Frame(self.main_speech_content, background=self.purple_palette[13])

        # Initializing the pulser component with specific colors and styles
        self.pulser = Pulser(
            self,
            self.speech_body,
            (self.purple_palette[13], self.purple_palette[13], self.purple_palette[13], self.purple_palette[13]),
            corner_radius=200,
            border_width=2,
            border_color=self.purple_palette[9]
        ).pack_frame()

        # Enabling drag-and-drop functionality for the pulser
        self.pulser.drop_target_register(DND_ALL)
        self.pulser.dnd_bind('<<Drop>>', self.handleDropEvent)

        # Initializing the chat input bar without displaying it yet
        self.chatbar(self.speech_body)

        FloatingButtonList(self, orientation='vertical', functions=self.pages)



        # Placing the speech chat body in the frame
        self.speech_body.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)
        




# Text (Chat) Chat Page
    def text_chat(self):
        """
        Initializes and displays the text chat interface.
        """
        try:
            # Creating the main frame for text chat
            self.text_chat_frame = tk.Frame(self.page_frame)

            # Adding the side panel to the text chat frame
            self.side_panel_creator(self.text_chat_frame)

            # Creating the main content frame for text chat
            self.main_text_content = tk.Frame(self.text_chat_frame)

            # Setting up the text chat content
            self.main_text_content_content()

            # Placing the main text content to occupy the entire frame
            self.main_text_content.place_configure(relwidth=1.0, relx=0, rely=0, relheight=1.0)

            # Packing the text chat frame to make it visible
            self.text_chat_frame.pack(fill='both', expand=True)
        except:
            # Handling cases where text chat does not exist
            print("Not In Existence (Text Chat)")

    def scroll_frame_content(self):
        """
        Loads the current conversation file and updates the scrollable frame.
        """
        try:
            # Reading the current conversation file name
            with open("Conversations/.current_conversation_file_name.txt", 'r') as f:
                current_file = f.read()

            # Opening the selected conversation
            self.open_conversation(conversation_to_open=current_file)
        except:
            # Handling cases where the file does not exist
            pass

    def scroll_to_top(self, event=None):
        """
        Scrolls the conversation to the top.
        """
        # Moving the scrollbar to the top
        self.scroll_frame._parent_canvas.yview_moveto(0.0)

        self.scroll_frame._parent_canvas.yview_moveto(0.0)

    def main_text_content_content(self):
        """
        Sets up the UI components for the text chat content.
        """
        # Loading the top bar/header
        self.topbar(self.main_text_content)

        # Creating the body section for text chat
        self.text_body = tk.Frame(self.main_text_content, background=self.purple_palette[13])

        # Initializing a scrollable frame for text messages
        self.scroll_frame = ctk.CTkScrollableFrame(self.text_body, corner_radius=0, fg_color=self.purple_palette[13])

        # Enabling drag-and-drop functionality for the scroll frame
        self.scroll_frame.drop_target_register(DND_ALL)
        self.scroll_frame.dnd_bind('<<Drop>>', self.handleDropEvent)

        # Adding an empty spacer frame at the top of the scrollable frame
        tk.Frame(self.scroll_frame, height=50, bg=self.purple_palette[13]).pack(side='top')

        # Loading conversation content into the scroll frame
        self.scroll_frame_content()

        # Packing the scroll frame to make it visible
        self.scroll_frame.pack(fill='both', expand=True)

        # Binding scroll shortcuts for Mac and Windows/Linux
        self.bind("<Command-Up>", self.scroll_to_top)
        self.bind("<Command-Down>", self.auto_scroll_to_end)
        self.bind("<Control-Up>", self.scroll_to_top)
        self.bind("<Control-Down>", self.auto_scroll_to_end)

        # Adding the chat input bar
        self.chatbar(self.text_body)

        # Creating a button frame for scrolling control
        self.button_frame = ctk.CTkFrame(self.text_body, corner_radius=50, width=60, height=60, fg_color=self.purple_palette[9])

        # Placing the button frame at a fixed position
        self.button_frame.place(relx=.85, rely=.8)
        self.button_frame.pack_propagate(False)

        # Binding click event to toggle scrolling behavior
        self.button_frame.bind("<Button-1>", self.scroll_button_method)

        # Creating a scroll button to toggle between top and bottom
        self.scroll_button = ctk.CTkButton(
            self.button_frame, text="▲", font=("Segoe UI Symbol", 24),
            width=0, height=60, fg_color=self.purple_palette[9],
            hover_color=self.purple_palette[9], command=self.scroll_button_method
        )
        self.scroll_button.pack()

        FloatingButtonList(self, orientation='vertical', functions=self.pages)

        # Placing the text body in the frame
        self.text_body.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

    def auto_scroll_to_end(self, e=None):
        """
        Scrolls the conversation to the latest message at the bottom.
        """
        # Setting the scrollbar position to the bottom
        self.scroll_frame._scrollbar.set(*self.scroll_frame._parent_canvas.yview())

        # Configuring the canvas to update the scrollbar settings
        self.scroll_frame._parent_canvas.configure(
            yscrollcommand=self.scroll_frame._scrollbar.set,
            scrollregion=self.scroll_frame._parent_canvas.bbox('all')
        )

        # Moving the scrollbar to the bottom
        self.scroll_frame._parent_canvas.yview_moveto(1.0)

    def scroll_button_method(self, e=None):
        """
        Toggles between scrolling to the top and scrolling to the bottom.
        """
        # Checking the current direction of the button
        direction = self.scroll_button.cget('text')

        if direction == '▲':
            # Scrolling to the top and updating the button text
            self.scroll_to_top()
            self.scroll_button.configure(text='▼')
        else:
            # Scrolling to the bottom and updating the button text
            self.auto_scroll_to_end()
            self.scroll_button.configure(text='▲')


# Input Field for prompting and its associated functions
    def chatbar(self, frame):
        """
        Creates and configures the chat input bar with an entry widget and a textbox widget.
        Handles drag-and-drop events and binds keyboard shortcuts based on the context (speech or text).

        Args:
            frame (tk.Frame): The parent frame where the chat input bar is placed.

        Returns:
            None
        """
        self.prompt = tk.StringVar()

        # Creating an entry widget for user input and a textbox widget for additional input
        self.entry_widget = ctk.CTkEntry(frame, width=500, height=50, corner_radius=50, textvariable=self.prompt)
        self.textbox_widget = ctk.CTkTextbox(frame, width=500, height=100, corner_radius=10)

        # Setting focus on both widgets to prepare for user input
        self.entry_widget.focus_set()
        self.textbox_widget.focus_set()

        # Registering the widgets to accept drag-and-drop events
        self.entry_widget.drop_target_register(DND_ALL)
        self.textbox_widget.drop_target_register(DND_ALL)

        # Binding drag-and-drop event handlers to process dropped content
        self.entry_widget.dnd_bind('<<Drop>>', lambda e: self.handleDropEvent(e))
        self.textbox_widget.dnd_bind('<<Drop>>', lambda e: self.handleDropEvent(e))

        # Placing the entry widget with spacing
        self.entry_widget.pack(pady=20)

        # Checking if the current frame is the speech input section and binding relevant events
        if frame == self.speech_body:
            self.entry_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<Command-Return>", self.get_prompt_from_text_box)
            self.textbox_widget.bind("<Control-Return>", self.get_prompt_from_text_box)
            self.entry_widget.bind("<Return>", self.get_prompt_from_text_box)
        
        # Checking if the current frame is the text input section and binding relevant events
        if frame == self.text_body:
            self.entry_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<KeyRelease>", self.toggle_prompt_box)
            self.textbox_widget.bind("<Command-Return>", self.get_prompt_from_text_box_text)
            self.textbox_widget.bind("<Control-Return>", self.get_prompt_from_text_box_text)
            self.entry_widget.bind("<Return>", self.get_prompt_from_text_box_text)
    
    def place_file_tag(self, e):
        """
        Positions the file tag within the window dynamically based on window resizing.
        Adjusts placement depending on whether the window is maximized or resized.

        Args:
            e (tk.Event): The event object containing window size information.

        Returns:
            None
        """
        if self.file_tag and self.file_tag.winfo_exists():
            width = e.width
            height = e.height
            window_width = self.winfo_width()
            window_height = self.winfo_height()
            
            # Checking the window size and repositioning the file tag accordingly
            if window_width == width or window_height == height:
                self.file_tag.place(relx=0.15, rely=0.8)
            else:
                self.file_tag.place(relx=0.1, rely=0.8)

    def handleDropEvent(self, e):
        """
        Handles the event when a file is dropped onto the application.
        
        Args:
            e (tkinter.Event): The event object containing information about the drop event.
        
        Returns:
            None
        """
        frame = e.widget  # Getting the widget where the file was dropped
        data = e.data.strip("{}")  # Extracting the file path
        file_extension = Path(data).suffix.replace('.', '').upper()  # Getting the file extension in uppercase
        
        # Checking if the file extension is supported
        if file_extension.lower() not in list(self.file_type_colors.keys()):
            print(file_extension.lower(), list(self.file_type_colors.keys()))
            messagebox.showinfo("Alert", "The Only Supported Types are Images or Audio.")
            return 
        
        # Getting the color associated with the file type
        color = self.file_type_colors.get(file_extension.lower(), 'gray') 
        
        try:
            # Checking if the file tag label exists or needs to be created
            if not self.file_tag or not self.file_tag.winfo_exists():  
                self.file_tag = ctk.CTkLabel(
                    self.speech_body if self.speech_body.winfo_exists() else self.text_body if self.text_body.winfo_exists() else frame,  
                    font=('Arial Black', 16, 'bold'),
                    width=50,
                    height=70,
                    corner_radius=20,
                    text=file_extension,
                    fg_color=color
                )
            else:
                # Updating the label text and color if it already exists
                self.file_tag.configure(text=file_extension, fg_color=color)
            
            # Bringing the label to the top of the UI
            self.file_tag.lift()
            self.file_tag.bind("<Button-1>", lambda e: self.destroy_tag())
            
            # Positioning the file tag on the screen
            self.place_file_tag(Size(self.winfo_screenwidth(), self.winfo_screenheight()))
            
            # Sending the file to the LLM for processing
            self.send_file_to_llm(data, file_extension)
        except TclError as error:
            print(f"Error handling drop event: {error}")

    def destroy_tag(self, e=None):
        """
        Destroys the file tag when it is clicked.
        
        Args:
            e (tkinter.Event, optional): The event object (defaults to None).
        
        Returns:
            None
        """
        print("Destroying Tag")
        self.file_tag.place_forget()  # Hiding the tag from the UI
        self.file_tag.destroy()  # Removing the tag widget
        self.extra_func_args = {}  # Resetting extra function arguments

    def wrap_length(self, rel_width):
        """
        Calculates the wrap length for text elements based on a relative width of the window.
        
        Args:
            rel_width (float): A value representing the width as a fraction of the window width.
        
        Returns:
            int: The calculated wrap length in pixels.
        """
        return rel_width * self.winfo_width()

    def on_resize(self, event):
        """
        Handles window resize events by repositioning the file tag.
        
        Args:
            event (tkinter.Event): The event object containing resize details.
        
        Returns:
            None
        """
        e = Size(self.winfo_screenwidth(), self.winfo_screenheight())
        self.place_file_tag(e)

    def toggle_prompt_box(self, e):
        """
        Toggles between an entry widget and a textbox widget based on text length.
        
        Args:
            e (tkinter.Event): The event object triggering the toggle.
        
        Returns:
            None
        """
        current_text = self.prompt.get()
        current_textbox_content = self.textbox_widget.get("1.0", tk.END).strip()

        # Switching to the textbox if text length exceeds the threshold
        if len(current_text) >= 75 and self.entry_widget.winfo_ismapped():
            self.entry_widget.pack_forget()
            self.textbox_widget.delete("1.0", tk.END)  
            self.textbox_widget.insert("1.0", current_text)  # Moving text to the textbox
            self.textbox_widget.focus_set()
            self.textbox_widget.pack(pady=20)

        # Switching back to the entry widget if text length decreases
        elif len(current_textbox_content) < 75 and self.textbox_widget.winfo_ismapped():
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.prompt.set(current_textbox_content)  
            self.entry_widget.pack(pady=20)

    def get_prompt_from_text_box(self, e):
        """
        Retrieves user input from the appropriate text widget (entry or textbox), clears the widget, and processes the input.
        
        Args:
            e: Event trigger (not used but required for event binding).
        """
        if self.entry_widget.winfo_ismapped(): 
            # Getting input from the entry widget
            self.user_prompt = self.prompt.get()
            self.prompt.set("")
        else:
            # Getting input from the textbox widget
            self.user_prompt = self.textbox_widget.get("1.0", tk.END).strip()
            self.textbox_widget.delete("1.0", tk.END)
            self.prompt.set("")
            # Hiding the textbox and switching focus to the entry widget
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.entry_widget.pack(pady=20)
        
        # Executing the function with or without extra arguments
        if self.extra_func_args:
            self.extra_func_args['extra_prompt'] = self.user_prompt
            print(self.extra_func_args)
            self.pulser.speech(ai_function_execution(
                self.user_prompt, tools, available_functions, self.utilities,
                extra_func=self.extra_func_args['func'], 
                **{k: self.extra_func_args[k] for k in ['extra_prompt', 'path', 'extra_utilities_class']}
            ), self.speech_voice)
        else:
            self.pulser.speech(ai_function_execution(self.user_prompt, tools, available_functions, self.utilities), self.speech_voice)
        
    def get_prompt_from_text_box_text(self, e):
        """
        Retrieves user input from the appropriate text widget, displays it in the UI, and generates a response.
        
        Args:
            e: Event trigger (not used but required for event binding).
        """
        if not self.conversation or not self.utilities.conversation.conversation_history:
            self.toggle_conversation()
        
        if self.entry_widget.winfo_ismapped(): 
            # Getting input from the entry widget
            self.user_prompt = self.prompt.get()
            self.prompt.set("")
        else:
            # Getting input from the textbox widget
            self.user_prompt = self.textbox_widget.get("1.0", tk.END).strip()
            self.textbox_widget.delete("1.0", tk.END)
            self.prompt.set("")
            # Hiding the textbox and switching focus to the entry widget
            self.textbox_widget.pack_forget()
            self.entry_widget.focus_set()
            self.entry_widget.pack(pady=20)

        # Creating a textbox to display user input
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
        
        # Creating a textbox to display AI-generated response
        self.response_label = ctk.CTkTextbox(
            self.scroll_frame,
            wrap="word",
            fg_color=self.purple_palette[6],
            corner_radius=10,
            font=("Arial", 14),
            width=int(self.wrap_length(0.5)),
            height=5,
        )
        self.response_label.configure(state="normal")
        
        # Executing the function with or without extra arguments
        if self.extra_func_args:
            self.extra_func_args['extra_prompt'] = self.user_prompt
            print(self.extra_func_args)
            self.response_label.insert("1.0", ai_function_execution(
                self.user_prompt, tools, available_functions, self.utilities,
                extra_func=self.extra_func_args['func'], 
                **{k: self.extra_func_args[k] for k in ['extra_prompt', 'path', 'extra_utilities_class']}
            ))
        else:
            self.response_label.insert("1.0", ai_function_execution(self.user_prompt, tools, available_functions, self.utilities))
        
        self.response_label.configure(state="disabled") 
        self.adjust_textbox_height(self.response_label)
        self.response_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='w') 
        self.auto_scroll_to_end()

    def adjust_textbox_height(self, textbox):
        """
        Adjusts the height of a textbox dynamically based on its content.
        
        Args:
            textbox: The textbox widget whose height needs to be adjusted.
        """
        text_content = textbox.get("1.0", "end").strip()

        if not text_content:
            textbox.configure(height=1)
            return

        # Getting the pixel width of the textbox
        textbox_width = textbox.winfo_width()

        if textbox_width == 1:  # Avoiding incorrect width value before rendering
            textbox.after(10, lambda: self.adjust_textbox_height(textbox))
            return

        # Estimating character width in pixels (depends on font size and style)
        char_width = 7  # Adjust this value based on the actual font width
        max_chars_per_line = textbox_width // char_width

        # Calculating the number of lines required
        lines = sum(max(1, -(-len(paragraph) // max_chars_per_line)) for paragraph in text_content.split("\n"))

        # Setting new height based on the estimated number of lines
        line_height = 18  # Approximate height of each line
        new_height = ((lines * line_height)) 
        new_height -= (0.1 * new_height)  # Adding a margin for a better fit
        textbox.configure(height=new_height)
        self.auto_scroll_to_end()

    def send_file_to_llm(self, path, extension):
        """
        Sends the dropped file to an LLM for analysis based on its type.
        
        Args:
            path (str): The file path of the dropped file.
            extension (str): The file extension in lowercase.
        
        Returns:
            dict: The arguments prepared for LLM processing.
        """
        extension = extension.lower()
        
        # Setting up the function arguments based on file type
        self.extra_func_args = {
            'extra_prompt': '',
            'path': path,
            'extra_utilities_class': self.utilities,
            'func': None,
            'type': ''
        }
        
        # Assigning the appropriate function for image or audio processing
        if extension in {'png', 'jpeg', 'jpg'}:
            self.extra_func_args['type'] = 'image'
            self.extra_func_args['func'] = ai_image_analysis
        elif extension in {'mp3', 'wav'}: 
            self.extra_func_args['func'] = ai_sound_analysis
            self.extra_func_args['type'] = 'sound'
        
        print("Sending File:", path, "to llm...", "\n", self.extra_func_args)
        
        return self.extra_func_args

    def get_conversation_content_for_text_chat(self):
        """
        Retrieves and displays the conversation history for the text-based chat.
        Clears previous messages before dynamically generating UI components for each message.

        Args:
            None

        Returns:
            None
        """
        # Removing all existing children widgets from the scroll frame
        for item in self.scroll_frame.winfo_children():
            item.destroy()

        # Getting the conversation history
        self.conversation = self.utilities.conversation.conversation_history

        # Adding spacing at the top of the chat display
        tk.Frame(self.scroll_frame, height=50).pack(side='top')
        
        # Iterating through conversation history and displaying messages
        for i in range(len(self.conversation)):
            if self.conversation[i]['role'] in ['system', 'tool']:
                continue
            
            elif self.conversation[i]['role'] == 'user':
                # Creating and configuring a textbox for user messages
                self.input_label = ctk.CTkTextbox(
                    self.scroll_frame,
                    wrap="word",
                    fg_color=self.purple_palette[4],
                    corner_radius=10,
                    font=("Arial", 14),
                    width=int(self.wrap_length(0.5)),
                    height=5,
                )
                # Inserting and disabling text for display
                self.input_label.configure(state="normal")
                self.input_label.insert("1.0", self.conversation[i]['content'])
                self.input_label.configure(state="disabled") 
                self.adjust_textbox_height(self.input_label)
                self.input_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='e')
            
            else:
                # Creating and configuring a textbox for assistant responses
                self.response_label = ctk.CTkTextbox(
                    self.scroll_frame,
                    wrap="word",
                    fg_color=self.purple_palette[6],
                    corner_radius=10,
                    font=("Arial", 14),
                    width=int(self.wrap_length(0.5)),
                    height=5,
                )
                # Inserting and disabling text for display
                self.response_label.configure(state="normal")
                self.response_label.insert("1.0", self.conversation[i]['content'])
                self.response_label.configure(state="disabled") 
                self.adjust_textbox_height(self.response_label)
                self.response_label.pack(ipadx=5, ipady=20, padx=40, pady=10, anchor='w')

        # Scrolling to the end of the conversation to show the latest message
        self.auto_scroll_to_end()
        
        # Adding spacing at the bottom of the chat display
        tk.Frame(self.scroll_frame, height=50).pack(side='bottom')


    def _nav_buttons(self):
        """
        Creates and places navigation buttons for page selection.

        This function generates two navigation buttons labeled "Page 1" and "Page 2" 
        and places them in the `page_frame`. When clicked, each button calls 
        `self.change_page(idx)` with the corresponding page index.

        Args:
            None

        Returns:
            None
        """
        for idx in range(2):
            nav_button = ctk.CTkButton(
                self.page_frame, 
                text='Page ' + str(idx + 1), 
                command=lambda idx=idx: self.change_page(idx),  # Passing idx to lambda to avoid late binding issues
                fg_color=self.purple_palette[-1],  # Setting button color
                hover_color=self.purple_palette[4]  # Setting hover effect color
            )
            nav_button.pack(side='left', expand=True)  # Placing buttons horizontally

    
# Color Palette for Devlopment
    def _color_palette(self):
        """
        Displays a window showcasing the color palette for development.

        This function creates a temporary `Toplevel` window displaying a scrollable 
        list of the colors defined in `self.purple_palette`. Each color is shown 
        as a labeled background, providing a quick preview of the available shades.

        Args:
            None

        Returns:
            None
        """
        # Creating a top-level window to display the color palette
        toast_window = tk.Toplevel(self)
        toast_window.attributes('-fullscreen', False)  # Ensuring it's not fullscreen
        toast_window.grab_set()  # Making it modal (prevents interaction with the main window)
        toast_window.geometry("400x400+300+300")  # Setting window size and position

        # Creating a scrollable frame inside the window
        sk = ctk.CTkScrollableFrame(toast_window)

        # Iterating over the defined color palette to display each color
        for idx, i in enumerate(self.purple_palette):
            toast_label = tk.Label(
                sk, 
                text=f"Color {i}, Index {idx}",  # Displaying color value and index
                bg=i,  # Setting the background color
                fg="white", 
                font=("Arial", 12, "bold"), 
                padx=10, 
                pady=20
            )
            toast_label.pack(fill='both')  # Ensuring the label expands

        sk.pack(fill="both", expand=True)  # Expanding the scrollable frame


# Input modals for various input types, or taos notifications.
    def textbox_placeholder(self, placeholder_text: str) -> None:
        """
        Sets a placeholder text inside the text box and ensures it disappears on focus.

        Args:
            placeholder_text (str): The placeholder text to display.
        """
        self.conversation_modal_text_box.insert("1.0", placeholder_text)
        
        def clear_placeholder(event):
            if self.conversation_modal_text_box.get("1.0", "end-1c") == placeholder_text:
                self.conversation_modal_text_box.delete("1.0", "end")
        
        self.conversation_modal_text_box.bind("<FocusIn>", clear_placeholder)
        
        def set_placeholder(event):
            if self.conversation_modal_text_box.get("1.0", "end-1c") == "":
                self.conversation_modal_text_box.insert("1.0", placeholder_text)
        
        self.conversation_modal_text_box.bind("<FocusOut>", set_placeholder)

    def toast(self, message: str, position: str = "top") -> None:
        """
        Displays a temporary toast notification with a message.

        Args:
            message (str): The message to display in the toast notification.
            position (str, optional): The vertical position of the toast ('top' or 'bottom'). Defaults to 'top'.
        """
        # Creating a top-level window for the toast notification
        toast_window = tk.Toplevel(self)
        toast_window.attributes('-fullscreen', False)
        toast_window.grab_set()
        toast_window.overrideredirect(True)  # Removing window borders
        
        # Setting a temporary position to allow proper size calculation
        toast_window.geometry("+0+0")
        
        # Creating a label widget for the message
        toast_label = tk.Label(
            toast_window, text=message, bg=self.purple_palette[4], fg="white",
            font=("Arial", 12, "bold"), padx=10, pady=5
        )
        toast_label.pack()
        
        # Updating the window to get actual dimensions
        toast_window.update_idletasks()
        toast_width = toast_window.winfo_width()
        toast_height = toast_window.winfo_height()
        
        # Getting main window position and size
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        window_x = self.winfo_x()
        window_y = self.winfo_y()
        
        # Calculating centered position for the toast
        x_pos = window_x + (window_width // 2) - (toast_width // 2)
        if position == "top":
            y_pos = window_y + 30  # Offset from top
        else:
            y_pos = window_y + window_height - toast_height - 30  # Offset from bottom
        
        # Applying final position
        toast_window.geometry(f"{toast_width}x{toast_height}+{x_pos}+{y_pos}")
        
        # Destroying the toast window after 2 seconds
        self.after(2000, toast_window.destroy)

    def get_title_from_modal(self, edit: bool, callback, current_conversation_title_path: str = "") -> None:
        """
        Retrieves the entered conversation title and applies necessary updates.
        
        Args:
            edit (bool): Indicates whether the title is being edited.
            callback (function): Function to handle the new title.
            current_conversation_title_path (str, optional): The file path of the current conversation title. Defaults to "".
        """
        title = self.conversation_modal_text_box.get(0.0, "end").strip()
        if title and edit:
            self.edit_title(title, current_conversation_title_path)
        if title and callback:
            callback(title.replace(" ", "-"))
        self.modal.destroy()
    
    def conversation_modal(self, edit: bool = False, current_conversation_title_path: str = "", callback = None) -> None:
        """
        Creates and displays a modal window for entering or editing a conversation title.

        Args:
            edit (bool, optional): Indicates whether the modal is for editing an existing title. Defaults to False.
            current_conversation_title_path (str, optional): The file path of the current conversation title. Defaults to "".
            callback (function, optional): A function to call with the new title. Defaults to None.
        """
        self.modal = tk.Toplevel(self)
        self.modal.withdraw()  # Hiding window while setting properties
        self.modal.attributes('-fullscreen', False)
        self.modal.overrideredirect(False)
        self.modal.grab_set()  # Making the modal the active window
        
        # Setting size and centering the modal
        width, height = 500, 200
        x_pos = (self.modal.winfo_screenwidth() // 2) - (width // 2)
        y_pos = (self.modal.winfo_screenheight() // 2) - (height // 2) - 50
        self.modal.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
        
        self.modal.deiconify()
        self.modal.configure(bg=self.purple_palette[4])
        
        # Creating layout frames
        topFrame = tk.Frame(self.modal, background=self.purple_palette[9])
        middleFrame = tk.Frame(self.modal)
        bottomFrame = tk.Frame(self.modal, background=self.purple_palette[10])
        
        topFrame.place(relx=0, rely=0, relwidth=1, relheight=0.2)
        middleFrame.place(relx=0, rely=0.2, relwidth=1, relheight=0.7)
        bottomFrame.place(relx=0, rely=0.7, relwidth=1, relheight=0.3)
        
        # Determining conversation title
        current_conversation_title = current_conversation_title_path.replace('.json', "")[45:] if not edit else "New Conversation Title"
        
        # Creating title and date labels
        self.conversation_modal_title = ctk.CTkLabel(topFrame, text=current_conversation_title, fg_color=self.purple_palette[9], font=("Arial Black", 12, 'bold'), anchor='w')
        self.conversation_modal_title.pack(fill='both', expand=True, padx=10, side='left')
        
        self.conversation_modal_date = ctk.CTkLabel(topFrame, text=datetime.now().strftime("%b %d, %Y"), fg_color=self.purple_palette[9], font=("Arial Black", 12, 'bold'), anchor='e')
        self.conversation_modal_date.pack(fill='both', expand=True, padx=10, side='right')
        
        # Creating text box
        self.conversation_modal_text_box = ctk.CTkTextbox(middleFrame, fg_color=self.purple_palette[9], border_color=self.purple_palette[9])
        self.textbox_placeholder("Enter Conversation Title Here...")
        self.conversation_modal_text_box.pack(fill='both', expand=True)
        
        # Creating submit button
        self.conversation_modal_submit_button = ctk.CTkButton(bottomFrame, text="Submit", fg_color=self.purple_palette[13], hover_color=self.purple_palette[12], corner_radius=20, font=("Arial Black", 12, 'bold'), anchor='center', command=lambda: self.get_title_from_modal(edit, callback, current_conversation_title_path))
        self.conversation_modal_submit_button.pack(fill='both', pady=10, padx=10, side='right')










class FloatingButtonList(ctk.CTkButton):
    """
    A class representing a floating button list.

    Attributes:
        parent (tk.Tk): The parent window.
        orientation (str): The orientation of the button list ('vertical' or 'horizontal').
        functions (list): The list of functions to be called when buttons are clicked.
        i (int): The index of the current button.
        i_id (int): The ID of the current button.
        photos (list): The list of button images.
        labels (list): The list of button labels.
        label_toggle (bool): The toggle state of the labels.
        image_names (list): The list of image names for the buttons.
    """

    def __init__(self, parent: tk.Tk, orientation: str = 'vertical', functions: list = []) -> None:
        """
        Initializes the FloatingButtonList instance.

        Args:
            parent (tk.Tk): The parent window.
            orientation (str, optional): The orientation of the button list ('vertical' or 'horizontal'). Defaults to 'vertical'.
            functions (list, optional): The list of functions to be called when buttons are clicked. Defaults to [].
        """
        super().__init__(parent, text='\u2630'.strip(), font=('Arial Black', 45), fg_color=parent.purple_palette[7], hover_color=parent.purple_palette[7], corner_radius=10, width=50, height=50)
        self.i = 0
        self.i_id = 0
        self.photos = []
        self.labels = []
        self.parent = parent
        self.label_toggle = False
        self.functions = functions
        self.orientation = orientation
        # self.bind("<Button-1>", self.open_other_buttons)
        self.configure(command=self.open_other_buttons)
        
        self.image_names = ["ai", "chat"]
        self.place_button()

    def place_buttons(self) -> None:
        """
        Places the floating buttons on the screen.
        """
        if self.i < len(self.image_names): 
            self.label_button = ctk.CTkButton(
                self.parent, 
                image=self.get_button_image(self.image_names[self.i]), 
                corner_radius=10, 
                text='', 
                fg_color=self.parent.purple_palette[7],
                hover_color=self.parent.purple_palette[7],
                command=lambda id=self.i: self.open_next_page(id),
                width=60,
                height=60,
            )
            # self.label_button.bind("<Button-1>", lambda event, id=self.i: self.open_next_page(event, id))
            if self.orientation == 'horizontal':
                self.label_button.place(relx=(1 - (310 - self.i * 100) / self.parent.winfo_width()), y=70, anchor='ne')
            else:
                self.label_button.place(relx=0.95, y=(150 + self.i * 100), anchor='ne')
            self.labels.append(self.label_button)
            self.i += 1
            self.i_id = self.parent.after(25, self.place_buttons)                
        else:
            self.after_cancel(self.i_id)

    def clear_buttons(self) -> None:
        """
        Clears the floating buttons from the screen.
        """
        for i in self.labels:
            i.place_forget()
        self.i = 0
            
    def open_other_buttons(self, e=None) -> None:
        """
        Opens or closes the floating buttons.

        Args:
            e (tk.Event): The event triggering the method.
        """
        if not self.label_toggle:
            self.place_buttons()
            self.label_toggle = not self.label_toggle
        else:
            self.clear_buttons()
            self.label_toggle = not self.label_toggle

    def open_next_page(self, id: int, e=None ) -> None:
        """
        Opens the next page based on the button clicked.

        Args:
            e (tk.Event): The event triggering the method.
            id (int): The ID of the button clicked.
        """
        self.place_forget()
        self.clear_buttons()
        self.parent.change_page(id)

    def get_button_image(self, image_name, size=(40, 40)) -> ImageTk.PhotoImage:
        """
        Retrieves the image for the button.

        Args:
            image_name (str): The name of the image file.

        Returns:
            ImageTk.PhotoImage: The image for the button.
        """
        image_path = os.path.join(os.getcwd(), 'Images', f'{image_name}.png')
        img = Image.open(image_path)

        self.photo = ctk.CTkImage(
            dark_image=img,
            light_image=img,
            size=size  # Explicitly set the display size
        )
        self.photos.append(self.photo)
        return self.photo

    def place_button(self):
        self.place(relx=0.95, y=50, anchor='ne')
    









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

    def voices(self):

        # Get the voices from the "say" command
        result = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)

        voices = []
        for line in result.stdout.splitlines():
            parts = line.split("#")
            if len(parts) == 2:
                name_and_lang = parts[0].strip().split(maxsplit=1)
                if len(name_and_lang) == 2:
                    name, lang = name_and_lang
                    description = parts[1].strip()
                    voices.append({"name": name, "language": lang, "description": description})

        # Save as JSON file
        # with open("macos_voices.json", "w", encoding="utf-8") as f:
            # json.dump(voices, f, indent=4, ensure_ascii=False)

        # print("Saved as macos_voices.json")
        return voices

    def speech(self, text: str, voice) -> None:
        """
        Convert the text to speech and play it.

        Args:
            text (str): The text to be converted to speech.

        Returns:
            None
        """
        current_os = platform.system()

        
        if current_os == 'Darwin':
            subprocess.run(["say", "-v", f"{voice}", "-o", os.path.join(os.getcwd(), 'Sound', 'prompt.aiff'), text])
            try:
                # say(True, text)
                self.y, self.sr = librosa.load(self.output_file, sr=None)
            except Exception as e:
                print(f"Error loading audio file: {e}")
            # self.voices()
        else:
            engine = pyttsx3.init(driverName='nsss') 
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)  # Change index if neede
            output_path = os.path.join(os.getcwd(), 'Sound', 'prompt.aiff')
            engine.save_to_file(text, output_path)
            engine.runAndWait()

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




