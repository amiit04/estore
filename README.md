# E-Store

A modern, modular e-commerce web application built with Django. E-Store provides user authentication, product catalog, shopping cart, checkout, and a clean admin interface for managing products and site settings.

---

## 📦 Features

- **User Accounts**  
  - Registration, login/logout, password reset  
  - Profile management (via the `account` app)

- **Product Catalog**  
  - Category-based listing, search, and detail pages  
  - Media uploads for product images (`uploads/`)  
  - Rich admin management in the Django admin

- **Shopping Cart & Checkout** (`shop` app)  
  - Add/remove items, update quantities  
  - Order placement and simple order history  

- **Site Settings** (`site_settings` app)  
  - Manage site-wide configuration (e.g. store name, logo, contact info)

- **Core & Layout** (`core` app)  
  - Home page, footer, common templates and context processors  
  - Global static assets (SCSS, CSS, JS in `static/`)

---

## 🛠️ Tech Stack

- **Python**: 3.11.3  
- **Django**: 4.1  
- **Database**: SQLite (default; easy to switch to PostgreSQL, MySQL, etc.)  
- **Front-end**: HTML5, SCSS, vanilla JavaScript  
- **Dependencies** (see `requirements.txt`)
---

## 🚀 Quick Start

1. **Clone the repo**  
    ```bash
    git clone https://github.com/amiit04/estore.git
    cd estore
    ```

2. **Create & activate virtual environment**

   ```bash
   python3 -m venv .env
   source .env/bin/activate  # macOS/Linux
   .env\Scripts\activate     # Windows
   ```

3. **Install Python dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Then edit .env to set SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.
   ```

5. **Apply migrations & create a superuser**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Collect static files**

   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   Open [http://localhost:8000/](http://localhost:8000/) in your browser.

---

## 🗂️ Project Structure

```
estore/
├── account/          # User auth & profile
├── core/             # Home page, global templates, context processors
├── products/         # Product models, views, templates
├── shop/             # Cart, orders, checkout
├── site_settings/    # Site-wide configuration models
├── static/           # CSS, SCSS, JS, images
├── templates/        # Base & app-specific templates
├── uploads/          # Media uploads (product images, etc.)
├── manage.py
├── requirements.txt
└── db.sqlite3        # Development database (gitignored in production)
```

---

## 🤝 Contributing

1. Fork this repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Open a Pull Request

> Built with ❤️ and [Django](https://www.djangoproject.com/)