# Importing the necessary modules from the Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials  # For loading credentials from a file
from firebase_admin import db  # For interacting with Firebase Realtime Database

# Initializing Firebase Admin SDK with a service account key (serviceAccountKey.json)
cred = credentials.Certificate("https://drive.google.com/file/d/16s2u2oht-bMR69LJe0NBqIw6TuBQVqAZ/view?usp=drive_link")
firebase_admin.initialize_app(cred , {
    # URL of your Firebase Realtime Database
    'databaseURL' : "https://face-attendance-54d34-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

# Reference to the 'Students' node in the Firebase Realtime Database
ref = db.reference('Students')

# Dictionary to store student data; key represents student ID (e.g., 9) and the value is their information
data = {
    "9":  # The key '9' represents the student ID, and it is expected that the image name should be 9.png for attendance
        {
            "name": "Riyaz Momin",  # Student's name
            "major": "Data Science",  # Student's major
            "starting_year": 2018,  # Year the student started
            "total_attendance": 12,  # Total number of attendance records
            "standing": "G",  # Standing in the class (e.g., 'G' could mean 'Good')
            "year": 2,  # The year of study (e.g., 2nd year)
            "last_attendance_time": "2022-12-11 00:54:34"  # The last recorded attendance time
        },
    # You can add more students here if necessary in a similar format
}

# Looping through the data dictionary and pushing each student's information to Firebase Realtime Database
for key, value in data.items():
    # Using the student ID as the key and setting the student's data in Firebase
    ref.child(key).set(value)
