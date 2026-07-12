# ICT BD Bus Services Ltd - Web-Based Bus Ticketing Management System

A full-stack web application for managing intercity bus ticketing operations, built with **Flask** and **PostgreSQL**. Provides online booking for customers, counter booking for staff, and full administrative control over buses, routes, schedules, and finances.

---

## Features

### Authentication & Authorization
- Secure login, registration, and password reset
- Role-based access control: **Administrator**, **Ticket Counter Staff**, **Customer**
- Session management with Flask-Login

### Administrator
- Dashboard with KPI cards (revenue, bookings, cancellation rate, active buses)
- Manage buses (CRUD), routes (CRUD), and schedules (CRUD)
- User management with role assignment and activation/deactivation
- Financial and operational reports (daily, weekly, monthly)
- View all bookings and payments system-wide

### Customer
- Search available buses by origin, destination, date, and bus type
- Interactive seat selection grid (available / booked / selected states)
- Mock payment gateway (bKash, Nagad, Rocket, Card, Cash)
- Booking history with confirmed and cancelled statuses
- Download e-ticket as PDF with QR code
- Cancel bookings with 80% refund policy
- Profile management

### Ticket Counter Staff
- Counter booking flow: search → select seat → enter passenger info → cash payment
- View all bookings and payments
- Reprint tickets and cancel bookings

### System-Wide
- PDF e-ticket generation with QR codes via ReportLab
- Real-time seat availability API
- Bootstrap 5 responsive UI with role-based sidebar navigation
- Flash notifications for all user actions

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.14, Flask 3.1.1 |
| Database | PostgreSQL 18.4, SQLAlchemy ORM |
| Frontend | Jinja2 templates, Bootstrap 5, Bootstrap Icons |
| Auth | Flask-Login, Flask-WTF (CSRF protection) |
| PDF | ReportLab, qrcode |
| Migrations | Flask-Migrate (Alembic) |

---

## Project Structure

```
bus_ticketing/
├── app/
│   ├── __init__.py          # App factory & blueprint registration
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions (db, migrate, login, csrf)
│   ├── models/              # SQLAlchemy models (7 tables)
│   │   ├── user.py
│   │   ├── bus.py
│   │   ├── route.py
│   │   ├── schedule.py
│   │   ├── booking.py
│   │   ├── ticket.py
│   │   └── payment.py
│   ├── auth/                # Authentication & decorators
│   ├── admin/               # Administrator module
│   ├── customer/            # Customer module
│   ├── staff/               # Staff module
│   ├── utils/               # PDF generation, helpers
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JS, images
├── migrations/              # Alembic migration scripts
├── run.py                   # Application entry point
├── seed.py                  # Database seed script
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not committed)
└── .gitignore
```

---

## Database Schema

| Table | Description |
|-------|-------------|
| `users` | Admin, Staff, and Customer accounts |
| `buses` | Bus registration (number, type, capacity) |
| `routes` | Origin-destination pairs with fare and distance |
| `schedules` | Departure times, available seats, status |
| `bookings` | Links users to schedules with seat info |
| `tickets` | E-ticket details and QR codes |
| `payments` | Transaction records with payment method |

---

## Setup & Installation

### Prerequisites
- Python 3.14+
- PostgreSQL 18.4+

### 1. Clone the repository
```bash
git clone https://github.com/shamimhossain52/bus-ticketing-system.git
cd bus-ticketing-system
```

### 2. Create a virtual environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/bus_ticketing
```

### 5. Create the database
```sql
-- In PostgreSQL
CREATE DATABASE bus_ticketing;
```

### 6. Run database migrations
```bash
flask db upgrade
```

### 7. Seed initial data (optional)
```bash
python seed.py
```

This creates sample users, buses, routes, and schedules.

**Default accounts:**

| Role | Email | Password |
|------|-------|----------|
| Administrator | admin@ictbd.com | admin123 |
| Staff | staff@ictbd.com | staff123 |
| Customer | customer@test.com | customer123 |

### 8. Run the development server
```bash
python run.py
```

Visit **http://127.0.0.1:5000** in your browser.

---

## Screenshots

<img width="1221" height="587" alt="image" src="https://github.com/user-attachments/assets/8dc6792a-e1a1-4289-b8fe-7196474fa879" />
<img width="1417" height="450" alt="image" src="https://github.com/user-attachments/assets/91b8ada1-104d-44c9-876d-e5b5f1993304" />
<img width="1412" height="413" alt="image" src="https://github.com/user-attachments/assets/3a1345ea-5e10-4221-a2f2-f285261c7ece" />
<img width="1417" height="543" alt="image" src="https://github.com/user-attachments/assets/01b6a605-47aa-49e3-82e0-54210fb35976" />
<img width="1285" height="610" alt="image" src="https://github.com/user-attachments/assets/660bd233-68ff-4bbb-be81-383ff35b5cf6" />


## License

This project was developed as a coursework assignment for **ICT BD Bus Services Ltd**.

---

## Author

**Gazi Shamim**  
[GitHub](https://github.com/shamim3000)
