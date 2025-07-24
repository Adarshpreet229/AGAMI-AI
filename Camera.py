import cv2
import os
import time
from datetime import datetime
import google.generativeai as genai
import pyttsx3
import base64

# Configure Google Generative AI
genai.configure(api_key="AIzaSyBZtv08pXgLuElc_qy1YRnP0A75ZY9Wz_4")  # Replace with your API key
model = genai.GenerativeModel("gemini-1.5-flash")

# Text-to-Speech Functionality
def speak(audio, speed=200):
    engine = pyttsx3.init()
    engine.setProperty('rate', speed)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Use default Windows voice
    engine.say(audio)
    engine.runAndWait()

def save_to_downloads(frame):
    downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"captured_image_{timestamp}.jpg"
    save_path = os.path.join(downloads_path, filename)
    cv2.imwrite(save_path, frame)
    return save_path

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def capture_and_analyze(mode="default"):
    # Initialize the webcam (0 is usually the default webcam)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        speak("I couldn’t open the webcam. Please check if it’s connected.")
        return

    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        speak("I couldn’t capture the frame. Please try again.")
        cap.release()
        return

    # Save the frame to Downloads
    saved_path = save_to_downloads(frame)
    print(f"Image saved to: {saved_path}")

    # Analyze the image using Google Generative AI based on mode
    try:
        base64_image = encode_image_to_base64(saved_path)
        
        # Define the prompt based on the mode
        if mode == "emotion":
            prompt = "Analyze the image and describe the emotion on the person’s face in a natural, concise way, like you’re telling someone what the person seems to be feeling."
            speak_prefix = ""
        elif mode == "hands":
            prompt = "Interpret any hand signs or gestures in the image and form a complete sentence based on what they might be communicating. If no clear signs are present, say so."
            speak_prefix = ""
        else:  # default mode
            prompt = "Describe what’s in this image in a natural, concise way, as if you’re telling someone what you see in front of a camera."
            speak_prefix = ""

        # Send the prompt and image to the model
        response = model.generate_content([
            prompt,
            {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
        ])
        result = response.text.strip()
        print(f"AI Result: {result}")
        speak(f"{speak_prefix}{result}")
    except Exception as e:
        print(f"Error analyzing the image with AI: {e}")
        speak("I encountered an issue analyzing the image. Please try again.")

    # Release the webcam
    cap.release()

# Main interaction (run once and exit)
print("Say 'camera' to describe the view, 'emotion' to detect a person’s emotion, or 'hands' to interpret hand signs. The program will exit after analysis.")
user_input = input("> ").lower()

if user_input == "camera":
    capture_and_analyze(mode="default")
elif user_input == "emotion":
    capture_and_analyze(mode="emotion")
elif user_input == "hands":
    capture_and_analyze(mode="hands")
else:
    print("I didn’t understand that. Please say 'camera', 'emotion', or 'hands' to proceed.")