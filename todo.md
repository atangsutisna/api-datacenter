## Tasks dan Langkah Pengerjaannya

**Upload File**
Langkah-langkah untuk upload file:
- User mengirimkan perintah /upload
- Sistem akan bertanya "Silahkan kirimkan File-nya"
- Atau, alurnya seperti ini:
  1. User upload filenya
  2. Sistem akan menanyakan "Dimana folder mana anda menyimpan file itu?"
  3. User akan mengirimkan nama foldernya. Bila folder itu tidak ada, maka sistem akan membuatnya. Bila folder itu ada, maka akan dimasukan ke dalam folder itu langsung.

**Download File**
Langkah-langkah download file:
1. User akan mengetikan perintah /search
2. Sistem akan menanyakan file apa yang akan di-search
3. User akan mengiriman nama file tersebut
4. Sistem akan menampilkan semua file yang mengandung kata tersebut. Atau, yang sama persis seperti kata tersebut. File yang ditampilkan sudah mengandung link untuk download.

**Summarize File**
1. User mengirimkan perintah /search
2. Sistem akan mencari file yang mendandung kata tersebut. 
3. Sistem akan menampilkan file disertai dengan link download.
4. Selain itu, sistem akan juga akan membuat summarize untuk file tersebut.
5. Sistem akan melakukan File index. Mungkin, proses ini akan dikerjakan di tahap enhancement.

Ini sangat menyenangkan :joy:

## TODO
1. ~~Rename file atau folder~~
2. ~~Hapus file atau folder masih bermasalah~~
3. ~~Upload file~~
4. Paging untuk hasil pencarian. Untuk saat ini, ketika hasil pencarian jumlahnya lebih dari 4096. Belum ada handler untuk error ini. Sehingga, seperti Bug.
5. Ketika melakukan pencarian, kadang sistem suka bilang "Maaf, saya tidak mengerti"
6. Untuk membuat summary file excel, perlu ada perbaikan. Sebelum file dikirimkan ke openai, konversikan terlebih dahulu menjadi PDF. Untuk saat ini, open ai belum support untuk membuat summary file excel.
8. Batasi penggunaan token. Untuk file-file doc atau pdf yang isinya lebih dari 100 halaman, buat duplikasi file sebanyak dua halaman. Tujuannya adalah untuk mempercepat proses summarize. Tujuan dari summarize ini hanya ingin tahu gambaran sekilas tentang sebuah file. Hanya itu.
9. Buat rencana presentasi. Susun tiap pertemua hanya membahas satu fitur. Misal hari jumat bahas tentang upload file.
10. Bug, ketika user punya dua akun. 
Buka salah satu root folder, lalu balik lagi.
Buka salah satu folder, nanti muncul, maaf saya tidak mengerti.
List tidak diupdate ketika buka salah satu root folder
11. ~~Menambahkan account ke nomor handphone (todo)~~
12. Mengurangi account dari nomor handphone

## Bagaimana cara input user?
1. admin menambahkan nomor handphone dan kaitannya dengan account melalui command.
2. sistem akan mencatat handphone dan accounts itu ke dalam file mappinguser.json
3. sistem menunggu user ketika request ke chatbot
4. request datang, sistem akan melakukan verifikasi nomor handphone
5. jika nomor handphone valid, ada di file mappinguser.json, maka sistem akan memindahkannya ke db.json

## Perbaikan dan Testing Sabtu, 6 September 2025
1. Download file. 
Donwload file bermasalah jika ukuran file lebih dari 5 mb.
2. Handle rename file with existing name
3. Handle create a new folder with existing name
4. Check permission before removing action
5. Upload file
User yang seharusnya bisa upload file, tidak bisa upload file. Penyebabnya adalah pathnya tidak lengkap. Yaitu menggunakan simplified path.
6. Check permission before renaming

## TODO
1. Bagaimana menghandle jika rename nggak jadi?
2. Folder root tidak boleh diubah