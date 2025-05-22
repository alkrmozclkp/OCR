import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import pytesseract
import threading
import time
import cv2

# Tesseract yolu
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Tema ve ana pencere ayarları
current_theme = "Light"
ctk.set_appearance_mode(current_theme)
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("OCR Uygulaması - Görüntüden Metin Tanıma")
root.geometry("1080x720")
root.resizable(False, False)

# Görüntü ön işleme
def preprocess_image(path):
    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return Image.fromarray(thresh)

# Bildirim (toast) mesajı
def show_toast(message, toast_type="info"):
    colors = {
        "info": "#2196F3",
        "success": "#4CAF50",
        "warning": "#FF9800",
        "error": "#F44336"
    }
    color = colors.get(toast_type, "#333")
    toast = ctk.CTkLabel(root, text=message, fg_color=color, text_color="white",
                         font=ctk.CTkFont(size=14, weight="bold"),
                         corner_radius=10, height=35, width=400, anchor="center")
    toast.place(relx=0.5, y=20, anchor="n")
    root.after(2000, toast.destroy)

# Tema değiştirme
def toggle_theme():
    global current_theme
    current_theme = "Dark" if current_theme == "Light" else "Light"
    ctk.set_appearance_mode(current_theme)
    root.after(50, update_button_colors)

# Görsel seçme ve OCR işleme başlatma
def select_image():
    threading.Thread(target=ocr_process).start()

# OCR işlemi
def ocr_process():
    file_path = filedialog.askopenfilename(title="Resim Seç",
                                           filetypes=[("Görsel Dosyaları", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        try:
            progress_bar.set(0.0)
            for i in range(1, 6):
                time.sleep(0.1)
                progress_bar.set(i * 0.2)
            image = preprocess_image(file_path)
            custom_config = r'--oem 3 --psm 3'
            text = pytesseract.image_to_string(image, lang='tur', config=custom_config)
            text_box.delete("0.0", "end")
            text_box.insert("0.0", text)
            progress_bar.set(1.0)
            show_toast("Metin başarıyla tanındı.", "success")
        except Exception:
            show_toast("Bir sorun oluştu. Görsel okunamadı.", "error")
            progress_bar.set(0.0)

# Metni panoya kopyala
def copy_text():
    text = text_box.get("0.0", "end").strip()
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        show_toast("Metin panoya kopyalandı.", "success")
    else:
        show_toast("Kopyalanacak metin yok.", "warning")

# Metni dosyaya kaydet
def save_text():
    text = text_box.get("0.0", "end").strip()
    if not text:
        show_toast("Kaydedilecek metin bulunamadı.", "warning")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")],
                                             title="Kaydet")
    if file_path:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(text)
            show_toast("Metin başarıyla kaydedildi.", "success")
        except Exception:
            show_toast("Dosya kaydedilemedi.", "error")

# Yazı tipi boyutunu değiştir
def change_font_size(size):
    text_box.configure(font=("Consolas", int(size)))

# Metni temizle
def clear_text():
    result = messagebox.askyesno("Temizle", "Tüm metni silmek istediğinizden emin misiniz?")
    if result:
        text_box.delete("0.0", "end")
        show_toast("Metin temizlendi.", "success")

# Tüm metni seç
def select_all_text():
    text_box.tag_add("sel", "1.0", "end")

# Seçili metni sil
def delete_selection():
    try:
        text_box.delete("sel.first", "sel.last")
    except:
        pass

# Arayüz bileşenleri
text_box = ctk.CTkTextbox(root, width=950, height=500, font=("Consolas", 18))
text_box.pack(pady=(30, 10), padx=20)

font_size_menu = ctk.CTkOptionMenu(root, values=["12", "14", "16", "18", "20", "22", "24"],
                                   command=change_font_size, width=100)
font_size_menu.set("18")
font_size_menu.pack()

edit_frame = ctk.CTkFrame(root, fg_color="transparent")
edit_frame.pack(pady=(5, 10))
ctk.CTkButton(edit_frame, text="🧹 Temizle", command=clear_text).pack(side="left", padx=5)
ctk.CTkButton(edit_frame, text="🖊️ Seç", command=select_all_text).pack(side="left", padx=5)
ctk.CTkButton(edit_frame, text="❌ Sil", command=delete_selection).pack(side="left", padx=5)

progress_bar = ctk.CTkProgressBar(root, width=950)
progress_bar.set(0)
progress_bar.pack(pady=(0, 10))

button_frame = ctk.CTkFrame(root, fg_color="transparent")
button_frame.pack(pady=10)

button_width = 180
button_height = 45
corner_radius = 25
font_button = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")

# Butonlar
theme_button = ctk.CTkButton(button_frame, text="🌙 Tema", command=toggle_theme,
                             width=button_width, height=button_height,
                             corner_radius=corner_radius, font=font_button)
theme_button.pack(side="left", padx=10)

select_button = ctk.CTkButton(button_frame, text="📷 Görsel Seç", command=select_image,
                              width=button_width, height=button_height,
                              corner_radius=corner_radius, font=font_button)
select_button.pack(side="left", padx=10)

copy_button = ctk.CTkButton(button_frame, text="📋 Kopyala", command=copy_text,
                            width=button_width, height=button_height,
                            corner_radius=corner_radius, font=font_button)
copy_button.pack(side="left", padx=10)

save_button = ctk.CTkButton(button_frame, text="💾 Kaydet", command=save_text,
                            width=button_width, height=button_height,
                            corner_radius=corner_radius, font=font_button)
save_button.pack(side="left", padx=10)

# Tema rengine göre renk ayarları
def update_button_colors():
    if current_theme == "Dark":
        theme_button.configure(fg_color="#4f4f4f", hover_color="#333333", border_color="#4f4f4f")
        select_button.configure(fg_color="#388e3c", hover_color="#1b5e20", border_color="#388e3c")
        copy_button.configure(fg_color="#1976d2", hover_color="#0d47a1", border_color="#1976d2")
        save_button.configure(fg_color="#f57c00", hover_color="#e65100", border_color="#f57c00")
        text_box.configure(text_color="white", border_color="#333333", bg_color="#212121")
    else:
        theme_button.configure(fg_color="#9e9e9e", hover_color="#757575", border_color="#9e9e9e")
        select_button.configure(fg_color="#4CAF50", hover_color="#45a049", border_color="#4CAF50")
        copy_button.configure(fg_color="#2196F3", hover_color="#1976D2", border_color="#2196F3")
        save_button.configure(fg_color="#FF9800", hover_color="#fb8c00", border_color="#FF9800")
        text_box.configure(text_color="black", border_color="#d0d0d0", bg_color="white")

update_button_colors()
root.mainloop()
