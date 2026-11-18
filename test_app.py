import base64
import sqlite3

import pytest

from app import create_app


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


ADMIN_PW = "test-admin-pw"


@pytest.fixture
def client(db_path, monkeypatch):
    # Pin the password so a real .env loaded by pipenv never leaks into tests.
    monkeypatch.setenv("ADMIN_PASSWORD", ADMIN_PW)
    app = create_app(str(db_path))
    app.config["TESTING"] = True
    return app.test_client()


def basic_auth(password, user="admin"):
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def rows(db_path):
    with sqlite3.connect(db_path) as conn:
        return conn.execute("SELECT name, email, major FROM signups").fetchall()


def test_form_page_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'name="email"' in resp.data


def test_signup_saves_and_redirects(client, db_path):
    resp = client.post(
        "/", data={"name": "Ada", "email": "ada@example.com", "major": "Math"}
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/thanks")
    assert rows(db_path) == [("Ada", "ada@example.com", "Math")]


def test_missing_field_rejected(client, db_path):
    resp = client.post("/", data={"name": "Ada", "email": "", "major": "Math"})
    assert resp.status_code == 400
    assert b"Please fill in every field" in resp.data
    assert rows(db_path) == []


def test_thanks_page(client):
    resp = client.get("/thanks")
    assert resp.status_code == 200
    assert b"Thank you" in resp.data


def add_signups(client):
    client.post("/", data={"name": "Ada", "email": "ada@example.com", "major": "Math"})
    client.post(
        "/", data={"name": "Grace", "email": "grace@example.com", "major": "CS"}
    )


def test_admin_requires_password(client):
    resp = client.get("/admin")
    assert resp.status_code == 401
    assert resp.headers["WWW-Authenticate"].startswith("Basic")


def test_admin_rejects_wrong_password(client):
    add_signups(client)
    resp = client.get("/admin", headers=basic_auth("wrong"))
    assert resp.status_code == 401
    assert b"ada@example.com" not in resp.data


def test_admin_lists_every_signup(client):
    add_signups(client)
    resp = client.get("/admin", headers=basic_auth(ADMIN_PW))
    assert resp.status_code == 200
    for value in [b"Ada", b"ada@example.com", b"Math",
                  b"Grace", b"grace@example.com", b"CS"]:
        assert value in resp.data
    assert b"2 signups" in resp.data


def test_admin_empty_list(client):
    resp = client.get("/admin", headers=basic_auth(ADMIN_PW))
    assert resp.status_code == 200
    assert b"No signups yet" in resp.data


def test_admin_escapes_html(client):
    client.post(
        "/", data={"name": "<script>x</script>", "email": "a@b.c", "major": "Art"}
    )
    resp = client.get("/admin", headers=basic_auth(ADMIN_PW))
    assert b"<script>x</script>" not in resp.data
    assert b"&lt;script&gt;" in resp.data


def test_admin_locked_when_password_unset(db_path, monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    app = create_app(str(db_path))
    client = app.test_client()
    assert client.get("/admin", headers=basic_auth("")).status_code == 401
    assert client.get("/admin", headers=basic_auth("None")).status_code == 401
