from tkinter import *
from tkinter import Scale
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from PIL import Image, ImageTk
import configparser
import os
import json


class FileHandler:
    # data cannot be shared with other classes with class instances, each intances are independent
    # use class variables instead
    config_file = "config.ini"
    config = configparser.ConfigParser()
    file_path = None
    # decorator to change behaviour (cls), operates itself rather than instances

    @classmethod
    def ask_file_path(cls):
        if os.path.exists(cls.config_file):
            cls.config.read(cls.config_file)
            cls.file_path = cls.config.get("Settings", "file_path")
        else:
            cls.file_path = None
        selected_file_path = fd.askopenfilename(defaultextension='.txt', filetypes=[
            ('All Files', '*.*'), ("Text File", "*.txt")])

        if selected_file_path:
            cls.file_path = selected_file_path
            cls.config["Settings"] = {"file_path": cls.file_path}
            with open(cls.config_file, "w") as config_file:
                cls.config.write(config_file)

        return cls.file_path

    # Have to clear file path here before parsing
    @classmethod
    def clear_file_path(cls):
        cls.file_path = None


class openFile:
    # if text file is too big, it will crash the program
    def open_existing_file():
        # calls a seperate class for function
        file_handler = FileHandler()
        selected_file_path = file_handler.ask_file_path()

        if selected_file_path:
            with open(selected_file_path, "r") as file:
                try:
                    content = file.read()
                    text_area.delete("1.0", "end")  # Clear previous content
                    text_area.insert("1.0", content)
                    try:
                        openFile.load_formatting_info()
                    except:
                        mb.showerror("Error", "Cannot call formating method")
                    try:
                        root.title(selected_file_path)
                    except:
                        mb.showerror(message="Cannot save current file path")
                except:
                    mb.showerror(message="Cannot write file to text area")

    def load_formatting_info():
        try:
            with open("formatting_info.json", "r") as f:
                formatting_info = json.load(f)
                alignment = formatting_info.get("alignment")
                if alignment:
                    if alignment == "center":
                        textFormat.center_align()
                    elif alignment == "left":
                        textFormat.left_align()
                    elif alignment == "right":
                        textFormat.right_align()

        except Exception as e:
            mb.showerror("Error", "Unable to read from format json file")


class openNewFile:
    def create_new_file():
        root.title("Untitled - Text Editor")
        text_area.delete(1.0, END)
        try:
            FileHandler.clear_file_path()
        except Exception as e:
            mb.showerror("Error", e)


class saveFile:

    def save_as():
        global file
        if not file:
            file = None
        else:
            with open(file, "w") as f:
                f.write(text_area.get(1.0, END))
        # no asteriks for saving
        if file is None or file:
            try:
                file = fd.asksaveasfilename(defaultextension='.txt',
                                            filetypes=[("Text File", ".txt")])
                with open(file, "w") as f:
                    f.write(text_area.get(1.0, END))
                #
                alignment = textFormat.alignment
                formattingHandler.save_format_info(alignment)
                #
                root.title(file)
            except Exception as e:
                mb.showerror("Save as is not functioning", e)

    def save_current():
        # declare and unpack sharable class variables
        file_path = FileHandler.file_path

        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(text_area.get(1.0, END))
                # uses textFormat class attribute
                alignment = textFormat.alignment
                formattingHandler.save_format_info(alignment)

        #  add saving format here later
            except Exception as e:
                mb.showerror("Error", e)
        elif file_path is None:
            try:
                saveFile.save_as()
            except Exception as e:
                mb.showerror("Error", e)


class exitApplication:
    def exiting():
        exit_save = """
        Do you want to save before closing?
        """
        response = mb.askyesnocancel(title="Exiting", message=exit_save)
        if response == True:
            if FileHandler.file_path:
                saveFile.save_current()
                root.destroy()
            else:
                saveFile.save_as()
                root.destroy()
        elif response == False:
            root.destroy()
        else:
            return


class formattingHandler:

    def save_format_info(alignment):
        formatting_info = {"alignment": alignment}
        try:
            with open("formatting_info.json", "w") as f:
                json.dump(formatting_info, f)
        except Exception as e:
            mb.showerror(
                "Error", f"Unable to save text format into json file: {e}")

# Format is applied to all texts


