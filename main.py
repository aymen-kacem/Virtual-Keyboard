import cv2
import time
import numpy as np
from cvzone.HandTrackingModule import HandDetector


class Button:
    def __init__(self, pos, text, size=(85, 85)):
        self.pos = pos
        self.size = size
        self.text = text


# Initialize video capture and hand detector
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 520)

detector = HandDetector(detectionCon=0.8, minTrackCon=0.2)

# Define virtual keyboard layout
keyboard_keys = [
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"],
    ["SPACE", "ENTER", "BACKSPACE"]
]

# Create buttons
button_list = []
for k in range(len(keyboard_keys)):
    for x, key in enumerate(keyboard_keys[k]):
        if key not in ["SPACE", "ENTER", "BACKSPACE"]:
            button_list.append(Button((100 * x + 25, 100 * k + 50), key))
        elif key == "ENTER":
            button_list.append(Button((100 * x - 30, 100 * k + 50), key, (220, 85)))
        elif key == "SPACE":
            button_list.append(Button((100 * x + 780, 100 * k + 50), key, (220, 85)))
        elif key == "BACKSPACE":
            button_list.append(Button((100 * x + 140, 100 * k + 50), key, (400, 85)))

# Typing variables
typed_text = ""
key_press_start = {}  # Track the timing for each key

def draw_buttons(img, button_list):
    """Draw buttons with a transparent look."""
    overlay = img.copy()
    for button in button_list:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(overlay, button.pos, (x + w, y + h), (37, 238, 250), cv2.FILLED)
        cv2.putText(overlay, button.text, (x + 20, y + 65),
                    cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)
        cv2.rectangle(overlay, button.pos, (x + w, y + h), (255, 255, 255), 2)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)
    return img


while True:
    success, img = cap.read()
    allHands, img = detector.findHands(img)

    # Draw keyboard buttons and text display
    img = draw_buttons(img, button_list)
    cv2.rectangle(img, (25, 10), (1050, 60), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, typed_text, (35, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)

    if len(allHands) > 0:
        lm_list = allHands[0]['lmList']
        for button in button_list:
            x, y = button.pos
            w, h = button.size

            # Check if the index finger is over a button
            if x < lm_list[8][0] < x + w and y < lm_list[8][1] < y + h:
                cv2.rectangle(img, button.pos, (x + w, y + h), (247, 45, 134), cv2.FILLED)
                cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)

                # Start timing the button press
                if button.text not in key_press_start:
                    key_press_start[button.text] = time.time()

                # Register the key press if held for 1 second
                if time.time() - key_press_start[button.text] > 1:
                    if button.text == "SPACE":
                        typed_text += " "
                    elif button.text == "ENTER":
                        typed_text += "\n"
                    elif button.text == "BACKSPACE":
                        typed_text = typed_text[:-1]
                    else:
                        typed_text += button.text

                    # Remove the key from the timing dictionary to avoid repeats
                    del key_press_start[button.text]

            # Reset timing if the finger leaves the button
            elif button.text in key_press_start:
                del key_press_start[button.text]

    cv2.imshow("Virtual Keyboard", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Exit on ESC key
        break

cap.release()
cv2.destroyAllWindows()
