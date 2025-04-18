import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os

selected_file = None  # Глобальная переменная для хранения пути к файлу


def remove_metadata(input_path, output_path):
    try:
        img = Image.open(input_path)
        img.save(output_path, format='PNG')
        messagebox.showinfo("Success", "Метаданные успешно удалены и изображение пересохранено!")
    except Exception as e:
        messagebox.showerror("Error", f"Ошибка: {str(e)}")


def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
    if file_path:
        show_image(file_path)


def show_image(file_path):
    global selected_file
    selected_file = file_path
    try:
        img = Image.open(file_path)
        img.thumbnail((300, 300))
        img = ImageTk.PhotoImage(img)
        label.config(image=img)
        label.image = img  # Храним ссылку, чтобы не собирался GC
        path_label.config(text=os.path.basename(file_path))
    except Exception as e:
        messagebox.showerror("Error", f"Не удалось загрузить изображение:\n{str(e)}")


def process_image():
    if selected_file:
        output_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")])
        if output_path:
            remove_metadata(selected_file, output_path)


def drop_event(event):
    files = root.tk.splitlist(event.data)
    for f in files:
        if f.lower().endswith('.png'):
            show_image(f)
            break
        else:
            messagebox.showwarning("Неверный формат", "Поддерживаются только PNG файлы.")


# Создание основного окна с поддержкой DND
root = TkinterDnD.Tk()
root.title("Удаление метаданных PNG")
root.geometry("500x650")

# Метка с изображением
label = tk.Label(root)
label.pack(pady=10)

# Метка пути файла
path_label = tk.Label(root, text="Перетащите PNG сюда или выберите файл", fg="gray")
path_label.pack()

# Виджет зоны drop-а
drop_zone = tk.Label(root, text="⬇ Перетащите PNG файл сюда ⬇", relief="ridge", width=40, height=4, bg="#f0f0f0")
drop_zone.pack(pady=10)
drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind('<<Drop>>', drop_event)

# Кнопки
select_button = tk.Button(root, text="Выбрать PNG", command=select_file)
select_button.pack(pady=5)

process_button = tk.Button(root, text="Удалить метаданные и сохранить", command=process_image)
process_button.pack(pady=5)

root.mainloop()
