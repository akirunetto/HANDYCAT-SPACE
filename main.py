import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

print("Kamera Mirror aktif. Tekan 'q' untuk keluar.")

while True:
    success, img = cap.read()
    if not success:
        print("Gagal membaca frame kamera.")
        break

    # --- BAGIAN BARU: MIRROR KAMERA ---
    # Angka 1 artinya flip horizontal. (0 = vertikal, -1 = keduanya)
    img = cv2.flip(img, 1) 
    # ----------------------------------

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    h, w, c = img.shape

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                
                # Deteksi Ujung Telunjuk (ID 8)
                if id == 8:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    # Koordinat sekarang mengikuti pandangan cermin
                    cv2.putText(img, f"X:{cx} Y:{cy}", (cx + 20, cy - 20), 
                                cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Deteksi Tangan (Mirror)", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()