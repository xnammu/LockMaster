import os
import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog
import random

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

def browse_item():
    path = filedialog.askopenfilename() or filedialog.askdirectory()
    if path:
        path_entry.delete(0, tk.END)
        path_entry.insert(0, path)

def create_matrix_rain(canvas):
    canvas.delete("all")
    width = canvas.winfo_width()
    height = canvas.winfo_height()
    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        char = random.choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        canvas.create_text(x, y, text=char, fill="#00FF00", font=("Consolas", 12))
    canvas.after(100, create_matrix_rain, canvas)

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
