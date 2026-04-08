# 🎓 AutoSystem — AI-Powered Attendance Management System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-lightgrey?style=for-the-badge&logo=flask)
![DeepFace](https://img.shields.io/badge/DeepFace-FaceNet-orange?style=for-the-badge)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-green?style=for-the-badge&logo=google)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?style=for-the-badge&logo=opencv)

**AutoSystem** is a real-time, AI-powered attendance system that uses facial recognition and blink-based liveness detection to automatically mark student attendance — eliminating manual roll calls and proxy fraud.

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
  - [Liveness Detection (Anti-Spoofing)](#liveness-detection-anti-spoofing)
  - [Face Recognition Engine](#face-recognition-engine)
  - [Attendance Workflow](#attendance-workflow)
- [Technology Stack](#-technology-stack)
- [AI Models & Algorithms](#-ai-models--algorithms)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Application Routes (API)](#-application-routes-api)
- [Frontend & UI Design](#-frontend--ui-design)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [Seeding Test Data](#-seeding-test-data)
- [Testing](#-testing)
- [Utility Scripts](#-utility-scripts)
- [Configuration & Known Issues](#-configuration--known-issues)
- [Security Notes](#-security-notes)
- [Future Improvements](#-future-improvements)

---

## 🔍 Overview

AutoSystem is a full-stack web application built with **Flask** that automates student attendance using a two-step AI pipeline:

1. **Liveness Check** — MediaPipe Face Mesh detects a real blink to confirm a live person is present (anti-spoofing).
2. **Face Verification** — DeepFace (FaceNet model) compares the live camera frame against stored student profile photos to confirm identity.

Faculty members start a session from their browser, the webcam activates, and attendance is marked automatically per subject per class. Students can log in to view their own attendance history per date and subject.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 AI Face Recognition | FaceNet model via DeepFace with cosine distance metric |
| 👁️ Blink Liveness Detection | MediaPipe Face Mesh EAR (Eye Aspect Ratio) algorithm — prevents photo spoofing |
| 👨‍🏫 Faculty Dashboard | Start attendance sessions per class and subject, view all students, export CSV |
| 🎓 Student Dashboard | View personal attendance logs grouped by date with Present/Absent per subject |
| 📊 Attendance Percentage | Live progress bar with color-coded reliability (green ≥75%, yellow ≥50%, red <50%) |
| 🔁 Multi-Subject Support | Multiple subjects can be marked per day — no conflicts |
| 🔒 Role-Based Auth | Separate login flows for Student and Faculty roles |
| 📤 CSV Export | Faculty can export filtered attendance records as CSV |
| 📝 Activity Logging | All camera events and sessions are logged to `attendance.log` |
| 💅 Premium Glassmorphism UI | Animated background blobs, toast notifications, responsive design |

---

## ⚙️ How It Works

### Liveness Detection (Anti-Spoofing)

To prevent students from showing a photo instead of their real face, a **blink detection** gate is implemented using **MediaPipe Face Mesh**:

1. The webcam feed is processed frame-by-frame using MediaPipe's 468-point 3D face landmark model.
2. The **Eye Aspect Ratio (EAR)** is calculated for both eyes using specific landmark indices:
   - **Left Eye**: Landmarks `362`, `263` (horizontal), `385`, `373`, `387`, `380` (vertical)
   - **Right Eye**: Landmarks `33`, `133` (horizontal), `160`, `153`, `158`, `144` (vertical)
3. EAR Formula:
   ```
   EAR = (vertical_dist_1 + vertical_dist_2) / (2.0 × horizontal_dist)
   Average EAR = (left_EAR + right_EAR) / 2.0
   ```
4. If EAR drops below **0.22–0.25** for at least **2 consecutive frames**, a blink is confirmed.
5. Only after a confirmed blink does the system proceed to the expensive face verification step.

> **Why this matters:** This approach prevents photo-based spoofing and significantly reduces unnecessary API calls to DeepFace — making the system both secure and performant.

---

### Face Recognition Engine

The `FaceEngine` class (`face_engine.py`) encapsulates the AI verification logic:

1. On confirmed blink, the current camera frame is saved as a temporary JPEG file.
2. **DeepFace.verify()** is called to compare the temp frame against each registered student's profile photo:
   - **Model**: `Facenet` (128-dimension face embedding)
   - **Detector Backend**: `opencv`
   - **Distance Metric**: `cosine`
   - **enforce_detection**: `False` (handles partially visible faces gracefully)
3. If `verified = True` and cosine distance `< 0.5`, the student is marked as detected.
4. The temp file is cleaned up after use (`cleanup()` method).

---

### Attendance Workflow

```
Faculty starts session → Selects class & subject → Webcam opens
        ↓
MediaPipe processes each frame → Calculates EAR
        ↓
Blink detected (EAR < threshold for 2+ frames)
        ↓
DeepFace.verify() runs against all student photos in that class
        ↓
Matched student added to detected_students list
        ↓
Faculty presses ESC → Camera closes
        ↓
AttendanceService.mark_attendance() called
- All students in the class get a record: Present or Absent
- Existing records updated only if upgrading Absent → Present
        ↓
Faculty dashboard refreshes with updated counts
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend Framework** | Flask 2.x | Web server, routing, session management |
| **AI - Face Verification** | DeepFace (FaceNet) | Face embedding & identity matching |
| **AI - Liveness** | MediaPipe Face Mesh | 468-point face landmarks, blink/EAR |
| **Computer Vision** | OpenCV (`cv2`) | Webcam capture, frame processing, rendering |
| **Deep Learning Runtime** | TensorFlow | Backend for DeepFace model inference |
| **ORM** | SQLAlchemy | Database models and sessions |
| **Database** | SQLite | Local file-based relational database |
| **Templating** | Jinja2 (Flask built-in) | HTML template rendering |
| **CSS Framework** | Bootstrap 5.3.2 | Responsive grid and UI components |
| **Custom CSS** | Vanilla CSS (Glassmorphism) | Animated blobs, custom cards, gradients |
| **Notifications** | Toastify.js | In-browser flash messages |
| **PDF Generation** | fpdf2 | Convert research markdown to IEEE PDF |
| **Fonts** | Google Fonts (Outfit, Lexend, Inter) | Modern typography |
| **Icons** | Font Awesome 6.5 | UI icons throughout |
| **File Upload** | Werkzeug `secure_filename` | Safe student profile photo uploads |

---

## 🤖 AI Models & Algorithms

### FaceNet (via DeepFace)
- **Architecture**: Deep Convolutional Neural Network
- **Output**: 128-dimensional face embedding vector
- **Matching Method**: Cosine similarity (`distance < 0.5` = verified match)
- **Training**: Trained on millions of face images; transfer learning applied
- **Why FaceNet**: Balance of speed and accuracy. Better than VGG-Face for real-time use cases.

### MediaPipe Face Mesh
- **Landmark Points**: 468 3D facial landmarks per face
- **Used Landmarks for EAR**:
  - Left Eye horizontal: `362 → 263`
  - Left Eye vertical: `385↕373`, `387↕380`
  - Right Eye horizontal: `33 → 133`
  - Right Eye vertical: `160↕153`, `158↕144`
- **Threshold**: EAR `< 0.22` (in `app.py`) / `< 0.25` (in `face_engine.py`)
- **Consecutive Frames**: Minimum 2 frames below threshold for confirmed blink

### EAR (Eye Aspect Ratio) Algorithm
Based on the work by Soukupová & Čech (2016). It is a simple, fast calculation that captures the geometry of the eye opening:

```python
EAR = (||p2-p6|| + ||p3-p5||) / (2 × ||p1-p4||)
```
Where `p1–p6` are the six eye landmark coordinates (adapted here to MediaPipe indices).

---

## 📁 Project Structure

```
AutoSystem/
│
├── app.py                      # Main Flask application — all routes & webcam logic
├── face_engine.py              # FaceEngine class — EAR calculation & DeepFace verify
├── attendance_service.py       # AttendanceService class — marks Present/Absent in DB
├── models.py                   # SQLAlchemy ORM models (Student, Faculty, Attendance)
├── database.py                 # SQLAlchemy engine, session, Base setup (SQLite)
│
├── requirements.txt            # Python dependencies
├── attendance.db               # SQLite database file (auto-created on first run)
├── attendance.log              # Application activity log file
│
├── seed_data.py                # Script to insert dummy students and faculty into DB
├── scratch_db.py               # Quick SQLite query script to inspect students table
├── verify_auth.py              # Test script: registration and login verification flow
├── generate_pdf.py             # Converts research_paper.md → IEEE-style PDF via fpdf2
├── research_paper.md           # Research paper in Markdown format
├── research_paper.html         # Research paper in HTML format
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom glassmorphism CSS — design system
│   └── uploads/                # Student profile photos (uploaded during registration)
│
├── templates/
│   ├── base.html               # Base Jinja2 template — layout, fonts, scripts, toasts
│   ├── login.html              # Login page (email, password, role selector)
│   ├── register.html           # Registration page (student fields + photo upload)
│   ├── faculty_dashboard.html  # Faculty hub — session starter + student journal table
│   └── student_dashboard.html  # Student hub — attendance log grouped by date
│
└── tmp/
    ├── test_attendance.py      # Unit test: attendance marking logic (no duplicates)
    └── test_school_mode.py     # Integration test: multi-subject + overwrite scenarios
```

---

## 🗄️ Database Schema

The database is SQLite (`attendance.db`), managed via SQLAlchemy ORM. Three tables:

### `students`
| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | STRING | Full name (required) |
| `email` | STRING UNIQUE | Login credential (required) |
| `password` | STRING | Plain text (stored as-is) |
| `image` | STRING | Filename of uploaded profile photo |
| `class_name` | STRING | Class/grade e.g. `10th-A` (was `subject`) |
| `roll_number` | STRING | Roll number e.g. `24` (was `subject_code`) |

### `faculty`
| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `name` | STRING | Full name (required) |
| `email` | STRING UNIQUE | Login credential (required) |
| `password` | STRING | Plain text (stored as-is) |

### `attendance`
| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `student_id` | INTEGER FK → students.id | Which student |
| `faculty_id` | INTEGER FK → faculty.id | Who marked it (nullable) |
| `subject_name` | STRING | Subject being marked (e.g. `Math`) |
| `date` | STRING | Format: `YYYY-MM-DD` |
| `status` | STRING | `"Present"` or `"Absent"` |

> **Design Note**: Each student gets one record per subject per day. Running attendance again for the same subject/day only upgrades `Absent → Present`, never downgrades.

---

## 🌐 Application Routes (API)

| Method | Route | Auth Required | Description |
|---|---|---|---|
| `GET` | `/` | No | Renders login page |
| `GET` | `/register` | No | Renders registration form |
| `POST` | `/register` | No | Handles user registration (Student or Faculty) |
| `POST` | `/login` | No | Authenticates user, sets session, redirects to dashboard |
| `GET` | `/student_dashboard` | Student session | Shows student's attendance records by date |
| `GET` | `/faculty_dashboard` | Faculty session | Shows all students with attendance stats |
| `POST` | `/start_attendance` | Faculty session | Opens webcam, runs AI scan, marks attendance |
| `GET` | `/export_attendance` | Faculty session | Downloads attendance data as CSV |
| `GET` | `/logout` | Any | Clears session, redirects to login |

---

## 🎨 Frontend & UI Design

### Design Philosophy
The UI follows a **premium glassmorphism** aesthetic with light-mode theming:

- **Animated Background**: Three floating gradient blobs (`blob-1`, `blob-2`, `blob-3`) using CSS `@keyframes blobFloat` — subtle, 40-second loop.
- **Glass Cards**: `backdrop-filter: blur(20px)`, semi-transparent white background (`rgba(255,255,255,0.8)`), soft border.
- **Hover Effects**: Cards lift `translateY(-4px)` on hover with elevated shadow.
- **Color Palette**:
  - Brand Primary: `#4f46e5` (Indigo 600)
  - Brand Secondary: `#0d9488` (Teal 600)
  - Accent: `#f43f5e` (Rose 500)
  - Background: `#f8fafc` (Sky 50)
- **Typography**: `Outfit` (headings, 800 weight), `Lexend` (body text)
- **Toast Notifications**: Toastify.js for flash messages — green gradient for success, red for errors.

### Pages

#### Login (`login.html`)
- Fingerprint icon header with `text-gradient` brand title
- Email + password fields with Font Awesome icons
- Role selector (Student / Faculty)
- Password visibility toggle (eye icon)
- Link to registration page

#### Register (`register.html`)
- Dynamic form — student-only fields (Class, Roll Number, Profile Photo) appear/hide based on role selection via `toggleStudentFields()` JS
- File input accepts `image/*` — validated server-side to `png/jpg/jpeg` only
- Minimum password length: 6 characters

#### Faculty Dashboard (`faculty_dashboard.html`)
- **Session Starter Widget** (left column): Selects Class/Group and Subject Area (with custom "Other" entry). Submits to `/start_attendance`.
- **Session Journal Table** (right column): Lists all students with avatar, name, email, class, roll number, attendance percentage (color-coded progress bar), and present count.
- **Search** bar for filtering students by name/email.
- **CSV Export** button that passes current filter state.

#### Student Dashboard (`student_dashboard.html`)
- Attendance logs grouped by date (newest first)
- Each subject shown as a card with `P` (Present) or `A` (Absent) pill badge
- Empty state shown if no records exist yet

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- `pip` package manager
- A webcam (required for AI attendance)
- Windows / macOS / Linux

### Step 1: Clone or Download the Repository
```bash
# If using git
git clone <repository-url>
cd AutoSystem

# Or navigate to the folder directly
cd "C:\Users\vafid\Downloads\AutoSystem\AutoSystem"
```

### Step 2: Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**`requirements.txt` contents:**
```
flask
opencv-python
deepface
tensorflow
numpy
sqlalchemy
mediapipe
```

> ⚠️ **Dependency Notes:**
> - `tensorflow` and `mediapipe` have version sensitivity. If you encounter conflicts, try:
>   ```bash
>   pip install tensorflow==2.13.0 mediapipe==0.10.9
>   ```
> - DeepFace will automatically download the FaceNet model weights on first run (~90 MB).
> - OpenCV requires no additional system libraries on Windows. On Linux, you may need `libgl1`.

### Step 4: Initialize the Database
The database is auto-created on first run. Alternatively, run:
```bash
python seed_data.py
```
This inserts 5 sample students and 2 faculty members.

---

## ▶️ Running the Application

```bash
python app.py
```

The Flask development server starts at:
```
http://127.0.0.1:5000
```

Open your browser and navigate to `http://127.0.0.1:5000` to see the login page.

> For production deployment, replace `app.run(debug=True)` with a WSGI server like **Gunicorn**:
> ```bash
> pip install gunicorn
> gunicorn -w 4 app:app
> ```

---

## 🌱 Seeding Test Data

To quickly populate the database with sample students and faculty:

```bash
python seed_data.py
```

**Inserted Students:**

| Name | Email | Password | Subject | Code |
|---|---|---|---|---|
| Ravi | ravi@gmail.com | 123 | Math | M101 |
| Asha | asha@gmail.com | 123 | Science | S102 |
| Rahul | rahul@gmail.com | 123 | English | E103 |
| Priya | priya@gmail.com | 123 | Computer | C104 |
| Kiran | kiran@gmail.com | 123 | Physics | P105 |

**Inserted Faculty:**

| Name | Email | Password |
|---|---|---|
| Mr. Kumar | kumar@gmail.com | 123 |
| Ms. Devi | devi@gmail.com | 123 |

> ⚠️ Note: The seed data uses old field names (`subject`, `subject_code`) — update to `class_name`, `roll_number` if using the latest schema.

---

## 🧪 Testing

Two test scripts are located in the `tmp/` directory:

### `tmp/test_attendance.py`
Tests the core attendance marking logic:
- Marks a student as Absent on first run
- Marks the same student as Present on second run (same day/subject)
- Verifies no duplicate records are created
- Confirms the `Absent → Present` upgrade logic works correctly

```bash
python tmp/test_attendance.py
```

### `tmp/test_school_mode.py`
Full integration test for school-mode (multi-teacher, multi-subject):
- Creates 2 faculty members and 1 student in class `10th-A`
- Teacher 1 marks **Math** as Present
- Teacher 2 marks **Science** as Present
- Verifies 2 separate records exist (not merged)
- Tests attendance correction (overwrite Present → Absent for Math)

```bash
python tmp/test_school_mode.py
```

### `verify_auth.py`
Tests registration and login verification flow using hashed passwords (Werkzeug):
```bash
python verify_auth.py
```

---

## 🛠️ Utility Scripts

### `scratch_db.py`
Quick SQLite inspection — prints the students table as a Markdown table to the terminal:
```bash
python scratch_db.py
```

### `generate_pdf.py`
Converts `research_paper.md` into an IEEE-style PDF using `fpdf2`:
```bash
pip install fpdf2
python generate_pdf.py
# Output: AutoSystem_IEEE_Research_Paper.pdf
```

---

## ⚙️ Configuration & Known Issues

### Configuration
All configuration is currently inline in `app.py`:

| Setting | Location | Current Value |
|---|---|---|
| Flask Secret Key | `app.secret_key` | `"secret_key"` |
| Upload Folder | `UPLOAD_FOLDER` | `"static/uploads"` |
| Database URI | `database.py` | `"sqlite:///attendance.db"` |
| EAR Threshold | `app.py` / `face_engine.py` | `0.22` / `0.25` |
| Consecutive Frames | Both files | `2` |
| DeepFace Model | `app.py` / `face_engine.py` | `"Facenet"` |
| Distance Threshold | `app.py` | `< 0.5` |

### Known Issues & Limitations

1. **Typo in `app.py` Line 15**: `locdcdcdzgging.INFO` — should be `logging.INFO`. This causes a `NameError` on startup. Fix:
   ```python
   # Line 15 - BEFORE (broken)
   logging.basicConfig(filename='attendance.log', level=locdcdcdzgging.INFO, ...)
   
   # AFTER (fixed)
   logging.basicConfig(filename='attendance.log', level=logging.INFO, ...)
   ```

2. **Plaintext Passwords**: Passwords are stored as plaintext in the database. Use `werkzeug.security.generate_password_hash` for production.

3. **Global DB Session**: `db = Session()` is created globally in `app.py` — this is not thread-safe. Consider using `scoped_session` for production.

4. **`start_attendance` is Blocking**: The webcam capture loop runs synchronously in the web request thread — the browser will appear frozen until the faculty presses ESC. Consider offloading to a background thread or using WebSockets in a future version.

5. **`face_engine.py` vs `app.py` Duplication**: The `FaceEngine` class in `face_engine.py` is a refactored version. `app.py` still uses its own inline EAR calculation. These should be consolidated.

6. **`seed_data.py` Uses Old Field Names**: References `subject` / `subject_code` but the model uses `class_name` / `roll_number`.

---

## 🔐 Security Notes

| Risk | Current State | Recommended Fix |
|---|---|---|
| Secret Key | Hardcoded `"secret_key"` | Load from environment variable |
| Passwords | Plaintext storage | Use `werkzeug.security` hashing |
| Session Security | Flask default (cookie-based) | Set `SESSION_COOKIE_SECURE=True` in production (HTTPS) |
| File Uploads | Extension checked (png/jpg/jpeg) | Add MIME type validation + file size limit |
| CSRF Protection | Not implemented | Use Flask-WTF for CSRF tokens |
| SQL Injection | Protected by SQLAlchemy ORM | ✅ Safe |

---

## 🔮 Future Improvements

- [ ] **Multi-threading for webcam** — Background thread for `/start_attendance` so browser doesn't freeze
- [ ] **Real-time WebSocket feed** — Show live camera feed in the browser (Flask-SocketIO)
- [ ] **Password hashing** — Migrate to `werkzeug.security` hashed passwords
- [ ] **Environment config** — Move secrets to `.env` with `python-dotenv`
- [ ] **Attendance reports** — PDF/Excel export per student per month
- [ ] **Admin panel** — Manage all users, reset passwords, delete records
- [ ] **Anti-spoofing upgrade** — Replace blink detection with a dedicated liveness model (e.g., FAS Net)
- [ ] **Mobile support** — Use device camera API for mobile browsers
- [ ] **Notifications** — Email/SMS alerts to students when marked absent
- [ ] **Deployment** — Dockerize the app + PostgreSQL database for production

---

## 📄 Research Paper

A research paper documenting the system's design, methodology, and evaluation is included:

- **Markdown**: [`research_paper.md`](./research_paper.md)
- **HTML**: [`research_paper.html`](./research_paper.html)
- **PDF** (generate locally): Run `python generate_pdf.py` → `AutoSystem_IEEE_Research_Paper.pdf`

---

## 📜 License

This project is developed for academic and educational purposes.

---

<div align="center">

**Built with ❤️ using Flask · DeepFace · MediaPipe · OpenCV · SQLAlchemy**

</div>
