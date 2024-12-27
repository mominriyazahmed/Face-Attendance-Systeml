# Importing necessary libraries for image processing, face recognition, file handling, and Firebase interactions
import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# Initializing Firebase with credentials and database configuration
cred = credentials.Certificate("https://drive.google.com/file/d/16s2u2oht-bMR69LJe0NBqIw6TuBQVqAZ/view?usp=drive_link")
firebase_admin.initialize_app(cred , {
    # Database URL for Firebase Realtime Database
    'databaseURL' : "https://face-attendance-54d34-default-rtdb.asia-southeast1.firebasedatabase.app/",
    # Firebase storage bucket URL
    'storageBucket' : "face-attendance-54d34.appspot.com"
})

# Defining the folder path where student images are stored
folderPath = 'Images'
# Getting the list of all files (image names) in the 'Images' folder
pathList = os.listdir(folderPath)
print(pathList)

# Lists to store images and corresponding student IDs
imgList = []
studentIds = []

# Loop through each image in the folder
for path in pathList:
    # Append the image to imgList
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    # Extract student ID (image filename without extension) and append to studentIds list
    studentIds.append(os.path.splitext(path)[0])

    # Upload each image to Firebase Storage
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()  # Get the default storage bucket
    blob = bucket.blob(fileName)  # Create a reference to the image in Firebase Storage
    blob.upload_from_filename(fileName)  # Upload the image to Firebase
    # Optionally, you can print the uploaded image path and student ID (commented here)
    # print(path)
    # print(os.path.splitext(path)[0])

# Output list of student IDs
print(studentIds)

# Function to find and encode faces from images
def findEncodings(imageList):
    encodeList = []  # List to store face encodings
    counter = 0  # Counter for images with no detected faces
    for img in imageList:
        # Convert the image from BGR (OpenCV format) to RGB (required by face_recognition)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Get face encodings from the image
        encodings = face_recognition.face_encodings(img)
        # If faces are detected, append the encoding to the list
        if encodings:  
            encodeList.append(encodings[0])
        else:
            counter += 1  # Increment counter if no face was detected
            print("No face detected in one of the images")
        print(counter)  # Print the number of images with no detected faces
    return encodeList

# Starting the face encoding process
print("Encoding started")
encodeListKnown = findEncodings(imgList)  # Call the function to encode faces
encodeListKnownWithIds = [encodeListKnown, studentIds]  # Pair each encoding with its corresponding student ID
print("Encoding Complete")
print(len(encodeListKnown))  # Print the number of encodings generated

# Save the encoded face data with student IDs to a file for future use
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)  # Serialize the data into the file
file.close()
