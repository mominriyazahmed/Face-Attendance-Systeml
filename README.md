# Face Attendance System

A Python-based face recognition attendance system that uses Firebase for database management and Tkinter for the graphical user interface (GUI). This project enables real-time attendance marking and includes features to register new students with their details and photos.

## Features

- **Face Recognition:** Automatically detects and recognizes faces to mark attendance.
- **Student Registration:** Add new students with their details and photo through a GUI.
- **Database Integration:** Firebase Realtime Database is used for storing student data and attendance records.
- **GUI Interface:** User-friendly interface built with Tkinter.
- **Excel Export:** Attendance records are saved in an Excel file for easy access.

## Installation

### Prerequisites

- Python 3.10 or later
- Firebase account with a Realtime Database and Cloud Storage setup
- Installed libraries:
  ```bash
  pip install firebase-admin face_recognition opencv-python-headless numpy cvzone openpyxl
  ```

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your_username/your_repo_name.git
   cd your_repo_name
   ```

2. Add your Firebase configuration:
   - Place your `serviceAccountKey.json` file in the project directory.

3. Prepare the environment:
   - Create an `Images` folder and add student photos named as `student_id.png`.
   - Ensure the required directories and files exist as per the project setup.

4. Run the application:
   - Start the GUI:
     ```bash
     python main_with_gui_excel2.py
     ```
   - Optional: Generate encodings for new student photos:
     ```bash
     python EncodeGenerator.py
     ```
   - Optional: Initialize the database:
     ```bash
     python AddData_to_database.py
     ```

## Usage

1. **Register a Student:**
   - Open the GUI.
   - Click on "Register New Student."
   - Enter the student details and upload their photo.

2. **Mark Attendance:**
   - Start the recognition system via the GUI.
   - The system will detect and mark attendance for recognized faces.

3. **Check Records:**
   - Attendance records are saved in the Firebase database.
   - An Excel file (`attendance_record.xlsx`) is generated locally for offline access.

## Technologies Used

- **Python**: Core programming language.
- **OpenCV**: For image processing.
- **Face Recognition**: Library for facial encoding and recognition.
- **Tkinter**: For building the GUI.
- **Firebase**: Backend database and storage.
- **OpenPyXL**: For working with Excel files.

## Contributors

- **Riyaz Momin** - Developer and Project Owner

## Future Enhancements

- Add multi-camera support.
- Integrate email or SMS notifications.
- Enhance security with multi-factor authentication.
- Add a dashboard for viewing and managing attendance records online.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
