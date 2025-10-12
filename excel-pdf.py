from spire.xls import *
from spire.xls.common import *
import os

def export_to_pdf(input_excel_path, sheet_index=0):
    """
    Mengkonversi sheet tertentu dari file Excel ke PDF dan menyimpannya 
    di folder yang sama dengan file sumber.
    """
    workbook = None
    try:
        # --- Modifikasi untuk menentukan Output Path ---
        # 1. Mendapatkan path direktori dan nama file tanpa ekstensi
        direktori_path = os.path.dirname(input_excel_path)
        nama_file_tanpa_ext = os.path.splitext(os.path.basename(input_excel_path))[0]
        
        # 2. Membuat nama file PDF baru
        output_pdf_filename = f"{nama_file_tanpa_ext}_Sheet_{sheet_index + 1}.pdf"
        output_pdf_path = os.path.join(direktori_path, output_pdf_filename)
        # -----------------------------------------------

        # 3. Membuat objek Workbook dan memuat file Excel
        workbook = Workbook()
        workbook.LoadFromFile(input_excel_path)

        # Cek apakah indeks sheet valid
        if sheet_index < len(workbook.Worksheets):
            sheet = workbook.Worksheets[sheet_index]
        else:
            print(f"❌ Error: Indeks sheet {sheet_index} tidak valid.")
            return

        # Solusi Masalah Sheet Tersembunyi (Visibility)
        if sheet.Visibility != WorksheetVisibility.Visible:
             sheet.Visibility = WorksheetVisibility.Visible

        # Opsional: Mengatur agar sheet muat ke halaman PDF
        workbook.ConverterSetting.SheetFitToPage = True

        # 4. Mengkonversi sheet ke PDF dan menyimpan di path yang ditentukan
        sheet.SaveToPdf(output_pdf_path)

        print(f"✅ Berhasil mengkonversi sheet ke-{sheet_index + 1} ('{sheet.Name}')")
        print(f"   Disimpan di: {output_pdf_path}")
        return output_pdf_path
    except Exception as e:
        print(f"❌ Terjadi kesalahan saat konversi: {e}")
        
    finally:
        # Membuang sumber daya
        if workbook is not None:
             workbook.Dispose()

# --- Penggunaan ---
excel_file = "/home/kangatang/git/filegator/repository/atang/file_example_XLS_5000.xls"
indeks_sheet = 0 # <-- Angka 0 selalu merujuk pada sheet pertama
# Memanggil fungsi konversi
export_to_pdf(excel_file, indeks_sheet)