import tkinter
from tkinter import messagebox
import os, base64

from cryptography import fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def save_and_encrypt():
    title = entry_title.get()
    message = text_secret.get("1.0", "end")
    master_secret = entry_key.get()

    if len(title) == 0 or len(message) == 0 or len(master_secret) == 0:
        messagebox.showerror("Error", "Please enter all fields")
    else:
        # encrypt
        try:
            salt = os.urandom(16)
            key = derive_key(master_secret, salt)
            f = fernet.Fernet(key)
            token = f.encrypt(message.encode())
            salt_64 = base64.b64encode(salt).decode()

            with open("mysecret.txt", "a",
                      encoding="utf-8") as data_file:  # r yazıp read deseydik osyayı bulamaz error verirdi
                data_file.write(f"\n{title}\n::{salt_64}::{token.decode()}\n")
        except FileNotFoundError:
            with open("mysecret.txt", "w") as data_file:
                data_file.write(f"\n{title}\n::{salt_64}::{token.decode()}\n")
        finally:
            entry_title.delete(0, tkinter.END)
            entry_key.delete(0, tkinter.END)
            text_secret.delete("1.0", tkinter.END)


def decrypt():
    title = entry_title.get()
    master_secret = entry_key.get()
    if len(title) == 0 or len(master_secret) == 0:
        messagebox.showerror("Error", "Please enter all fields")
    else:
        # Dosyayı oku ve secret'i bul
        try:
            with open("mysecret.txt", "r", encoding="utf-8") as data_file:
                content = data_file.read()
                lines = content.split('\n')

                # Başlığı bul
                for i, line in enumerate(lines):
                    if line == title:
                        # Bir sonraki satırda salt ve token var
                        if i + 1 < len(lines):
                            data_line = lines[i + 1]
                            if "::" in data_line:
                                parts = data_line.split("::")
                                salt_64 = parts[1]
                                token_str = parts[2]

                                # Decrypt işlemi
                                salt = base64.b64decode(salt_64)
                                key = derive_key(master_secret, salt)
                                f = fernet.Fernet(key)

                                try:
                                    decrypted = f.decrypt(token_str.encode()).decode()
                                    text_secret.delete("1.0", tkinter.END)
                                    text_secret.insert("1.0", decrypted)
                                    messagebox.showinfo("Success", "Decrypted successfully!")
                                    return
                                except:
                                    messagebox.showerror("Error", "Wrong master key!")
                                    return

                messagebox.showerror("Error", "Title not found!")
        except FileNotFoundError:
            messagebox.showerror("Error", "No secrets file found!")


window = tkinter.Tk()
window.geometry("400x600")
window.title("Secret Notes")
window.configure(bg="light blue")

title_label = tkinter.Label(window, text="Secret Notes", bg="light blue", fg="red")
title_label.config(font=("Arial", 15))
title_label.pack()

# ui
try:
    img = tkinter.PhotoImage(file="pic2.png")
    img = img.subsample(6, 6)
    panel = tkinter.Label(window, image=img, bg="light blue")
    panel.image = img
    panel.pack()
except:
    pass

little_title = tkinter.Label(window, text="Enter your title:", bg="light blue", fg="red", font=("Arial", 12))
little_title.place(x=145, y=150)
entry_title = tkinter.Entry(window, width=50, bg="white", fg="red")
entry_title.place(x=50, y=180)
entry_title.focus()

label_secret = tkinter.Label(window, text="Enter your secret:", bg="light blue", fg="red", font=("Arial", 12))
label_secret.place(x=140, y=200)

text_secret = tkinter.Text(window, bg="white", fg="red", width=38, height=12)
text_secret.place(x=50, y=220)

label_key = tkinter.Label(text="Enter your master key:", bg="light blue", fg="red", font=("Arial", 12))
label_key.place(x=130, y=420)

entry_key = tkinter.Entry(window, width=50, bg="white", fg="red")
entry_key.place(x=50, y=450)

save_button = tkinter.Button(text="Save & Encripty", bg="white", fg="red", command=save_and_encrypt)
save_button.place(x=150, y=510)

decrypt_button = tkinter.Button(text="Decrypt", bg="white", fg="red", command=decrypt)
decrypt_button.place(x=170, y=540)

window.mainloop()