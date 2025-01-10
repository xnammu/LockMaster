import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk  # Import ttk for Progressbar
from cryptography.fernet import Fernet
import random
import winsound

# Generate a key for encryption and decryption
def generate_key():
    return Fernet.generate_key()

# Save the key to a file (you can modify this to save it securely)
def save_key(key):
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Load the key from a file
def load_key():
    return open("secret.key", "rb").read()

def encrypt_file(path, progress_var, progress_bar):
    key = generate_key()
    save_key(key)
    fernet = Fernet(key)

    # Get the size of the file
    file_size = os.path.getsize(path)
    progress_var.set(0)  # Reset progress

    with open(path, "rb") as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    # Update progress as file is written in chunks
    chunk_size = 1024  # Chunk size in bytes
    num_chunks = len(encrypted) // chunk_size

    with open(path, "wb") as encrypted_file:
        for i in range(0, len(encrypted), chunk_size):
            encrypted_file.write(encrypted[i:i+chunk_size])
            progress = (i + chunk_size) / len(encrypted) * 100
            progress_var.set(progress)
            progress_bar.update_idletasks()  # Force the UI to update

def decrypt_file(path, progress_var, progress_bar):
    key = load_key()
    fernet = Fernet(key)

    # Get the size of the file
    file_size = os.path.getsize(path)
    progress_var.set(0)  # Reset progress

    with open(path, "rb") as encrypted_file:
        encrypted = encrypted_file.read()

    decrypted = fernet.decrypt(encrypted)

    # Update progress as file is written in chunks
    chunk_size = 1024  # Chunk size in bytes
    num_chunks = len(decrypted) // chunk_size

    with open(path, "wb") as decrypted_file:
        for i in range(0, len(decrypted), chunk_size):
            decrypted_file.write(decrypted[i:i+chunk_size])
            progress = (i + chunk_size) / len(decrypted) * 100
            progress_var.set(progress)
            progress_bar.update_idletasks()  # Force the UI to update

def lock_item():
    path = path_entry.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        encrypt_file(path, progress_var, progress_bar)
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
        messagebox.showinfo("Success", "File/Folder locked successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to lock the file/folder: {e}")

def unlock_item():
    path = path_entry.get()
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", "Please select a valid file or folder.")
        return

    try:
        decrypt_file(path, progress_var, progress_bar)
        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        messagebox.showinfo("Success", "File/Folder unlocked successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to unlock the file/folder: {e}")

def browse_item():
    path = filedialog.askopenfilename() or filedialog.askdirectory()
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

def create_matrix_rain(canvas):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    for _ in range(50):
        x = random.randint(0, width)
        y = random.randint(0, height)
        char = random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        canvas.create_text(x, y, text=char, fill="#00FF00", font=("Consolas", random.randint(10, 16)))
    canvas.after(50, create_matrix_rain, canvas)

# Create the main application window
app = tk.Tk()
app.title("File/Folder Lock/Unlock")
app.geometry("600x400")
app.configure(bg="#0f0f0f")

# Create a canvas for the matrix rain background
matrix_canvas = tk.Canvas(app, bg="#0f0f0f", highlightthickness=0)
matrix_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

# Header
header = tk.Label(app, text="🔒 File/Folder Lock & Unlock", font=("Consolas", 18, "bold"), bg="#0f0f0f", fg="#00FF00")
header.pack(pady=20)

# Path selection components
path_label = tk.Label(app, text="Select File or Folder:", font=("Consolas", 12), bg="#0f0f0f", fg="#FFFFFF")
path_label.pack(pady=5)

path_entry = tk.Entry(app, width=50, font=("Consolas", 12), bg="#1e1e1e", fg="#00FF00", insertbackground="#00FF00")
path_entry.pack(pady=5)

browse_button = tk.Button(app, text="Browse", command=browse_item, font=("Consolas", 12), bg="#1e1e1e", fg="#00FF00", activebackground="#00FF00", activeforeground="#0f0f0f")
browse_button.pack(pady=10)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(app, length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

# Lock and Unlock buttons
lock_button = tk.Button(app, text="Lock", command=lock_item, font=("Consolas", 12), bg="#FF0000", fg="#FFFFFF", activebackground="#FF4444", activeforeground="#FFFFFF")
lock_button.pack(pady=10)

unlock_button = tk.Button(app, text="Unlock", command=unlock_item, font=("Consolas", 12), bg="#00FF00", fg="#0f0f0f", activebackground="#88FF88", activeforeground="#0f0f0f")
unlock_button.pack(pady=10)

# Footer copyright
footer = tk.Label(app, text="Made with ❤️ by Navneet Singh", font=("Consolas", 10, "italic"), bg="#0f0f0f", fg="#FFFFFF")
footer.pack(side=tk.BOTTOM, pady=20)

# Start the matrix rain effect
create_matrix_rain(matrix_canvas)

# Run the application
app.mainloop()
