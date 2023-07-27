import cv2
import numpy as np
import pyautogui
import pytesseract
from tkinter import Tk, Button
from pynput import mouse, keyboard
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

pytesseract.pytesseract.tesseract_cmd = r'F:\T\tesseract.exe'

# Load the dictionary from the pickle file
with open("statements_dict.pkl", "rb") as file:
    all_statements = pickle.load(file)

# Convert the dictionary keys to a list, this is our list of predefined options
options = list(all_statements.keys())

# Global variable to store the coordinates of the area to capture
capture_area = []

# Function to be called when the mouse button is pressed
def on_click(x, y, button, pressed):
    if pressed:
        # Button pressed: start of the capture area
        capture_area.append((x, y))
    else:
        # Button released: end of the capture area
        capture_area.append((x, y))

        # Stop the listener
        mouse_listener.stop()

# Create a mouse listener
mouse_listener = mouse.Listener(on_click=on_click)

# Function to start the capture
def start_capture():
    # Clear the previous capture area
    capture_area.clear()

    # Start the mouse listener
    mouse_listener.start()

# Function to perform OCR
def ocr():
    global capture_area

    # Calculate width and height of the region
    x1, y1 = capture_area[0]
    x2, y2 = capture_area[1]
    width = x2 - x1
    height = y2 - y1

    # Take a screenshot of the region
    screenshot = pyautogui.screenshot(region=(x1, y1, width, height))

    # Convert the screenshot to a numpy array and then to grayscale
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Thresholding to isolate near-white text
    _, thresholded = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Use OCR to extract text
    text = pytesseract.image_to_string(thresholded)

    # Compare the OCR text with the options
    compare_text(text)


def compare_text(text):
    # Create a TfidfVectorizer object
    vect = TfidfVectorizer(min_df=1, stop_words="english")

    # Calculate the TF-IDF vectors for the OCR text and the options
    tfidf = vect.fit_transform([text] + options)

    # Calculate the cosine similarity between the OCR text and each option
    similarity_scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()

    # Get the top 3 matches (or fewer if there are not enough options)
    top_matches = similarity_scores.argsort()[-3:][::-1]

    # Define ANSI escape codes for green and red
    green = "\033[32m"
    red = "\033[31m"
    reset = "\033[0m"

    # Print the top matches
    for i, index in enumerate(top_matches):
        option = options[index]
        similarity = similarity_scores[index]
        truth_value = all_statements[option]

        # If it's the first match (most likely), color the output
        if i == 0:
            color = green if truth_value else red
            print(
                f"{color}{option} - match {similarity * 100:.2f}% ANSWER = {'VERDADEIRO' if truth_value else 'FALSO'}{reset}")
        else:
            print(f"{option} - match {similarity * 100:.2f}% ANSWER = {'VERDADEIRO' if truth_value else 'FALSO'}")


# Function to be called when '[' is pressed
def on_press(key):
    if key == keyboard.KeyCode.from_char('['):
        # Perform OCR
        ocr()

# Create a keyboard listener
keyboard_listener = keyboard.Listener(on_press=on_press)

# Start the keyboard listener
keyboard_listener.start()

# Create a simple GUI with a "Start OCR" button
window = Tk()
button = Button(window, text="Start OCR", command=start_capture)
button.pack()
window.mainloop()
