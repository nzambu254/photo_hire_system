# 📸 Liz Web - Photography Equipment Hire System

A Django-based web platform for managing photography equipment rentals. Customers can browse, book, and pay for equipment; staff can issue and process returns; admins manage everything.

---

## ✨ Features

- **3 User Roles**: Admin, Staff, Customer (role-based dashboards and permissions)
- **Equipment Catalog**: Browse cameras, lenses, lighting kits, tripods — with **real product images**
- **Online Booking**: Select hire dates, instant cost calculation, date validation
- **Real M-Pesa STK Push**: Actual Daraja sandbox — push notification appears on your phone, no real money charged
- **Card Payments**: Simulated card payment for demo
- **Password Eye Toggle**: Click the eye icon on any password field to show/hide what you're typing
- **Inventory Tracking**: Real-time status updates (available → reserved → hired → returned)
- **Return Processing**: Late fee calculation, damage charge assessment
- **Overdue Alerts**: Dashboard warnings for overdue equipment
- **Finance Module**: Revenue reports, payment history, monthly trends

---

## 🚀 Setup Instructions (Windows)

### 1. Open Command Prompt and navigate to the project:

```

```

### 2. Create a virtual environment:

```
python -m venv lizweb_env
lizweb_env\Scripts\activate
```

### 3. Copy the project folder to your preferred location and enter it:

```
cd photo_hire_system
```

### 4. Install dependencies:

```
pip install -r requirements.txt
```

(Installs Django, Pillow, and Requests)

### 6. Run database migrations:

```
python manage.py makemigrations accounts
python manage.py makemigrations equipment
python manage.py makemigrations bookings
python manage.py makemigrations payments
python manage.py migrate
```

### 7. Load sample data (creates users + equipment with real images):

```
python seed_data.py
```

### 8. Start the server:

```
python manage.py runserver
```

### 9. Open your browser:

```
http://127.0.0.1:8000
```

---

## 👤 Default Login Credentials

| Role     | Username  | Password    |
| -------- | --------- | ----------- |
| Admin    | admin     | admin123    |
| Staff    | staff1    | staff123    |
| Customer | customer1 | customer123 |

---

## 📁 Project Structure

```
photo_hire_system/
├── liz_web/              # Main Django project config
│   ├── settings.py       # All settings (DB, static, M-Pesa config)
│   ├── urls.py           # Root URL routing
│   └── wsgi.py
├── accounts/             # User management (3 roles)
│   ├── models.py         # Custom User model
│   ├── views.py          # Login, register, profile, user management
│   ├── decorators.py     # @admin_required, @staff_required
│   └── templatetags/     # Template filters for role checks
├── equipment/            # Equipment catalog
│   ├── models.py         # Category, Equipment
│   ├── views.py          # Browse, CRUD, manage
│   └── forms.py
├── bookings/             # Booking & hire tracking
│   ├── models.py         # Booking model with full lifecycle
│   ├── views.py          # Create, issue, return, cancel, overdue
│   └── dashboard_views.py # Role-based dashboards
├── payments/             # Payment processing
│   ├── models.py         # Payment records (M-Pesa, Card)
│   ├── mpesa.py          # Real Daraja API integration (STK Push + Query)
│   ├── views.py          # Payment processing, AJAX endpoints, finance reports
│   └── forms.py
├── templates/            # HTML templates
│   ├── base.html         # Main layout
│   ├── home.html         # Landing page
│   ├── accounts/         # Auth templates
│   ├── equipment/        # Catalog templates
│   ├── bookings/         # Booking templates
│   ├── payments/         # Payment templates
│   └── dashboard/        # Dashboard templates (admin/staff/customer)
├── static/
│   ├── css/style.css     # Custom styles
│   └── js/main.js
├── seed_data.py          # Sample data loader
├── manage.py
└── requirements.txt
```
