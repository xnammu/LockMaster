import os
import sys
import subprocess
import shutil
import tempfile
import zipfile
import random
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from cryptography.fernet import Fernet

# Platform detection
IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"
FONT_MONO = "Menlo" if IS_MAC else "Consolas"

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def play_sound(sound_type="success"):
    """Play alert/success sounds across macOS and Windows."""
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

# Key management
def get_key_save_path(target_path=None):
    """Determine a safe, writable path to save secret.key."""
    default_dir = os.path.expanduser("~/.lockmaster")
    try:
        os.makedirs(default_dir, exist_ok=True)
        return os.path.join(default_dir, "secret.key")
    except Exception:
        return os.path.abspath("secret.key")

def save_key(key, target_path=None):
    """Save key safely in user home directory and current directory if writable."""
    save_path = get_key_save_path(target_path)
    with open(save_path, "wb") as key_file:
        key_file.write(key)
    try:
        cwd_key = os.path.abspath("secret.key")
        if os.access(os.path.dirname(cwd_key), os.W_OK):
            with open(cwd_key, "wb") as key_file:
                key_file.write(key)
    except Exception:
        pass

def load_key(target_path=None):
    """Search for secret.key in multiple standard locations."""
    candidates = []
    if target_path:
        if os.path.isdir(target_path):
            candidates.append(os.path.join(target_path, "secret.key"))
        else:
            candidates.append(os.path.join(os.path.dirname(os.path.abspath(target_path)), "secret.key"))
    candidates.append(os.path.expanduser("~/.lockmaster/secret.key"))
    candidates.append(os.path.abspath("secret.key"))
    candidates.append(resource_path("secret.key"))

    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            try:
                with open(cand, "rb") as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception:
                continue
    raise FileNotFoundError("secret.key could not be found. Please ensure secret.key exists.")

def generate_key():
    return Fernet.generate_key()

def is_path_locked(path):
    """Check if a file or folder is currently locked."""
    if not os.path.exists(path):
        return False
    if not os.access(path, os.R_OK):
        return True
    if IS_MAC:
        try:
            res = subprocess.run(["ls", "-ldO", path], capture_output=True, text=True)
            if "uchg" in res.stdout:
                return True
        except Exception:
            pass
    return False

# Lock / Unlock operations
def apply_lock(path):
    if IS_MAC:
        subprocess.run(["chflags", "nouchg", path], capture_output=True)
        subprocess.run(["chmod", "-N", path], capture_output=True)
        subprocess.run(["chmod", "000", path], check=True)
        subprocess.run(["chflags", "uchg", path], check=True)
    elif IS_WIN:
        subprocess.run(["cacls", path, "/e", "/p", "everyone:n"], check=True, shell=True)
    else:
        subprocess.run(["chmod", "000", path], check=True)

def apply_unlock(path):
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

def lock_item():
    path = path_entry.get().strip()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        apply_lock(path)
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
        apply_unlock(path)
        play_sound("success")
        item_type = "Folder" if os.path.isdir(path) else "File"
        messagebox.showinfo("Success", f"{item_type} unlocked successfully.")
    except Exception as e:
        play_sound("alert")
        messagebox.showerror("Error", f"Failed to unlock the file/folder: {e}")

# Encryption & Decryption
def encrypt_single_file(path, progress_var, progress_bar):
    key = generate_key()
    save_key(key, path)
    fernet = Fernet(key)

    progress_var.set(0)
    with open(path, "rb") as file:
        original = file.read()

    encrypted = fernet.encrypt(original)
    chunk_size = 1024
    with open(path, "wb") as encrypted_file:
        for i in range(0, len(encrypted), chunk_size):
            encrypted_file.write(encrypted[i:i+chunk_size])
            progress = min(100.0, (i + chunk_size) / len(encrypted) * 100)
            progress_var.set(progress)
            progress_bar.update_idletasks()
    progress_var.set(100)

def decrypt_single_file(path, progress_var, progress_bar):
    key = load_key(path)
    fernet = Fernet(key)

    progress_var.set(0)
    with open(path, "rb") as encrypted_file:
        encrypted = encrypted_file.read()

    decrypted = fernet.decrypt(encrypted)
    chunk_size = 1024
    with open(path, "wb") as decrypted_file:
        for i in range(0, len(decrypted), chunk_size):
            decrypted_file.write(decrypted[i:i+chunk_size])
            progress = min(100.0, (i + chunk_size) / len(decrypted) * 100)
            progress_var.set(progress)
            progress_bar.update_idletasks()
    progress_var.set(100)

