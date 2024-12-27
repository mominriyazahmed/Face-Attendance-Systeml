# Import necessary libraries
import os
import pickle 
import cv2
import face_recognition  
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading  # Used to run face recognition in a separate thread from the GUI
import openpyxl  # For handling Excel files to store attendance data

# Initialize Firebase credentials and database
cred = credentials.Certificate("https://drive.google.com/file/d/16s2u2oht-bMR69LJe0NBqIw6TuBQVqAZ/view?usp=drive_link")
firebase_admin.initialize_app(cred, {
    'databaseURL' : "https://face-attendance-54d34-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket' : "face-attendance-54d34.appspot.com"
})
bucket = storage.bucket()

# Setup the webcam and background image for the GUI
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set frame width
cap.set(4, 480)  # Set frame height
imgBackground = cv2.imread('Resources/background.png')  # Load the background image

# Load mode images for different states of the system
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

# Load the face encodings and student IDs from the saved encoding file
file = open('EncodeFile.p', 'rb')  # Open the file with the face encodings
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds  # Unpack the encodings and student IDs

# Initialize variables for the system state
modeType = 0
counter = 0
id = -1
imgStudent = []

# Initialize an Excel workbook to store attendance records
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["ID", "Name", "Total Attendance", "Last Attendance Time"])

# Dictionary to store the last attendance time for each student
last_attendance_time_dict = {}

# Start face recognition process in a separate thread
def start_recognition():
    global imgBackground, modeType, counter, id, imgStudent

    while True:
        success, img = cap.read()  # Capture frame from webcam
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Resize for faster processing
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # Convert image to RGB (required by face_recognition)
        faceCurFrame = face_recognition.face_locations(imgS)  # Detect face locations in the frame
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)  # Get face encodings

        imgBackground[162:162 + 480, 55:55 + 640] = img  # Display webcam feed on the background image
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]  # Display current mode image

        if faceCurFrame:  # If faces are detected
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)  # Compare with known faces
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)  # Calculate face distance

                matchIndex = np.argmin(faceDis)  # Find the closest match
                if matches[matchIndex]:  # If a match is found
                    y1, x2, y2, x1 = faceLoc  # Get coordinates of the face
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scale up the coordinates
                    bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1  # Create bounding box around the face
                    imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)  # Draw the bounding box on the image
                    id = studentIds[matchIndex]  # Get student ID

                    # Check if attendance can be marked for this student
                    if can_mark_attendance(id):
                        print(f"Attendance marked for ID: {id}")
                        cvzone.putTextRect(imgBackground, "Loading", (275, 400))  # Display "Loading" message
                        cv2.imshow("Face Attendance", imgBackground)  # Show the updated image
                        cv2.waitKey(1)  # Wait for a short period
                        counter = 1
                        modeType = 1  # Change mode to show "Attendance in Progress"

                        # Get student information from Firebase
                        student_info = db.reference(f'Students/{id}').get()
                        datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
                        ws.append([id, student_info['name'], student_info['total_attendance'], datetime_now])  # Log attendance in Excel
                        wb.save("attendance_record.xlsx")  # Save the Excel file

                        # Update the last attendance time in the dictionary
                        last_attendance_time_dict[id] = datetime.now()

            if counter != 0:  # If the counter is not zero, proceed with attendance processing
                if counter == 1:
                    student_info = db.reference(f'Students/{id}').get()
                    blob = bucket.get_blob(f'Images/{id}.png')  # Fetch student image from Firebase storage
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                    attendance_marked = False

                    # Calculate the time since last attendance
                    datetimeObject = datetime.strptime(student_info['last_attendance_time'], "%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

                    # If more than 60 seconds have passed, mark attendance again
                    if secondsElapsed > 60:
                        ref = db.reference(f'Students/{id}')
                        student_info['total_attendance'] += 1  # Increment total attendance
                        ref.child('total_attendance').set(student_info['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # Update last attendance time
                    else:
                        modeType = 3  # Change mode to "Already Attended"
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if modeType != 3:  # If mode is not "Already Attended"
                    if 10 < counter < 20:
                        modeType = 2  # Change mode to "Finalizing Attendance"

                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter <= 10:  # If the counter is less than or equal to 10, display student details
                        cv2.putText(imgBackground, str(student_info['total_attendance']), (861, 125),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(student_info['major']), (1006, 550),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(id), (1006, 493),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                        cv2.putText(imgBackground, str(student_info['standing']), (910, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(student_info['year']), (1025, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                        cv2.putText(imgBackground, str(student_info['starting_year']), (1125, 625),
                                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                        # Display student name with appropriate offset
                        (w, h), _ = cv2.getTextSize(student_info['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                        offset = (414 - w) // 2
                        cv2.putText(imgBackground, str(student_info['name']), (808 + offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        # Show student image on the background
                        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                    counter += 1

                    if counter >= 20:  # Reset the counter and mode after 20 frames
                        counter = 0
                        modeType = 0
                        student_info = []
                        imgStudent = []
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
        else:
            modeType = 0  # No face detected, reset mode and counter
            counter = 0

        cv2.imshow("Face Attendance", imgBackground)  # Show the final image with the webcam feed and mode
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit if 'q' is pressed
            break

    cap.release()  # Release the webcam
    cv2.destroyAllWindows()  # Close all OpenCV windows

# Function to update the GUI with the webcam feed
def update_gui():
    _, img = cap.read()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (640, 480))
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(image=img)

    label_webcam.imgtk = img
    label_webcam.configure(image=img)

    root.update()

    root.after(10, update_gui)  # Update the GUI every 10ms

# Function to close the face recognition process and the Tkinter window
def close_face_recognition():
    global cap
    cap.release()
    root.destroy()

# Function to check if attendance can be marked for a student
def can_mark_attendance(student_id):
    if student_id in last_attendance_time_dict:
        datetimeObject = last_attendance_time_dict[student_id]
        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
        return secondsElapsed > 30  # Only mark attendance if more than 30 seconds have passed
    else:
        return True  # Mark attendance if it's the first time the student is detected

# Create a Tkinter window for displaying the GUI
root = tk.Tk()
root.title("Face Recognition Attendance System")
root.geometry("800x600")

# Create a label widget to display the webcam feed
label_webcam = tk.Label(root)
label_webcam.pack(padx=10, pady=10)

# Start the face recognition in a separate thread
start_recognition()
