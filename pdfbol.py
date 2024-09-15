import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pdfplumber
import PyPDF2
import re
import os


def extract_sicil_no_from_text(text, keyword):
    pattern = rf"{keyword}\s*(\d+)"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def split_pdf_by_sicil_no(pdf_file, keyword, output_folder, progress_var):
    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            current_writer = None
            sicil_no = None
            
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            for page_num in range(total_pages):
                page = pdf.pages[page_num]
                text = page.extract_text()

                new_sicil_no = extract_sicil_no_from_text(text, keyword)
                
                if new_sicil_no:
                    if current_writer:
                        output_filename = os.path.join(output_folder, f"{sicil_no}.pdf")
                        with open(output_filename, "wb") as output_pdf:
                            current_writer.write(output_pdf)
                    
                    current_writer = PyPDF2.PdfWriter()
                    sicil_no = new_sicil_no
                
                if current_writer:
                    current_writer.add_page(pdf_reader.pages[page_num])
                
                # Güncellenmiş ilerleme çubuğu
                progress_var.set((page_num + 1) / total_pages * 100)
                root.update_idletasks()
            
            if current_writer and sicil_no:
                output_filename = os.path.join(output_folder, f"{sicil_no}.pdf")
                with open(output_filename, "wb") as output_pdf:
                    current_writer.write(output_pdf)
                
        messagebox.showinfo("Bilgi", f"PDF dosyaları başarıyla '{output_folder}' klasörüne kaydedildi.")
    
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

def start_split():
    pdf_file = pdf_file_var.get()
    keyword = keyword_var.get()
    if not pdf_file or not keyword:
        messagebox.showwarning("Uyarı", "Lütfen PDF dosyasını seçin ve anahtar kelime girin.")
        return
    
    output_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Bolunmus_PDFler")
    
    # Başlat
    progress_var.set(0)
    split_pdf_by_sicil_no(pdf_file, keyword, output_folder, progress_var)

# GUI
root = tk.Tk()
root.title("PDF Bölme Uygulaması")

tk.Label(root, text="PDF Dosyası:").pack(pady=5)
pdf_file_var = tk.StringVar()
tk.Entry(root, textvariable=pdf_file_var, width=50).pack(pady=5)
tk.Button(root, text="PDF Dosyası Seç", command=lambda: pdf_file_var.set(filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])))\
    .pack(pady=5)

tk.Label(root, text="Anahtar Kelime:").pack(pady=5)
keyword_var = tk.StringVar()
tk.Entry(root, textvariable=keyword_var, width=50).pack(pady=5)

tk.Button(root, text="Başlat", command=start_split).pack(pady=20)

# İlerleme çubuğu
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=10, pady=10)

root.mainloop()

