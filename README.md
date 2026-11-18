# trip-signup

A small Flask app where students register interest in a study abroad trip.
Students fill in a form with their name, email and major. Organizers can see every
signup on a password-protected admin page.

## Features

- **Signup form** (`/`): collects name, email and major. All three are required.
  An incomplete form is rejected with a message.
- **Thank-you page** (`/thanks`): shown after a successful signup.
- **Admin page** (`/admin`): a table of every signup in the order received,
  protected by a password.

## Requirements

- Python 3.14
- [Pipenv](https://pipenv.pypa.io/)

## Setup

1. Install the dependencies (add `--dev` to include pytest for running tests):

   ```sh
   pipenv install --dev
   ```

2. Create a `.env` file in the project root with the admin password:

   ```
   ADMIN_PASSWORD=choose-a-strong-password
   ```

   `pipenv run` loads this file automatically. Never commit `.env`; it is
   already listed in `.gitignore`.

## Running the app

```sh
pipenv run flask run --debug
```

Then open <http://127.0.0.1:5000>.

Signups are stored in a SQLite database, `signups.db`, which is created
automatically on first run. It holds applicant data, so don't commit it (it is
also in `.gitignore`).

## Admin page

Go to <http://127.0.0.1:5000/admin>. Your browser will ask you to log in. Enter
any username and the `ADMIN_PASSWORD` from your `.env` file.

- If `ADMIN_PASSWORD` isn't set, the admin page refuses everyone.
- The page uses HTTP Basic Auth, which sends the password essentially
  unencrypted over plain HTTP. Serve the app over HTTPS if it runs anywhere
  other than your own machine.

## Running the tests

```sh
pipenv run pytest -q
```

Each test uses its own temporary database and a test-only admin password, so
running the tests never touches `signups.db` or your real `.env` password.

## Project layout

```
app.py              Flask app factory (create_app) and routes
templates/
  base.html         Shared layout (Bootstrap CSS)
  signup.html       Signup form
  thanks.html       Confirmation page
  admin.html        Admin list of signups
test_app.py         pytest test suite
Pipfile             Dependencies (Flask; pytest for development)
Pipfile.lock        Locked dependency versions
```

## Notes for contributors

- Use the built-in `sqlite3` module (no ORM) and only parameterized queries
  (`?` placeholders).
- Never print or log applicant emails.
- Plain HTML templates and CSS only; no JavaScript frameworks.
- Add or update a test for every change, and run the suite before submitting.
