import cv2
import mediapipe as mp

# Konfigurasi MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

# Buka kamera
cap = cv2.VideoCapture(0)

# KITA COBA MINTA RESOLUSI TINGGI DULU KE WEBCAM
# Agar saat di-crop ke 800x800 gambarnya tidak pecah (jika webcam mendukung)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

TARGET_SIZE = 800

print(f"Program berjalan. Output {TARGET_SIZE}x{TARGET_SIZE} (Center Crop).")
print("Tekan 'q' untuk keluar.")

while True:
    success, img = cap.read()
    if not success:
        print("Gagal membaca frame kamera.")
        break

    # 1. Mirror kamera
    img = cv2.flip(img, 1)

    # --- LOGIKA RESIZE & CROP ---
    h, w, _ = img.shape
    
    # Hitung skala agar sisi terpendek menjadi 800
    # Jika lebar < tinggi, patokannya lebar. Jika tinggi < lebar, patokannya tinggi.
    if w < h:
        scale = TARGET_SIZE / w
    else:
        scale = TARGET_SIZE / h
        
    new_w = int(w * scale)
    new_h = int(h * scale)
    
    # Resize gambar dengan rasio tetap (tidak gepeng)
    img_resized = cv2.resize(img, (new_w, new_h))
    
    # Hitung titik potong agar tepat di tengah (Center Crop)
    start_x = (new_w - TARGET_SIZE) // 2
    start_y = (new_h - TARGET_SIZE) // 2
    
    # Lakukan pemotongan (Slicing Array)
    img_cropped = img_resized[start_y:start_y+TARGET_SIZE, start_x:start_x+TARGET_SIZE]
    # ----------------------------

    # Proses MediaPipe pada gambar yang SUDAH DI-CROP
    img_rgb = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    # Ambil ukuran gambar crop (pasti 800x800)
    h_final, w_final, c_final = img_cropped.shape 

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                
                # Koordinat relatif terhadap kotak 800x800
                cx, cy = int(lm.x * w_final), int(lm.y * h_final)
                
                # Deteksi Ujung Telunjuk (ID 8)
                if id == 8:
                    cv2.circle(img_cropped, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    cv2.putText(img_cropped, f"X:{cx} Y:{cy}", (cx + 20, cy - 20), 
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            mp_draw.draw_landmarks(img_cropped, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Tampilkan hasil
    cv2.imshow("Hand Tracking 800x800 (Cropped)", img_cropped)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()