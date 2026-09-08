import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
import random

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
FONT_MONO = "Menlo" if IS_MAC else "Consolas"

def play_sound(sound_type="success"):
    try:
        if IS_MAC:
            sound_file = "/System/Library/Sounds/Ping.aiff" if sound_type == "success" else "/System/Library/Sounds/Glass.aiff"
            if os.path.exists(sound_file):
                subprocess.Popen(["afplay", sound_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif IS_WIN:
            import winsound
            alias = "SystemAsterisk" if sound_type == "success" else "SystemExclamation"
            winsound.PlaySound(alias, winsound.SND_ALIAS)
    except Exception:
        pass

def lock_item():
    path = path_entry.get().strip()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        if IS_MAC:
            subprocess.run(["chflags", "nouchg", path], capture_output=True)
            subprocess.run(["chmod", "-N", path], capture_output=True)
            subprocess.run(["chmod", "000", path], check=True)
            subprocess.run(["chflags", "uchg", path], check=True)
        elif IS_WIN:
            subprocess.run(["cacls", path, "/e", "/p", "everyone:n"], check=True, shell=True)
        else:
            subprocess.run(["chmod", "000", path], check=True)

        play_sound("success")
        item_type = "Folder" if os.path.isdir(path) else "File"
        messagebox.showinfo("Success", f"{item_type} locked successfully.")
    except Exception as e:
        play_sound("alert")
        messagebox.showerror("Error", f"Failed to lock the file/folder: {e}")

def unlock_item():
    path = path_entry.get().strip()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        if IS_MAC:
            subprocess.run(["chflags", "nouchg", path], capture_output=True)
            if os.path.isdir(path):
                subprocess.run(["chmod", "755", path], check=True)
            else:
                subprocess.run(["chmod", "644", path], check=True)
            subprocess.run(["chmod", "-N", path], capture_output=True)
        elif IS_WIN:
            subprocess.run(["cacls", path, "/e", "/p", "everyone:f"], check=True, shell=True)
        else:
            if os.path.isdir(path):
                subprocess.run(["chmod", "755", path], check=True)
            else:
                subprocess.run(["chmod", "644", path], check=True)

        play_sound("success")
        item_type = "Folder" if os.path.isdir(path) else "File"
        messagebox.showinfo("Success", f"{item_type} unlocked successfully.")
    except Exception as e:
        play_sound("alert")
        messagebox.showerror("Error", f"Failed to unlock the file/folder: {e}")

def browse_file():
    path = filedialog.askopenfilename(title="Select File to Lock")
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

def browse_folder():
    path = filedialog.askdirectory(title="Select Folder to Lock")
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

def create_matrix_rain(canvas):
    try:
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width > 1 and height > 1:
            for _ in range(30):
                x = random.randint(0, width)
                y = random.randint(0, height)
                char = random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                canvas.create_text(x, y, text=char, fill="#00FF00", font=(FONT_MONO, 12))
        canvas.after(100, create_matrix_rain, canvas)
    except Exception:
        pass

app = tk.Tk()
app.title("File/Folder Lock/Unlock")
app.geometry("600x420")
app.configure(bg="#0f0f0f")

matrix_canvas = tk.Canvas(app, bg="#0f0f0f", highlightthickness=0)
matrix_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

header = tk.Label(app, text="🔒 File/Folder Lock & Unlock", font=(FONT_MONO, 18, "bold"), bg="#0f0f0f", fg="#00FF00")
header.pack(pady=20)

path_label = tk.Label(app, text="Select File or Folder:", font=(FONT_MONO, 12), bg="#0f0f0f", fg="#FFFFFF")
path_label.pack(pady=5)

path_entry = tk.Entry(app, width=50, font=(FONT_MONO, 12), bg="#1e1e1e", fg="#00FF00", insertbackground="#00FF00")
path_entry.pack(pady=5)

browse_frame = tk.Frame(app, bg="#0f0f0f")
browse_frame.pack(pady=8)

if IS_WIN:
    browse_file_btn = tk.Button(browse_frame, text="Browse File", command=browse_file, font=(FONT_MONO, 11), bg="#1e1e1e", fg="#00FF00", activebackground="#00FF00", activeforeground="#0f0f0f")
    browse_folder_btn = tk.Button(browse_frame, text="Browse Folder", command=browse_folder, font=(FONT_MONO, 11), bg="#1e1e1e", fg="#00FF00", activebackground="#00FF00", activeforeground="#0f0f0f")
    lock_button = tk.Button(app, text="Lock", command=lock_item, font=(FONT_MONO, 12), bg="#FF0000", fg="#FFFFFF", activebackground="#FF4444", activeforeground="#FFFFFF")
    unlock_button = tk.Button(app, text="Unlock", command=unlock_item, font=(FONT_MONO, 12), bg="#00FF00", fg="#0f0f0f", activebackground="#88FF88", activeforeground="#0f0f0f")
else:
    browse_file_btn = tk.Button(browse_frame, text="Browse File", command=browse_file, font=(FONT_MONO, 11, "bold"), fg="#00FF00", highlightbackground="#0f0f0f")
    browse_folder_btn = tk.Button(browse_frame, text="Browse Folder", command=browse_folder, font=(FONT_MONO, 11, "bold"), fg="#00FF00", highlightbackground="#0f0f0f")
    lock_button = tk.Button(app, text="Lock", command=lock_item, font=(FONT_MONO, 12, "bold"), fg="#FF4444", highlightbackground="#0f0f0f")
    unlock_button = tk.Button(app, text="Unlock", command=unlock_item, font=(FONT_MONO, 12, "bold"), fg="#00FF00", highlightbackground="#0f0f0f")

browse_file_btn.pack(side=tk.LEFT, padx=6)
browse_folder_btn.pack(side=tk.LEFT, padx=6)

lock_button.pack(pady=10)
unlock_button.pack(pady=10)

footer = tk.Label(app, text="Made with ❤️ by Navneet Singh", font=(FONT_MONO, 10, "italic"), bg="#0f0f0f", fg="#FFFFFF")
footer.pack(side=tk.BOTTOM, pady=20)

create_matrix_rain(matrix_canvas)

if __name__ == "__main__":
    app.mainloop()
