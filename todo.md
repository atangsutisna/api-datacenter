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
1. ~~Download file.~~ 
Donwload file bermasalah jika ukuran file lebih dari 5 mb.
2. ~~Handle rename file with existing name~~
3. ~~Handle create a new folder with existing name~~
4. ~~Check permission before removing action~~
5. ~~Upload file~~
User yang seharusnya bisa upload file, tidak bisa upload file. Penyebabnya adalah pathnya tidak lengkap. Yaitu menggunakan simplified path.
6. ~~Check permission before renaming~~

## TODO
1. Bagaimana menghandle jika rename nggak jadi?
2. Folder root tidak boleh diubah

## BUG Rabu 10 September 2025
1. ~~Urutan folder disusun waktu. saat ini, disusun berdasarkan update terbaru.~~
2. ~~Bila upload lebih dari satu file, maka pesan yang muncul adalah sebanyak file itu. Jika file upload sebanyak 3, maka pesannya akan sebanyak 3.~~
Solusi: setelah file diupload, chatbot tidak langsung balas. Setelah kirim /selesai, bot akan membuat summary.
3. Hapus lebih dari satu
4. ~~Hapus bermasalah~~
5. Zip folder disimpan kemudia didownload
6. ~~Pesan error yang kurang tepat ketika tidak punya akses untuk download.~~
~~Saat ini, pesan yang tampil adalah seperti ini:~~
> DataCenterBot:
Baik, mungkin ini akan memerlukan waktu beberapa menit untuk menyiapkan file. Mohon ditunggu.

> DataCenterBot:
Maaf, kamu tidak diijinkan untuk mendownload file disini.

> DataCenterBot:
Selesai, silakan cek link di atas

#### How to reproduce bug remove (no 4)
1. buat folder baru
2. buka folder itu dengan perinta "buka folder 4"
3. lakukan upload ke dalam folder itu
4. tampilkan
5. hapus --> di sini sudah bermasalah. Bot masih ingat nomor 4
6. tampilakan
7. hapus --> di sini sudah bermasalah. bot sudah tidak bisa mengenali intent menghapus

Maka, akan muncul error seperti ini:
``
2025-09-10 09:43:47 INFO     checkpermissions  - workspace /var/www/filegator/repository/sdd/Public Internal, target path None
2025-09-10 09:43:47 ERROR    rasa_sdk.endpoint  - Exception occurred during execution of request <Request: POST /webhook>
Traceback (most recent call last):
  File "handle_request", line 83, in handle_request
    )
  File "/home/datacenter/git/api-datacenter/.venv/lib/python3.10/site-packages/rasa_sdk/endpoint.py", line 113, in webhook
    result = await executor.run(action_call)
  File "/home/datacenter/git/api-datacenter/.venv/lib/python3.10/site-packages/rasa_sdk/executor.py", line 399, in run
    action(dispatcher, tracker, domain)
  File "/home/datacenter/git/api-datacenter/actions/pre-rm.py", line 38, in run
    has_permission = self.is_permitted(telegram_id, selected_path, "write")
  File "/home/datacenter/git/api-datacenter/checkpermissions.py", line 30, in is_permitted
    if is_child(workspace, target_path) or workspace == target_path:
  File "/home/datacenter/git/api-datacenter/checkpermissions.py", line 18, in is_child
    Path(child).resolve().relative_to(Path(parent).resolve())
  File "/usr/lib/python3.10/pathlib.py", line 960, in __new__
    self = cls._from_parts(args)
  File "/usr/lib/python3.10/pathlib.py", line 594, in _from_parts
    drv, root, parts = self._parse_args(args)
  File "/usr/lib/python3.10/pathlib.py", line 578, in _parse_args
    a = os.fspath(a)
TypeError: expected str, bytes or os.PathLike object, not NoneType``


### Rabu, 17 September
** ~~susun berdasarkan abjad~~
** tambahkan pesan untuk user jika harus menunggu lama. dan hitung berapa lama. 
** waktu yang diperlukan untuk zip. isi data maksimal. batas maksimal download.
** transisi bila percakapan ke hal lain.

### Sabtu, 15 November 2025
1. Command download tidak mengirimkan link download. Ketika command download untuk file, response tidak ada masalah. Namun, ketika yang diminta adalah folder, maka yang muncul hanya teks tanpa link download.