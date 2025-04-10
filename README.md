# Flexym
Flexym is a real-time AI application for tracking exercise repetitions and posture correction, using MediaPipe and OpenCV to analyze body movements via webcam. It supports four exercises and provides interactive feedback. Developed as a university project at BINUS, Flexym ensures a safe and engaging workout experience.

## Features
1. Real-Time Repetition Counting
Accurately tracks repetitions for four exercises: pushup, squat, sit-up, and bicep curl.

2. Dynamic Posture Feedback
Provides alerts and corrective advice during incorrect movements, ensuring safe and effective exercise.

3. Customizable Feedback Intervals
Prompts the user for input (e.g., "Continue or finish?") after completing specific repetition intervals (e.g., 12 reps).

4. Webcam Integration
Works directly with a laptop/PC camera for live tracking.

5. Interactive GUI
Displays live video feed with annotations, posture feedback, and repetition count.

## Libraries Used
Python: Core application logic.

OpenCV & MediaPipe: Real-time video processing and movement analysis.

NumPy: Angle calculations for posture correction.

## Installation Steps

1. **Clone the repository**  
   ```sh
   git clone https://github.com/SonnWT/Flexym.git
   cd Flexym
2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
3. **Run the application**
   ```sh
   python Flexym.py