class textFormat:
    alignment = None

    def apply_alignment(alignment):
        try:
            text_area.tag_configure(alignment, justify=alignment)
            text_area.tag_add(alignment, "1.0", "end")
            textFormat.alignment = alignment  # Update the stored alignment. IMPORTANT
        except Exception as e:
            mb.showerror("Error", f"Cannnot {alignment} text: {e}")

    # Remove previously assigned tags before applying a new one

    def clear_tags():
        text_area.tag_remove("center", "1.0", "end")
        text_area.tag_remove("left", "1.0", "end")
        text_area.tag_remove("right", "1.0", "end")

    def center_align():
        textFormat.clear_tags()
        textFormat.apply_alignment("center")

    def left_align():
        textFormat.clear_tags()
        textFormat.apply_alignment("left")

    def right_align():
        textFormat.clear_tags()
        textFormat.apply_alignment("right")


class copyText:
    def copying():
        text_area.event_generate("<<Copy>>")


class cutText:
    def cutting():
        text_area.event_generate("<<Cut>>")


class pasteText:
    def pasting():
        text_area.event_generate("<<Paste>>")


class selectAll:
    def everything():
        text_area.event_generate("<<SelectAll>>")


class deleteLastChar():
    def deleting():
        text_area.event_generate("<<Delete>>")


class aboutTextEditor():
    def pop():
        mb.showinfo("About this text editor",
                    "This text editor could fly you to space.")


class aboutCommands():
    def about():
        commands = """
        File Menu:
        - 'New' opens a new .txt file
        - 'Open' opens an existing file
        - 'Save As' save your .txt files in a directory

        Edit Menu (Right Click):
        - 'Copy' copies selected texts
        - 'Cut' cuts selected texts
        - 'Paste' pastes copied/cut texts
        - 'Select All' selects the entire text
        - 'Delete' gets rid of selected texts entirely
        """
        mb.showinfo(title="All commands", message=commands)


class entryDoable:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def track_changes(self, event: Event = None):
        if event and event.char != '\x1a' and event.keysym != 'y':
            self.undo_stack.append(text_area.get("1.0", "end-1c"))

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(text_area.get("1.0", "end-1c"))
            text_area.delete("1.0", "end")
            text_area.insert("1.0", self.undo_stack.pop())

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(text_area.get("1.0", "end-1c"))
            text_area.delete("1.0", "end")
            text_area.insert("1.0", self.redo_stack.pop())

    def handle_undo(self, event: Event = None):
        self.undo()
        return 'break'

    def handle_redo(self, event: Event = None):
        self.redo()
        return 'break'


