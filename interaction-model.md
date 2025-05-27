# Model Interaksi

#### Minta Data
Pada model ini, user belum tahu persis apa yang mereka inginkan. Mereka hanya ingin melihat-lihat data yang ada.

Biasanya, bila mereka tidak menemukan data yang dimaksud maka meminta bantuan chatbot untuk mencarikannya.

**Contoh**
User: Minta data dong
Bot : Baik, ini folder dan file yang kamu punya
- Folder A
- Folder B
- Foler C
- file_excel.xls
- file_prensetasi.ppt
- file_catatan.docs

#### User ingin tahu ada data apa saja
Di sini user, hanya ingin tahu data yang mereka miliki.
**Response Bot**: 
1. Menampilkan semua folder yang ada di home directory. Kondisi ini hanya berlaku untuk user yang hanya punya satu akse folder atau home directory.
2. Menampilan folder utama saja. Misal, suatu user punya dua home directory: `Program Spark` dan `Public Internal`. Maka, data yang ditampilkan hanyalah dua folder tersebut.

**Contoh Pertanyaan**
- tampilkan semua data saya
- saya punya data apa saja?
- minta daftar data saya dong
- bisa tunjukan semua file dan folder saya?
- apa saja isi penyimpanan saya?
- perlihatkan semua data yang saya miliki
- tolong list data-data saya
- ada file dan folder apa saja di sini
- tampilkan ada data apa saja
- tolong tampilkan data saya
- ada file apa saja?
- tolong tampilkan semua filenya
- apa saja filenya?
- datanya apa saja?

**Contoh Respon**
Baik, ini semua data yang Anda miliki:
1. Folder 1
2. Folder 2
3. Folder 3
4. Folder 4
5. file_video.avi
6. file_peterpan.mp3
7. file_perhitungan_anggaran.xls
Anda sedang mencari apa dari daftar ini?

#### Mencari Data