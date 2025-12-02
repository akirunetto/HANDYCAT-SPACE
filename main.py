import cv2
import mediapipe as mp

# 1. Inisialisasi MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,           # Maksimal mendeteksi 2 tangan
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# 2. Buka Webcam (0 biasanya adalah ID webcam default)
cap = cv2.VideoCapture(0)

print("Tekan 'q' untuk keluar dari program.")

while True:
    success, img = cap.read()
    if not success:
        print("Gagal membaca frame kamera.")
        break

    # MediaPipe membutuhkan input gambar dalam format RGB, sedangkan OpenCV menggunakan BGR
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Proses deteksi tangan
    results = hands.process(img_rgb)

    # Dapatkan dimensi gambar (tinggi dan lebar) untuk konversi koordinat
    h, w, c = img.shape

    # Jika tangan terdeteksi
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            # Loop untuk setiap titik (landmark) pada tangan
            for id, lm in enumerate(hand_landmarks.landmark):
                # Konversi koordinat normalisasi (0.0 - 1.0) ke piksel
                cx, cy = int(lm.x * w), int(lm.y * h)
                
                # --- CONTOH: Menampilkan koordinat Ujung Telunjuk (ID 8) ---
                if id == 8:
                    # Gambar lingkaran di ujung telunjuk
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    # Tulis teks koordinat di layar
                    cv2.putText(img, f"X:{cx} Y:{cy}", (cx + 20, cy - 20), 
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                    
                    # Print ke terminal juga (opsional)
                    # print(f"ID: {id}, X: {cx}, Y: {cy}")

            # Gambar garis-garis koneksi tangan (kerangka)
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Tampilkan hasil di window
    cv2.imshow("Deteksi Tangan & Koordinat", img)

    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan resources
cap.release()
cv2.destroyAllWindows()