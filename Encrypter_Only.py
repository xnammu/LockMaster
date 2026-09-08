import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from cryptography.fernet import Fernet
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

def generate_key():
    return Fernet.generate_key()

def get_key_save_path(target_path=None):
    default_dir = os.path.expanduser("~/.lockmaster")
    try:
        os.makedirs(default_dir, exist_ok=True)
        return os.path.join(default_dir, "secret.key")
    except Exception:
        return os.path.abspath("secret.key")

def save_key(key, target_path=None):
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
    candidates = []
    if target_path:
        if os.path.isdir(target_path):
            candidates.append(os.path.join(target_path, "secret.key"))
        else:
            candidates.append(os.path.join(os.path.dirname(os.path.abspath(target_path)), "secret.key"))
    candidates.append(os.path.expanduser("~/.lockmaster/secret.key"))
    candidates.append(os.path.abspath("secret.key"))

    for cand in candidates:
        if os.path.exists(cand) and os.path.isfile(cand):
            try:
                with open(cand, "rb") as f:
                    content = f.read().strip()
                    if content:
                        return content
            except Exception:
                continue
    raise FileNotFoundError("secret.key could not be found.")

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

def decrypt_folder(folder_path, progress_var, progress_bar):
    key = load_key(folder_path)
    fernet = Fernet(key)
    progress_var.set(0)
    progress_bar.update_idletasks()

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

def browse_file():
    path = filedialog.askopenfilename(title="Select File to Encrypt")
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

def browse_folder():
    path = filedialog.askdirectory(title="Select Folder to Encrypt")
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
                canvas.create_text(x, y, text=char, fill="#00FF00", font=(FONT_MONO, random.randint(10, 14)))
        canvas.after(50, create_matrix_rain, canvas)
    except Exception:
        pass

app = tk.Tk()
app.title("File/Folder Encryption")
app.geometry("600x440")
app.configure(bg="#0f0f0f")

matrix_canvas = tk.Canvas(app, bg="#0f0f0f", highlightthickness=0)
matrix_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

header = tk.Label(app, text="🔒 File/Folder Encrypt & Decrypt", font=(FONT_MONO, 18, "bold"), bg="#0f0f0f", fg="#00FF00")
header.pack(pady=15)

path_label = tk.Label(app, text="Select File or Folder:", font=(FONT_MONO, 12), bg="#0f0f0f", fg="#FFFFFF")
path_label.pack(pady=5)

path_entry = tk.Entry(app, width=50, font=(FONT_MONO, 12), bg="#1e1e1e", fg="#00FF00", insertbackground="#00FF00")
path_entry.pack(pady=5)

browse_frame = tk.Frame(app, bg="#0f0f0f")
browse_frame.pack(pady=8)

if IS_WIN:
    browse_file_btn = tk.Button(browse_frame, text="Browse File", command=browse_file, font=(FONT_MONO, 11), bg="#1e1e1e", fg="#00FF00", activebackground="#00FF00", activeforeground="#0f0f0f")
    browse_folder_btn = tk.Button(browse_frame, text="Browse Folder", command=browse_folder, font=(FONT_MONO, 11), bg="#1e1e1e", fg="#00FF00", activebackground="#00FF00", activeforeground="#0f0f0f")
    lock_button = tk.Button(app, text="Encrypt", command=encrypt_item, font=(FONT_MONO, 12), bg="#FF0000", fg="#FFFFFF", activebackground="#FF4444", activeforeground="#FFFFFF")
    unlock_button = tk.Button(app, text="Decrypt", command=decrypt_item, font=(FONT_MONO, 12), bg="#00FF00", fg="#0f0f0f", activebackground="#88FF88", activeforeground="#0f0f0f")
else:
    browse_file_btn = tk.Button(browse_frame, text="Browse File", command=browse_file, font=(FONT_MONO, 11, "bold"), fg="#00FF00", highlightbackground="#0f0f0f")
    browse_folder_btn = tk.Button(browse_frame, text="Browse Folder", command=browse_folder, font=(FONT_MONO, 11, "bold"), fg="#00FF00", highlightbackground="#0f0f0f")
    lock_button = tk.Button(app, text="Encrypt", command=encrypt_item, font=(FONT_MONO, 12, "bold"), fg="#FF4444", highlightbackground="#0f0f0f")
    unlock_button = tk.Button(app, text="Decrypt", command=decrypt_item, font=(FONT_MONO, 12, "bold"), fg="#00FF00", highlightbackground="#0f0f0f")

browse_file_btn.pack(side=tk.LEFT, padx=6)
browse_folder_btn.pack(side=tk.LEFT, padx=6)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=8)

lock_button.pack(pady=8)
unlock_button.pack(pady=8)

footer = tk.Label(app, text="Made with ❤️ by Navneet Singh", font=(FONT_MONO, 10, "italic"), bg="#0f0f0f", fg="#FFFFFF")
footer.pack(side=tk.BOTTOM, pady=15)

create_matrix_rain(matrix_canvas)

if __name__ == "__main__":
    app.mainloop()
