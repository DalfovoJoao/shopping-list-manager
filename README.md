# Shopping List Manager 🛒

A beginner-friendly shopping list web app built with **Python, Flask, HTML, CSS, and SQLite**.

## Features

- Create an account and sign in.
- Create different shopping lists for different stores.
- Add products with a name, optional barcode, quantity, and price.
- Calculate subtotals and the total shopping cost automatically.
- Remove items from a shopping list.
- Keep each user's lists separate.

## How to run

1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python app.py
   ```

5. Open **http://127.0.0.1:5000** in your browser.

The database is created automatically in `instance/shopping.sqlite3`.

## Project structure

```text
shopping-list-manager/
├── app.py
├── database.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── auth.html
│   ├── lists.html
│   └── details.html
├── static/style.css
├── tests/test_database.py
└── README.md
```

## Learning goals

Python functions, web routes, forms, SQL queries, relational databases, user sessions, input validation, and basic project organization.

## Project background and credits

This is a **new implementation**, based on the general learning goals of the university exercise [Algorithms and Programming — Shopping List](https://github.com/felipebrandt/ads_algoritmos_e_programacao), provided as a teaching project by Felipe Brandt. It does not copy the original repository's source code. The HTML, Python logic, database schema, and styles here were written independently for this portfolio version.

## Limitations

This is a learning exercise, **not a production-ready application**. Set a random `SECRET_KEY` environment variable before any deployment, disable the Flask debugger, and add CSRF protection, rate limits, secure cookie configuration, and further security reviews. Use fake data and test accounts only. Barcode scanning via a camera is **not implemented** in this version; the barcode can be entered manually.
