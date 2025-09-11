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

Rabu 10 September 2025
** urutan folder disusun waktu -> solved: sorted by modification time
** bila upload lebih dari satu file, yang muncul adalah sebanya file itu.
** hapus lebih dari satu
** hapus hapus bermasalah
** zip folder disimpan kemudia didownload


2025-09-10 09:43:47 INFO     userloggedin  - Got user data {'telegram_id': '7272740693', 'fullname': 'Atang', 'accounts': [{'username': 'tatang-publik', 'fullname': 'tatang', 'homedir': '/sdd/Public Internal', 'parentdir': '/var/www/filegator/repository/sdd/Public Internal', 'permissions': 'read|write|upload|download|preview|batchdownload|zip'}, {'username': 'pengajuan', 'fullname': 'pengajuan', 'homedir': '/sdd/Pribadi(1)/Pribadi/Grita/Pengajuan Keuangan', 'parentdir': '/var/www/filegator/repository/sdd/Pribadi(1)/Pribadi/Grita/Pengajuan Keuangan', 'permissions': 'read|upload'}, {'username': 'tes2', 'fullname': 'tes2', 'homedir': '/sdd/tes2', 'parentdir': '/var/www/filegator/repository/sdd/tes2', 'permissions': 'read|upload'}, {'username': 'tes3', 'fullname': 'tes3', 'homedir': '/sdd/tes3', 'parentdir': '/var/www/filegator/repository/sdd/tes3', 'permissions': 'read|upload|download'}, {'username': 'tes', 'fullname': 'tes1', 'homedir': '/sdd/tes1', 'parentdir': '/var/www/filegator/repository/sdd/tes1', 'permissions': 'read|write|upload|download|preview|batchdownload|zip'}], 'phone': '6283821230266', 'version': 3}
2025-09-10 09:43:47 INFO     userloggedin  - Got user with telegram id 7272740693
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
TypeError: expected str, bytes or os.PathLike object, not NoneType
2025-09-10 09:45:03 INFO     actions.pre-rm  - starting to prepare rm action...
2025-09-10 09:45:03 INFO     actions.pre-rm  - attempting to get path on line None
2025-09-10 09:45:03 INFO     userloggedin  - attempting to find user with telegram id 7272740693 on db.json
2025-09-10 09:45:03 INFO     userloggedin  - Got user data {'telegram_id': '7272740693', 'fullname': 'Atang', 'accounts': [{'username': 'tatang-publik', 'fullname': 'tatang', 'homedir': '/sdd/Public Internal', 'parentdir': '/var/www/filegator/repository/sdd/Public Internal', 'permissions': 'read|write|upload|download|preview|batchdownload|zip'}, {'username': 'pengajuan', 'fullname': 'pengajuan', 'homedir': '/sdd/Pribadi(1)/Pribadi/Grita/Pengajuan Keuangan', 'parentdir': '/var/www/filegator/repository/sdd/Pribadi(1)/Pribadi/Grita/Pengajuan Keuangan', 'permissions': 'read|upload'}, {'username': 'tes2', 'fullname': 'tes2', 'homedir': '/sdd/tes2', 'parentdir': '/var/www/filegator/repository/sdd/tes2', 'permissions': 'read|upload'}, {'username': 'tes3', 'fullname': 'tes3', 'homedir': '/sdd/tes3', 'parentdir': '/var/www/filegator/repository/sdd/tes3', 'permissions': 'read|upload|download'}, {'username': 'tes', 'fullname': 'tes1', 'homedir': '/sdd/tes1', 'parentdir': '/var/www/filegator/repository/sdd/tes1', 'permissions': 'read|write|upload|download|preview|batchdownload|zip'}], 'phone': '6283821230266', 'version': 3}
2025-09-10 09:45:03 INFO     userloggedin  - Got user with telegram id 7272740693
2025-09-10 09:45:03 INFO     checkpermissions  - workspace /var/www/filegator/repository/sdd/Public Internal, target path None
2025-09-10 09:45:03 ERROR    rasa_sdk.endpoint  - Exception occurred during execution of request <Request: POST /webhook>
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
TypeError: expected str, bytes or os.PathLike object, not NoneType
** pesan error download harusnya muncul. jangan seperti ini:
> DataCenterBot:
Baik, mungkin ini akan memerlukan waktu beberapa menit untuk menyiapkan file. Mohon ditunggu.

> DataCenterBot:
Maaf, kamu tidak diijinkan untuk mendownload file disini.

> DataCenterBot:
Selesai, silakan cek link di atas
