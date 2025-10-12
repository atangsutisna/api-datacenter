# Chatbot Commands

Untuk menambah pengguna baru dengan hp baru, gunakan perintah ini:
```
/reguser
```

Untuk menambah account pada user, gunakan perintah ini;
```
/addaccount
```
Setiap nomor HP, minimal satu account. Perintah ini untuk menambahkan account ke nomor Hp.

```
/rmaccount
```
Perintah ini untuk menghapus account dari nomor HP

```
/upload
```

### Perintah ini untuk menginstruksikan chatbot untuk menerima file upload

Untuk menjalankan proses yang perlu waktu lama, service ini menggunakan redis dan Celery.

```
celery -A tasks worker --loglevel=INFO
atau
nohup celery -A celery_app worker --loglevel=INFO > celery-tasks.log &
```
Menjalankan redis-server
```
sudo systemctl status redis-server
```
Cek service redis-server
```
redis-cli ping
```
Sebagai contoh, jalankan trigger_task.py. Task yang dijalankan, ada di file tasks.py