def encrypt_folder(folder_path, progress_var, progress_bar):
    key = generate_key()
    save_key(key, folder_path)
    fernet = Fernet(key)
    progress_var.set(0)
    progress_bar.update_idletasks()

    was_locked = is_path_locked(folder_path)
    if was_locked:
        apply_unlock(folder_path)

    try:
        # Collect all files to encrypt
        all_files = []
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if f.startswith('.') or f.endswith('.enc'):
                    continue
                all_files.append(os.path.join(root, f))

        if not all_files:
            progress_var.set(100)
            return 0

        for idx, fpath in enumerate(all_files):
            try:
                with open(fpath, "rb") as src:
                    data = src.read()
                encrypted = fernet.encrypt(data)
                enc_path = fpath + ".enc"
                with open(enc_path, "wb") as dst:
                    dst.write(encrypted)
                os.remove(fpath)
            except Exception as fe:
                print(f"Skipping {fpath}: {fe}")
            progress = ((idx + 1) / len(all_files)) * 100
            progress_var.set(progress)
            progress_bar.update_idletasks()

        return len(all_files)
    finally:
        if was_locked:
            apply_lock(folder_path)

def decrypt_folder(folder_path, progress_var, progress_bar):
    key = load_key(folder_path)
    fernet = Fernet(key)
    progress_var.set(0)
    progress_bar.update_idletasks()

    was_locked = is_path_locked(folder_path)
    if was_locked:
        apply_unlock(folder_path)

    try:
        # Collect all .enc files
        enc_files = []
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if f.endswith('.enc'):
                    enc_files.append(os.path.join(root, f))

        if not enc_files:
            progress_var.set(100)
            return 0

        for idx, enc_path in enumerate(enc_files):
            try:
                with open(enc_path, "rb") as src:
                    encrypted = src.read()
                decrypted = fernet.decrypt(encrypted)
                orig_path = enc_path[:-4]
                with open(orig_path, "wb") as dst:
                    dst.write(decrypted)
                os.remove(enc_path)
            except Exception as fe:
                print(f"Skipping {enc_path}: {fe}")
            progress = ((idx + 1) / len(enc_files)) * 100
            progress_var.set(progress)
            progress_bar.update_idletasks()

        return len(enc_files)
    finally:
        if was_locked:
            apply_lock(folder_path)

def encrypt_item():
    path = path_entry.get().strip()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        if os.path.isdir(path):
            count = encrypt_folder(path, progress_var, progress_bar)
            play_sound("success")
            messagebox.showinfo("Success", f"Folder encrypted successfully ({count} files encrypted).")
        else:
            encrypt_single_file(path, progress_var, progress_bar)
            play_sound("success")
            messagebox.showinfo("Success", "File encrypted successfully.")
    except Exception as e:
        play_sound("alert")
        messagebox.showerror("Error", f"Failed to encrypt: {e}")

def decrypt_item():
    path = path_entry.get().strip()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        if os.path.isdir(path):
            count = decrypt_folder(path, progress_var, progress_bar)
            play_sound("success")
            messagebox.showinfo("Success", f"Folder decrypted successfully ({count} files restored).")
        else:
            decrypt_single_file(path, progress_var, progress_bar)
            play_sound("success")
            messagebox.showinfo("Success", "File decrypted successfully.")
    except Exception as e:
        play_sound("alert")
        messagebox.showerror("Error", f"Failed to decrypt: {e}")

# Separate File and Folder Browsers for clear UX
def browse_file():
    path = filedialog.askopenfilename(title="Select File to Lock/Encrypt")
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

def browse_folder():
    path = filedialog.askdirectory(title="Select Folder to Lock/Encrypt")
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

# Matrix Rain Animation
def matrix_rain(canvas):
    try:
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width > 1 and height > 1:
            rain = ["Lock", "Master", "0", "1", "AES", "KEY", "MAC"]
            for _ in range(25):
                x = random.randint(0, width)
                y = random.randint(0, height)
                char = random.choice(rain)
                canvas.create_text(x, y, text=char, fill="#00FF00", font=(FONT_MONO, random.randint(9, 13)))
        canvas.after(35, matrix_rain, canvas)
    except Exception:
        pass

# Ensure default key exists in ~/.lockmaster if present locally
try:
    initial_key = resource_path("secret.key")
    if os.path.exists(initial_key):
        home_key = os.path.expanduser("~/.lockmaster/secret.key")
        if not os.path.exists(home_key):
            os.makedirs(os.path.dirname(home_key), exist_ok=True)
            shutil.copyfile(initial_key, home_key)
