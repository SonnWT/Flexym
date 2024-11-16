import cv2
import mediapipe as mp
import numpy as np
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Konstanta
MIN_REP_ANGLE = {'pushup': 90, 'squat': 90, 'situp': 90, 'bicepcurl': 50}
MAX_REP_ANGLE = {'pushup': 160, 'squat': 160, 'situp': 140, 'bicepcurl': 70}
MIN_TIME_BETWEEN_REPS = 1.5  # Minimal waktu antar repetisi dalam detik
target_reps_interval = 12  # Interval untuk bertanya ke user setelah 12 repetisi

# Fungsi untuk menghitung sudut antar tiga titik
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle
    return angle

# Fungsi untuk menghitung repetisi dan memberikan umpan balik postur
def count_reps_and_correct_posture(landmarks, exercise, stage):
    feedback = ""
    correct_posture = True

    # Tentukan titik-titik utama berdasarkan jenis latihan
    if exercise == 'pushup' or exercise == 'bicepcurl':
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        angle = calculate_angle(shoulder, elbow, wrist)

    elif exercise == 'squat':
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                 landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
        angle = calculate_angle(hip, knee, ankle)

    elif exercise == 'situp':
        hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
               landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
        shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
        angle = calculate_angle(shoulder, hip, knee)

    # Tentukan tahap gerakan (up/down) dan beri umpan balik
    if angle > MAX_REP_ANGLE[exercise]:
        stage = 'up'
    if angle < MIN_REP_ANGLE[exercise] and stage == 'up':
        stage = 'down'
        return stage, 1, correct_posture, feedback

    # Umpan balik postur dan koreksi
    if angle < MIN_REP_ANGLE[exercise]:
        feedback = "Gerakan tidak cukup dalam."
        correct_posture = False
    elif angle > MAX_REP_ANGLE[exercise]:
        feedback = "Pastikan tidak terlalu lurus saat di posisi atas."
        correct_posture = False

    return stage, 0, correct_posture, feedback

# Tampilkan panduan penggunaan kamera untuk latihan yang dipilih
def display_exercise_guidelines(image, exercise):
    guidelines = {
        'pushup': "Kamera sejajar dengan siku dan bahu.",
        'squat': "Kamera sejajar dengan pinggul dan lutut.",
        'situp': "Kamera fokus pada pinggang dan bahu.",
        'bicepcurl': "Kamera di depan atau samping, fokus pada siku dan bahu."
    }

    guideline_text = guidelines.get(exercise, "Panduan tidak tersedia.")
    cv2.putText(image, guideline_text, (10, 450),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

# Fungsi utama untuk menangkap video dari kamera
def process_with_camera(exercise):  
    cap = cv2.VideoCapture(0)
    stage = None
    reps = 0
    last_rep_time = time.time()
    input_given = False  # Variabel untuk mengecek apakah input 'y' sudah diberikan

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = pose.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                stage, rep_increment, correct_posture, feedback = count_reps_and_correct_posture(landmarks, exercise, stage)

                # Update repetisi dan beri feedback postur
                if rep_increment == 1:
                    current_time = time.time()
                    if current_time - last_rep_time < MIN_TIME_BETWEEN_REPS:
                        feedback = "Gerakan terlalu cepat, perlambat!"
                        correct_posture = False
                    else:
                        last_rep_time = current_time
                        reps += rep_increment
                        if(reps % 12 == 1): 
                            input_given = False

                # Gambar landmark pada frame
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Tampilkan repetisi dan feedback
                cv2.putText(image, f'Reps: {reps}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 1, cv2.LINE_AA)

                if not correct_posture:
                    cv2.putText(image, f'Posture Alert: {feedback}', (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)

                display_exercise_guidelines(image, exercise)

                # Cek jika repetisi sudah mencapai kelipatan target (misalnya setiap 12 repetisi)
                if reps > 0 and reps % target_reps_interval == 0:
                    if not input_given:  # Jika input belum diberikan, tanyakan pada user
                        cv2.putText(image, 'Complete 12 reps! Continue or finish? (y/n)', (10, 400),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 1, cv2.LINE_AA)

                        cv2.imshow('Workout Counter', image)
                        
                        # Set default to continue workout
                        continue_workout = True
                        start_time = time.time()

                        # Buat input non-blocking dengan waktu tunggu minimal
                        while time.time() - start_time < 5:
                            key = cv2.waitKey(1) & 0xFF
                            if key == ord('y'):
                                input_given = True  # Menandakan input 'y' sudah diberikan
                                globals()[target_reps_interval] = target_reps_interval + 12
                                break  # Lanjutkan workout
                            elif key == ord('n'):
                                continue_workout = False
                                break

                        if not continue_workout:
                            cap.release()
                            cv2.destroyAllWindows()
                            print(f"Total repetisi: {reps}")
                            return
                    else:
                        cv2.putText(image, f'Continuing... Reps: {reps}', (10, 400),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            # Tampilkan video hasil
            cv2.imshow('Workout Counter', image)

            # Tekan 'q' untuk keluar
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Total repetisi: {reps}")

if __name__ == "__main__":
    exercise = 'bicepcurl'  # Ubah sesuai jenis latihan: 'pushup', 'squat', 'situp', 'bicepcurl'
    process_with_camera(exercise)