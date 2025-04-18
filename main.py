import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os

selected_files = []
thumbnails = []

CARD_WIDTH = 300
CARD_HEIGHT = 350
IMG_SIZE = (200, 200)
COLUMNS_MIN_WIDTH = 120  # Минимальная ширина на одну карточку


def is_png_file(path):
    return path.lower().endswith('.png')


def collect_png_files(paths):
    pngs = []
    for path in paths:
        if os.path.isdir(path):
            for fname in os.listdir(path):
                fpath = os.path.join(path, fname)
                if os.path.isfile(fpath) and is_png_file(fpath):
                    pngs.append(fpath)
        elif os.path.isfile(path) and is_png_file(path):
            pngs.append(path)
    return pngs


def remove_metadata_batch(files, output_dir):
    prefix = prefix_entry.get() if prefix_var.get() else ''
    suffix = suffix_entry.get() if suffix_var.get() else ''
    errors = []

    for file_path in files:
        try:
            filename = os.path.basename(file_path)
            name, ext = os.path.splitext(filename)
            new_name = f"{prefix}{name}{suffix}.png"
            out_path = os.path.join(output_dir, new_name)

            img = Image.open(file_path)
            img.save(out_path, format='PNG')
        except Exception as e:
            errors.append(f"{file_path}: {str(e)}")

    if errors:
        messagebox.showerror("Ошибки", "\n".join(errors))
    else:
        messagebox.showinfo("Готово", "Все изображения пересохранены без метаданных!")


def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
    if file_paths:
        append_to_file_list(file_paths)


def process_images():
    if not selected_files:
        messagebox.showwarning("Нет файлов", "Сначала выберите PNG-файлы.")
        return

    output_dir = filedialog.askdirectory()
    if output_dir:
        remove_metadata_batch(selected_files, output_dir)


def drop_event(event):
    raw_data = root.tk.splitlist(event.data)
    pngs = collect_png_files(raw_data)
    if pngs:
        append_to_file_list(pngs)
    else:
        messagebox.showwarning("Нет PNG", "Не найдено подходящих PNG файлов.")


def append_to_file_list(files):
    global selected_files
    added = 0
    for f in files:
        if f not in selected_files:
            selected_files.append(f)
            added += 1
    update_preview()
    if added == 0:
        messagebox.showinfo("Инфо", "Новые файлы не добавлены — они уже есть в списке.")


def clear_file_list():
    global selected_files
    selected_files = []
    update_preview()


def update_preview():
    for widget in preview_frame.winfo_children():
        widget.destroy()
    thumbnails.clear()

    count_label.config(text=f"Выбрано файлов: {len(selected_files)}")

    if not selected_files:
        return

    canvas_width = preview_canvas.winfo_width()
    if canvas_width == 1:
        canvas_width = root.winfo_width()

    columns = max(1, canvas_width // COLUMNS_MIN_WIDTH)

    for idx, f in enumerate(selected_files):
        try:
            img = Image.open(f).resize(IMG_SIZE)
            tk_img = ImageTk.PhotoImage(img)
            thumbnails.append(tk_img)

            frame = tk.Frame(preview_frame, width=CARD_WIDTH, height=CARD_HEIGHT, bd=1, relief="groove")
            frame.grid_propagate(False)

            label = tk.Label(frame, image=tk_img)
            label.pack()

            caption = tk.Label(frame, text=os.path.basename(f), wraplength=90, font=("Segoe UI", 8))
            caption.pack(pady=(2, 0))

            row = idx // columns
            col = idx % columns
            frame.grid(row=row, column=col, padx=5, pady=5)
        except:
            continue

    preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))


def on_resize(event):
    update_preview()


# ────────── UI ──────────

root = TkinterDnD.Tk()
root.title("Batch PNG Metadata Remover")
root.geometry("800x700")
root.minsize(400, 500)
root.configure(bg="#f4f4f4")

style_font = ("Segoe UI", 10)

# Верх: превью
preview_wrapper = tk.LabelFrame(root, text="Превью загруженных файлов", font=style_font, bg="#f4f4f4")
preview_wrapper.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

preview_canvas = tk.Canvas(preview_wrapper, bg="#ffffff")
preview_canvas.drop_target_register(DND_FILES)
preview_canvas.dnd_bind('<<Drop>>', drop_event)
v_scroll = tk.Scrollbar(preview_wrapper, orient=tk.VERTICAL, command=preview_canvas.yview)
preview_canvas.configure(yscrollcommand=v_scroll.set)

v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

preview_frame = tk.Frame(preview_canvas, bg="#ffffff")
canvas_window = preview_canvas.create_window((0, 0), window=preview_frame, anchor="nw")

preview_frame.bind("<Configure>", lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all")))
preview_canvas.bind("<Configure>", on_resize)

# Зона дропа
drop_zone = tk.Label(root, text="⬇ Перетащите PNG файлы или папки сюда ⬇",
                     relief="groove", font=("Segoe UI", 11, "bold"),
                     height=4, bg="#e0f7fa", fg="#006064")
drop_zone.pack(padx=10, pady=10, fill=tk.BOTH)
drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind('<<Drop>>', drop_event)

# Кнопки
btn_frame = tk.Frame(root, bg="#f4f4f4")
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Добавить файлы", width=20, command=select_files).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Сбросить выбор", width=20, command=clear_file_list).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Сохранить без метаданных", width=30, command=process_images).grid(row=0, column=2, padx=5)

count_label = tk.Label(root, text="Выбрано файлов: 0", font=("Segoe UI", 9), bg="#f4f4f4")
count_label.pack(pady=3)

# Префикс/суффикс
mod_frame = tk.LabelFrame(root, text="Настройки имени выходных файлов", font=style_font, bg="#f4f4f4")
mod_frame.pack(fill=tk.X, padx=10, pady=10)

prefix_var = tk.BooleanVar()
suffix_var = tk.BooleanVar()

tk.Checkbutton(mod_frame, text="Префикс", variable=prefix_var, bg="#f4f4f4").grid(row=0, column=0, sticky="w", padx=5)
prefix_entry = tk.Entry(mod_frame, width=20)
prefix_entry.grid(row=0, column=1, padx=5)

tk.Checkbutton(mod_frame, text="Суффикс", variable=suffix_var, bg="#f4f4f4").grid(row=0, column=2, sticky="w", padx=5)
suffix_entry = tk.Entry(mod_frame, width=20)
suffix_entry.grid(row=0, column=3, padx=5)

root.mainloop()