class imageHandler:
    def __init__(self):
        self.scale = Scale(root, from_=10, to=100,
                           orient="horizontal", label="Resize Image")
        self.scale.grid(row=0, column=10)

    def insert_img(self):
        file_path = fd.askopenfilename(
            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")])

        if file_path:
            try:
                load = Image.open(file_path)
                # resize image
                scale_factor = self.scale.get() / 100.0
                resized_image = load.resize(
                    (int(load.width * scale_factor), int(load.height * scale_factor)))

                render = ImageTk.PhotoImage(resized_image)

                img = Label(image=render)
                img.image = render
                img.place(x=0, y=0)
            except Exception as e:
                mb.showerror("Error", e)

# global method without class


def pop_menu(event):
    right_pop_up.tk_popup(event.x_root, event.y_root)


if __name__ == "__main__":
    # Initiailize window
    root = Tk()

    root.title("Untitled - Text Editor")
    root.geometry('800x500')
    root.resizable(0, 0)

    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # convert to raw string, or else backlash will be considered as  special character
    icon = ImageTk.PhotoImage(Image.open(
        r"C:\Users\limsi\OneDrive\Desktop\Text Editor_Python\src\Notepad.png"))
    root.iconphoto(False, icon)
    file = ''

    # Menu initialize
    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    # Text editor initialize

    # Components of Text Editor window
    text_area = Text(root, font=("Times New Roman", 12))
    text_area.grid(sticky=NSEW)
    # Key binds
    entry = entryDoable()
    text_area.bind("<Key>", entry.track_changes)
    text_area.bind("<Control-z>", entry.handle_undo)
    text_area.bind("<Control-y>", entry.handle_redo)

    scroller = Scrollbar(text_area, orient=VERTICAL)
    scroller.pack(side=RIGHT, fill=Y)

    scroller.config(command=text_area.yview)
    text_area.config(yscrollcommand=scroller.set)  # scrolling function

    # right click pop up
    right_pop_up = Menu(text_area, tearoff=0, bg="white", fg="black")
    img = imageHandler()
    right_pop_up.add_cascade(
        label="Insert Image", command=img.insert_img)
    right_pop_up.add_separator()
    right_pop_up.add_command(
        label="Undo", command=entry.undo, accelerator="Ctrl+Z")
    right_pop_up.add_command(
        label="Redo", command=entry.redo, accelerator="Ctrl+Y")
    right_pop_up.add_separator()
    right_pop_up.add_command(label="Copy", command=copyText.copying)
    right_pop_up.add_command(label="Cut", command=cutText.cutting)
    right_pop_up.add_command(label="Paste", command=pasteText.pasting)
    right_pop_up.add_separator()
    right_pop_up.add_command(label="Select All", command=selectAll.everything)
    right_pop_up.add_command(label="Delete", command=deleteLastChar.deleting)
    text_area.bind("<Button - 3>", pop_menu)

    # Adding components for File Menu
    file_menu = Menu(menu_bar, tearoff=False, activebackground='DodgerBlue')

    file_menu.add_command(label="New", command=openNewFile.create_new_file)
    file_menu.add_command(
        label="Open File", command=openFile.open_existing_file)
    file_menu.add_command(label="Save", command=saveFile.save_current)
    file_menu.add_command(label="Save As", command=saveFile.save_as)
    file_menu.add_separator()
    file_menu.add_command(label="Close File", command=exitApplication.exiting)

    menu_bar.add_cascade(label="File", menu=file_menu)

    # Adding the components for edit menu
    edit_menu = Menu(menu_bar, tearoff=False, activebackground='DodgerBlue')

    edit_menu.add_command(
        label='Undo', command=entry.undo, accelerator="Ctrl+Z")
    edit_menu.add_command(
        label='Redo', command=entry.redo, accelerator="Ctrl+Y")
    edit_menu.add_separator()
    edit_menu.add_command(label='Copy', command=copyText.copying)
    edit_menu.add_command(label='Cut', command=cutText.cutting)
    edit_menu.add_command(label='Paste', command=pasteText.pasting)
    edit_menu.add_separator()
    edit_menu.add_command(label='Select All', command=selectAll.everything)
    edit_menu.add_command(label='Delete', command=deleteLastChar.deleting)

    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # Adding components for Help Menu
    help_menu = Menu(menu_bar, tearoff=False, activebackground='DodgerBlue')

    help_menu.add_command(label='About this text editor',
                          command=aboutTextEditor.pop)
    help_menu.add_command(label='About Commands', command=aboutCommands.about)

    menu_bar.add_cascade(label="Help", menu=help_menu)

    # Text align component
    text_justify = Menu(menu_bar, tearoff=False, activebackground='DodgerBlue')
    # center
    icon_center = Image.open(
        r"C:\Users\limsi\OneDrive\Desktop\Text Editor_Python\src\align_center.png")
    resize_icon_center = icon_center.resize((30, 30))
    icon_center_tk = ImageTk.PhotoImage(resize_icon_center)
    # left
    icon_left = Image.open(
        r"C:\Users\limsi\OneDrive\Desktop\Text Editor_Python\src\align_left.png")
    resize_icon_left = icon_left.resize((30, 30))
    icon_left_tk = ImageTk.PhotoImage(resize_icon_left)
    # right
    icon_right = Image.open(
        r"C:\Users\limsi\OneDrive\Desktop\Text Editor_Python\src\align_right.png")
    resize_icon_right = icon_right.resize((30, 30))
    icon_right_tk = ImageTk.PhotoImage(resize_icon_right)

    text_justify.add_command(label="Center", image=icon_center_tk,
                             compound="left", command=textFormat.center_align)
    text_justify.add_separator()
    text_justify.add_command(label="Left", image=icon_left_tk,
                             compound="left", command=textFormat.left_align)
    text_justify.add_separator()
    text_justify.add_command(label="Right", image=icon_right_tk,
                             compound="left", command=textFormat.right_align)
    menu_bar.add_cascade(label='Text Alignment', menu=text_justify)
    menu_bar.add_cascade(label="( Image saving not supported )")

    # Finalize by window update and starter
    root.update()
    root.protocol("WM_DELETE_WINDOW", exitApplication.exiting)
    root.mainloop()
