# Hand-Controlled Terminal Shooter: Bullet Hell Edition

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Pygame](https://img.shields.io/badge/Library-Pygame-green)
![MediaPipe](https://img.shields.io/badge/AI-MediaPipe-orange)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV-red)

**Terminal Shooter** adalah sebuah implementasi teknis yang menggabungkan pengembangan permainan arkade (*arcade game*) klasik dengan teknologi *Computer Vision*. Proyek ini mendemonstrasikan integrasi *real-time* antara pemrosesan citra digital dan logika permainan interaktif.

Pengguna mengendalikan pesawat dalam permainan menggunakan deteksi gerakan tangan (*hand tracking*) melalui webcam, menghilangkan kebutuhan akan perangkat input konvensional seperti *keyboard* atau *mouse*.

## Fitur Utama

* **Computer Vision Control:** Mengimplementasikan Google MediaPipe untuk pelacakan koordinat tangan (Landmark Tracking) secara *real-time* guna mengontrol pergerakan entitas pemain.
* **Gesture Recognition:** Sistem deteksi gestur otomatis yang membedakan antara tangan mengepal (navigasi) dan tangan terbuka (pemicu mekanisme serangan area/bom).
* **Estetika Retro-Futuristik:** Menggunakan grafis berbasis karakter ASCII dengan efek visual neon dan simulasi CRT (*Cathode Ray Tube*) untuk menciptakan atmosfer visual yang konsisten.
* **Sistem Gameplay Adaptif:** Mencakup 10 tingkatan level dengan Boss yang memiliki pola serangan algoritmik unik.
* **Augmented Reality Overlay:** Menampilkan umpan kamera (*camera feed*) yang telah diproses sebagai lapisan latar belakang transparan, memberikan efek antarmuka holografik.

## Prasyarat Sistem

Sebelum menjalankan aplikasi, pastikan sistem Anda memiliki lingkungan Python yang terinstal beserta dependensi berikut:

* **Python 3.8+**
* **OpenCV** (Pemrosesan Citra)
* **MediaPipe** (Deteksi Tangan)
* **Pygame** (Mesin Permainan)
* **NumPy** (Komputasi Numerik)

## Instalasi

Ikuti langkah-langkah berikut untuk mengatur proyek di lingkungan lokal Anda:

1.  **Kloning Repositori**
    ```bash
    git clone [https://github.com/username-anda/hand-controlled-shooter.git](https://github.com/username-anda/hand-controlled-shooter.git)
    cd hand-controlled-shooter
    ```

2.  **Instalasi Dependensi**
    Gunakan `pip` untuk menginstal pustaka yang diperlukan:
    ```bash
    pip install pygame opencv-python mediapipe numpy
    ```

3.  **Menjalankan Aplikasi**
    Eksekusi skrip utama menggunakan Python:
    ```bash
    python hand_controlled_shooter.py
    ```

## Panduan Kontrol

Aplikasi ini menggunakan input visual dari webcam. Pastikan pencahayaan ruangan memadai dan posisi tangan terlihat jelas oleh kamera.

| Aksi | Gestur Tangan | Input Alternatif (Keyboard) |
| :--- | :--- | :--- |
| **Navigasi / Bergerak** | **Tangan Mengepal (Fist)** <br>Gerakkan kepalan tangan untuk mengarahkan pesawat. | Tombol Panah (Arrow Keys) |
| **Menembak** | **Otomatis** <br>Pesawat menembak secara berkelanjutan. | Otomatis |
| **Serangan Area (Bom)** | **Telapak Terbuka (Open Palm)** <br>Memicu ledakan area (memerlukan item Bom). | Tombol `B` |
| **Jeda (Pause)** | - | Tombol `ESC` |

## Struktur Teknis

Proyek ini mengintegrasikan dua loop utama dalam satu proses eksekusi:

1.  **Vision Loop (OpenCV & MediaPipe):**
    * Mengakuisisi frame dari webcam.
    * Melakukan pra-pemrosesan (resize, crop, dan flip).
    * Mengekstraksi landmark tangan (21 titik koordinat).
    * Mengonversi status jari menjadi sinyal kontrol logika.

2.  **Game Loop (Pygame):**
    * Menerima koordinat ternormalisasi dari modul Vision.
    * Memperbarui status entitas permainan (posisi pemain, musuh, proyektil).
    * Menangani deteksi tabrakan (*collision detection*) dan rendering grafis.

## Pengembangan Masa Depan

Berikut adalah rencana pengembangan untuk meningkatkan fungsionalitas proyek:

* Implementasi mode multipemain lokal menggunakan deteksi dua tangan.
* Variasi senjata berdasarkan gestur jari yang berbeda.
* Optimasi penggunaan sumber daya CPU/GPU untuk perangkat berspesifikasi rendah.

## Kontribusi

Kontribusi terhadap proyek ini sangat dihargai. Silakan buat *Pull Request* untuk perbaikan bug atau penambahan fitur. Untuk perubahan substansial, harap membuka *Issue* terlebih dahulu untuk diskusi.
