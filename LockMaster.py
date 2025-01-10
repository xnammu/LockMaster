import os
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
from cryptography.fernet import Fernet
import random
import winsound

# Lock/Unlock functions
def lock_item():
    path = path_entry.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        subprocess.run(["cacls", path, "/e", "/p", "everyone:n"], check=True, shell=True)
        messagebox.showinfo("Success", "File/Folder locked successfully.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to lock the file/folder.")

def unlock_item():
    path = path_entry.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        subprocess.run(["cacls", path, "/e", "/p", "everyone:f"], check=True, shell=True)
        messagebox.showinfo("Success", "File/Folder unlocked successfully.")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to unlock the file/folder.")

# Encrypt/Decrypt functions with encryption
def generate_key():
    return Fernet.generate_key()

def save_key(key):
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def encrypt_file(path, progress_var, progress_bar):
    key = generate_key()
    save_key(key)
    fernet = Fernet(key)

    file_size = os.path.getsize(path)
    progress_var.set(0)  # Reset progress

    with open(path, "rb") as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    chunk_size = 1024  # Chunk size in bytes
    num_chunks = len(encrypted) // chunk_size

    with open(path, "wb") as encrypted_file:
        for i in range(0, len(encrypted), chunk_size):
            encrypted_file.write(encrypted[i:i+chunk_size])
            progress = (i + chunk_size) / len(encrypted) * 100
            progress_var.set(progress)
            progress_bar.update_idletasks()

def decrypt_file(path, progress_var, progress_bar):
    key = load_key()
    fernet = Fernet(key)

    file_size = os.path.getsize(path)
    progress_var.set(0)  # Reset progress

    with open(path, "rb") as encrypted_file:
        encrypted = encrypted_file.read()

    decrypted = fernet.decrypt(encrypted)

    chunk_size = 1024  # Chunk size in bytes
    num_chunks = len(decrypted) // chunk_size

    with open(path, "wb") as decrypted_file:
        for i in range(0, len(decrypted), chunk_size):
            decrypted_file.write(decrypted[i:i+chunk_size])
            progress = (i + chunk_size) / len(decrypted) * 100
            progress_var.set(progress)
            progress_bar.update_idletasks()

def encrypt_item():
    path = path_entry.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        encrypt_file(path, progress_var, progress_bar)
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        messagebox.showinfo("Success", "File/Folder encrypted successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to encrypt the: {e}")

def decrypt_item():
    path = path_entry.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        decrypt_file(path, progress_var, progress_bar)
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        messagebox.showinfo("Success", "File/Folder decrypted successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to decrypt the : {e}")

# Browse for file or folder
def browse_item():
    path = filedialog.askopenfilename() or filedialog.askdirectory()
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

# Matrix Rain Background
def matrix_rain(canvas):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    rain = ["Lock", "Master"]
    for _ in range(25):
        x = random.randint(0, width)
        y = random.randint(0, height)
        char = random.choice(rain)
        canvas.create_text(x, y, text=char, fill="#00FF00", font=("Consolas", random.randint(9, 13)))
    canvas.after(25, matrix_rain, canvas)

# Create the main application window
app = tk.Tk()
# Set window title with lock emoji
app.title("LockMaster")
# Set the window icon using the resource_path function
app.iconbitmap(r'D:\Nammu\LockMaster\icon32.ico')
# Disable window resizing
app.resizable(False, False)

# Disable maximizing the window (remove the maximize button)
app.attributes('-fullscreen', False)  # To disable fullscreen (maximizing)
app.geometry("320x320")
app.configure(bg="#0f0f0f")

# Create a canvas for the matrix rain background
matrix_canvas = tk.Canvas(app, bg="#0f0f0f", highlightthickness=0)
matrix_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Header
header = tk.Label(app, text="🔒 LockMaster", font=("Consolas", 18, "bold"), bg="#0f0f0f", fg="#00FF00")
header.pack(pady=10)

# Path selection components
path_label = tk.Label(app, text="Select File or Folder:", font=("Consolas", 12), bg="#0f0f0f", fg="#FFFFFF")
path_label.pack(pady=5)

path_entry = tk.Entry(app, width=30, font=("Consolas", 12), bg="#1e1e1e", fg="#00FF00", insertbackground="#00FF00")
path_entry.pack(pady=5)

browse_button = tk.Button(app, text="Browse", command=browse_item, font=("Consolas", 12), bg="#1e1e1e", fg="#00FF00", activebackground="#00FF00", activeforeground="#0f0f0f")
browse_button.pack(pady=5)

# Progress bar for Encrypt/Decrypt
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, length=273, mode="determinate", variable=progress_var)
progress_bar.pack(pady=5)


# Create a frame for Lock/Unlock buttons
lock_frame = tk.Frame(app, bg="#0f0f0f")
lock_frame.pack(pady=5)

# Lock/Unlock Buttons (side by side)
lock_button = tk.Button(lock_frame, text="Lock", command=lock_item, font=("Consolas", 12), bg="#FF0000", fg="#FFFFFF", activebackground="#FF4444", activeforeground="#FFFFFF")
lock_button.pack(side=tk.LEFT, padx=5)

unlock_button = tk.Button(lock_frame, text="Unlock", command=unlock_item, font=("Consolas", 12), bg="#00FF00", fg="#0f0f0f", activebackground="#88FF88", activeforeground="#0f0f0f")
unlock_button.pack(side=tk.LEFT, padx=5)

# Create a frame for Encrypt/Decrypt buttons
encrypt_frame = tk.Frame(app, bg="#0f0f0f")
encrypt_frame.pack(pady=10)

# Encrypt/Decrypt Buttons
encrypt_button = tk.Button(encrypt_frame, text="Encrypt", command=encrypt_item, font=("Consolas", 12), bg="#FF0000", fg="#FFFFFF", activebackground="#FF4444", activeforeground="#FFFFFF")
encrypt_button.pack(side=tk.LEFT, padx=5)

decrypt_button = tk.Button(encrypt_frame, text="Decrypt", command=decrypt_item, font=("Consolas", 12), bg="#00FF00", fg="#0f0f0f", activebackground="#88FF88", activeforeground="#0f0f0f")
decrypt_button.pack(side=tk.LEFT, padx=5)


# Footer copyright
footer = tk.Label(app, text="Made with ❤️ by Navneet Singh", font=("Segoe UI Emoji" , 10, "bold"), bg="#0f0f0f", fg="#FFFFFF")
footer.pack(side=tk.BOTTOM)

# Start the matrix rain effect
matrix_rain(matrix_canvas)

# Run the application
app.mainloop()
