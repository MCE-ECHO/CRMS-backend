
# 🏫 College Classroom Management System

[![Django](https://img.shields.io/badge/Django-4.2-brightgreen)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST-3.15-blue)](https://www.django-rest-framework.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Django-based system for managing classroom bookings, timetables, and admin analytics.

![Dashboard Preview](https://via.placeholder.com/1500x600.png?text=Admin+Dashboard+Preview)

---

## ✨ Features

- **Admin Dashboard**:  
  📊 Real-time charts for classroom usage, peak hours, and faculty activity  
- **Booking Management**:  
  ✅ Approve/reject requests • 🕒 Conflict detection • 📅 Availability checker  
- **Timetable Operations**:  
  📥 Bulk CSV/Excel upload • ✏️ Edit entries • 📤 Export to CSV  
- **Security**:  
  🔒 Role-based access • 🛡️ CSRF protection  

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/Rakshak-D/CLASSROOMS.git
cd CLASSROOMS
pip install -r requirements.txt
```

### 2. Configure Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Run Server
```bash
python manage.py runserver
```
Access: `http://localhost:8000/admin-dashboard/`

---

## 🛠 Tech Stack

| Category       | Technologies                                |
|----------------|---------------------------------------------|
| **Frontend**   | HTML • CSS • Chart.js • SweetAlert2         |
| **Backend**    | Django • Django REST Framework              |
| **Database**   | SQLite (Default) • PostgreSQL (Production)  |
| **Data Tools** | Pandas • OpenPyXL                           |

---

## 📂 Repository Structure
```
CLASSROOMS/
├── accounts/          # Authentication
├── admin_dashboard/   # Dashboard logic & templates
├── booking/           # Booking models/views
├── classroom/         # Classroom management
├── timetables/        # Timetable CRUD operations
├── requirements.txt   # Dependencies
└── .gitignore         # Ignored files
```

---

## 📝 Requirements
**requirements.txt** (root directory):
```text
Django==4.2.11
djangorestframework==3.15.1
pandas==2.2.1
openpyxl==3.1.2
python-dateutil==2.9.0
```

---

## 📜 License
MIT License - See [LICENSE](LICENSE) for details.

---

## 📧 Contact
**Rakshak D**  
📧 rakshakmce@gmail.com  
🔗 [GitHub Profile - Rakshak-D](https://github.com/Rakshak-D)

---