except Exception:
    pass

# Main GUI Application
app = tk.Tk()
app.title("LockMaster")
app.geometry("360x380")
app.resizable(False, False)
app.configure(bg="#0f0f0f")

# Window icon
try:
    png_icon = resource_path("icon.png")
    if os.path.exists(png_icon):
        app_icon = tk.PhotoImage(file=png_icon)
        app.iconphoto(True, app_icon)
    elif IS_WIN:
        ico_path = resource_path("icon32.ico")
        if os.path.exists(ico_path):
            app.iconbitmap(ico_path)
except Exception:
    pass

# Matrix rain background canvas
matrix_canvas = tk.Canvas(app, bg="#0f0f0f", highlightthickness=0)
matrix_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Header
header = tk.Label(app, text="🔒 LockMaster", font=(FONT_MONO, 18, "bold"), bg="#0f0f0f", fg="#00FF00")
header.pack(pady=8)

# Path selection
path_label = tk.Label(app, text="Select File or Folder:", font=(FONT_MONO, 11), bg="#0f0f0f", fg="#FFFFFF")
path_label.pack(pady=3)

path_entry = tk.Entry(
    app, width=33, font=(FONT_MONO, 11),
    bg="#1e1e1e", fg="#00FF00", insertbackground="#00FF00",
    highlightthickness=1, highlightcolor="#00FF00", highlightbackground="#333333"
)
path_entry.pack(pady=4)

def make_button(parent, text, command, btn_style="action", width=10):
    if IS_WIN:
        if btn_style == "danger":
            return tk.Button(parent, text=text, command=command, font=(FONT_MONO, 10, "bold"), bg="#FF0000", fg="#FFFFFF", activebackground="#FF4444", activeforeground="#FFFFFF", width=width)
        elif btn_style == "success":
            return tk.Button(parent, text=text, command=command, font=(FONT_MONO, 10, "bold"), bg="#00FF00", fg="#0f0f0f", activebackground="#88FF88", activeforeground="#0f0f0f", width=width)
        else:
            return tk.Button(parent, text=text, command=command, font=(FONT_MONO, 10), bg="#1e1e1e", fg="#00FF00", activebackground="#00FF00", activeforeground="#0f0f0f", width=width)
    else:
        # macOS Aqua styling
        fg_col = "#FF4444" if btn_style == "danger" else ("#00FF00" if btn_style == "success" else "#00FF00")
        return tk.Button(
            parent, text=text, command=command, font=(FONT_MONO, 10, "bold"),
            fg=fg_col, highlightbackground="#0f0f0f", width=width
        )

# Browse buttons (File & Folder)
browse_frame = tk.Frame(app, bg="#0f0f0f")
browse_frame.pack(pady=4)

browse_file_btn = make_button(browse_frame, "Browse File", browse_file, "action", width=12)
browse_file_btn.pack(side=tk.LEFT, padx=5)

browse_folder_btn = make_button(browse_frame, "Browse Folder", browse_folder, "action", width=12)
browse_folder_btn.pack(side=tk.LEFT, padx=5)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, length=290, mode="determinate", variable=progress_var)
progress_bar.pack(pady=6)

# Lock / Unlock Frame
lock_frame = tk.Frame(app, bg="#0f0f0f")
lock_frame.pack(pady=4)

lock_button = make_button(lock_frame, "Lock", lock_item, "danger", width=10)
lock_button.pack(side=tk.LEFT, padx=6)

unlock_button = make_button(lock_frame, "Unlock", unlock_item, "success", width=10)
unlock_button.pack(side=tk.LEFT, padx=6)

# Encrypt / Decrypt Frame
encrypt_frame = tk.Frame(app, bg="#0f0f0f")
encrypt_frame.pack(pady=6)

encrypt_button = make_button(encrypt_frame, "Encrypt", encrypt_item, "danger", width=10)
encrypt_button.pack(side=tk.LEFT, padx=6)

decrypt_button = make_button(encrypt_frame, "Decrypt", decrypt_item, "success", width=10)
decrypt_button.pack(side=tk.LEFT, padx=6)

# Footer
footer = tk.Label(app, text="Made with ❤️ by Navneet Singh", font=(FONT_MONO, 9, "bold"), bg="#0f0f0f", fg="#888888")
footer.pack(side=tk.BOTTOM, pady=6)

# Start matrix rain
matrix_rain(matrix_canvas)

if __name__ == "__main__":
    app.mainloop()
