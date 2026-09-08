# LockMaster

LockMaster is a cross-platform desktop application (macOS & Windows) that allows you to lock, unlock, encrypt, and decrypt files or folders. It features a hacker-style Matrix rain background, permission-based locking, and strong AES encryption.

---

## Features

- **Lock / Unlock:**
  - **macOS:** Applies immutable user locks (`chflags uchg`) displaying the native Finder lock badge + strict POSIX ACLs (`chmod +a "everyone deny ..."`) preventing reading, editing, or deleting. Unlocking safely clears ACLs (`chmod -N`) and removes the immutable flag (`chflags nouchg`).
  - **Windows:** ACL permission locking via `cacls`.
- **Encrypt / Decrypt:** Secure files and full folders with AES encryption via Fernet.
- **Folder Support:** Easily encrypt and decrypt both individual files and entire directories.
- **Progress Bar:** Visual indicator for encryption and decryption progress.
- **Matrix Rain Effect:** Hacker-style animated matrix rain background.
- **Ready-to-Use Packages:**
  - **macOS:** Ready-to-use `LockMaster.dmg` and standalone `LockMaster.app` in `dist/`.
  - **Windows:** Ready-to-run `LockMaster.exe` in `dist/`.

---

## Installation & Running

### macOS (DMG & App)

1. Open `dist/LockMaster.dmg`.
2. Drag **LockMaster.app** into your **Applications** folder (or double-click to run directly).
3. (Alternatively) Run `open dist/LockMaster.app` from Terminal.

### Windows (EXE)

1. Go to the `dist` folder.
2. Double-click `LockMaster.exe`.

### Run from Source (macOS & Windows)

1. Create and activate a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate    # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python LockMaster.py
   ```

---

## Building the macOS DMG

To rebuild the macOS `.app` bundle and `.dmg` installer:

```bash
./build_dmg.sh
```
Or with Python:
```bash
python3 build_dmg.py
```

The output `LockMaster.dmg` and `LockMaster.app` will be created inside the `dist/` directory.

---

## Building the Windows EXE

To rebuild the Windows `.exe`:

```bash
pyinstaller --onefile --noconsole --icon=icon.ico LockMaster.py
```

---

## Usage

1. Click **Browse** to select a file or folder.
2. Use **Lock / Unlock** to toggle file system permissions and immutable flags.
3. Use **Encrypt / Decrypt** to encrypt or decrypt the content using AES encryption.

---

## Notes & Key Management

- **Secret Key:** Encryption uses a local `secret.key` file. LockMaster saves and checks keys in `~/.lockmaster/secret.key`, alongside target files, and in the app directory. Keep your key safe to decrypt your data.
- **Sounds:** On macOS, audio alerts use native system chimes (`afplay`), while on Windows it uses `winsound`.

---

## License

Open source for personal and educational use. Made with ❤️ by Navneet Singh.
