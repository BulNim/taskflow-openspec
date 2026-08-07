import os
import sys
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_taskflow.db"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from fastapi.testclient import TestClient

from app.core.db import Base, engine
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def signup(email="user@ex.com", password="password1"):
    r = client.post("/auth/signup", json={"email": email, "password": password})
    return r


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# --- Auth (spec: auth) ---

def test_signup_success():
    r = signup()
    assert r.status_code == 201
    assert "token" in r.json()


def test_signup_invalid_email():
    r = client.post("/auth/signup", json={"email": "not-an-email", "password": "password1"})
    assert r.status_code == 400


def test_signup_duplicate_email():
    signup()
    r = signup()
    assert r.status_code == 409
    assert r.json()["error"]["code"] == "EMAIL_TAKEN"


def test_signup_weak_password():
    r = client.post("/auth/signup", json={"email": "user2@ex.com", "password": "short"})
    assert r.status_code == 400


def test_login_success():
    signup()
    r = client.post("/auth/login", json={"email": "user@ex.com", "password": "password1"})
    assert r.status_code == 200
    assert r.json()["user"]["team_id"] is None


def test_login_invalid_credentials():
    signup()
    r = client.post("/auth/login", json={"email": "user@ex.com", "password": "wrongpass"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_unknown_email_same_error():
    r = client.post("/auth/login", json={"email": "nope@ex.com", "password": "password1"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_me_requires_token():
    r = client.get("/auth/me")
    assert r.status_code == 401


# --- Teams (spec: teams) ---

def _new_user_token(email):
    return signup(email).json()["token"]


def test_team_create_and_join():
    token_a = _new_user_token("leader@ex.com")
    r = client.post("/teams", json={"name": "Frontiers"}, headers=auth_headers(token_a))
    assert r.status_code == 201
    invite_code = r.json()["invite_code"]

    token_b = _new_user_token("member@ex.com")
    r2 = client.post("/teams/join", json={"invite_code": invite_code}, headers=auth_headers(token_b))
    assert r2.status_code == 200
    assert r2.json()["name"] == "Frontiers"


def test_join_invalid_format():
    token = _new_user_token("u1@ex.com")
    r = client.post("/teams/join", json={"invite_code": "bad"}, headers=auth_headers(token))
    assert r.status_code == 400


def test_join_nonexistent_code():
    token = _new_user_token("u1@ex.com")
    r = client.post("/teams/join", json={"invite_code": "ZZZZ-9999"}, headers=auth_headers(token))
    assert r.status_code == 404


def test_leave_and_rejoin_same_code():
    token_owner = _new_user_token("owner@ex.com")
    team = client.post("/teams", json={"name": "T1"}, headers=auth_headers(token_owner)).json()
    code = team["invite_code"]

    token_member = _new_user_token("m@ex.com")
    client.post("/teams/join", json={"invite_code": code}, headers=auth_headers(token_member))

    r = client.delete(f"/teams/{team['id']}/leave", headers=auth_headers(token_member))
    assert r.status_code == 200

    r2 = client.post("/teams/join", json={"invite_code": code}, headers=auth_headers(token_member))
    assert r2.status_code == 200


def test_get_team_info_returns_invite_code():
    token_owner = _new_user_token("owner2@ex.com")
    team = client.post("/teams", json={"name": "T2"}, headers=auth_headers(token_owner)).json()

    r = client.get(f"/teams/{team['id']}", headers=auth_headers(token_owner))
    assert r.status_code == 200
    assert r.json()["invite_code"] == team["invite_code"]


def test_non_member_forbidden():
    token_a = _new_user_token("a@ex.com")
    team = client.post("/teams", json={"name": "T1"}, headers=auth_headers(token_a)).json()

    token_b = _new_user_token("b@ex.com")
    r = client.get(f"/teams/{team['id']}/members", headers=auth_headers(token_b))
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"


# --- Kanban tasks (spec: kanban-tasks) ---

def _team_with_owner_and_member():
    token_owner = _new_user_token("owner@ex.com")
    team = client.post("/teams", json={"name": "T1"}, headers=auth_headers(token_owner)).json()
    token_member = _new_user_token("member@ex.com")
    client.post("/teams/join", json={"invite_code": team["invite_code"]}, headers=auth_headers(token_member))
    return team, token_owner, token_member


def test_task_create_and_list():
    team, token_owner, _ = _team_with_owner_and_member()
    r = client.post(f"/teams/{team['id']}/tasks", json={"title": "setup"}, headers=auth_headers(token_owner))
    assert r.status_code == 201
    assert r.json()["status"] == "TODO"

    r2 = client.get(f"/teams/{team['id']}/tasks", headers=auth_headers(token_owner))
    assert len(r2.json()) == 1


def test_status_change_requires_creator_or_owner():
    team, token_owner, token_member = _team_with_owner_and_member()
    task = client.post(f"/teams/{team['id']}/tasks", json={"title": "t"}, headers=auth_headers(token_owner)).json()

    r = client.patch(f"/tasks/{task['id']}/status", json={"status": "DOING"}, headers=auth_headers(token_member))
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "FORBIDDEN"

    r2 = client.patch(f"/tasks/{task['id']}/status", json={"status": "DOING"}, headers=auth_headers(token_owner))
    assert r2.status_code == 200


def test_delete_permission_matrix():
    team, token_owner, token_member = _team_with_owner_and_member()
    task_by_member = client.post(
        f"/teams/{team['id']}/tasks", json={"title": "member task"}, headers=auth_headers(token_member)
    ).json()

    # owner can delete member's task (override)
    r = client.delete(f"/tasks/{task_by_member['id']}", headers=auth_headers(token_owner))
    assert r.status_code == 200

    task2 = client.post(
        f"/teams/{team['id']}/tasks", json={"title": "owner task"}, headers=auth_headers(token_owner)
    ).json()
    # member cannot delete owner's task
    r2 = client.delete(f"/tasks/{task2['id']}", headers=auth_headers(token_member))
    assert r2.status_code == 403


def test_task_due_date_set_on_create():
    team, token_owner, _ = _team_with_owner_and_member()
    r = client.post(
        f"/teams/{team['id']}/tasks",
        json={"title": "with due date", "due_date": "2026-12-31"},
        headers=auth_headers(token_owner),
    )
    assert r.status_code == 201
    assert r.json()["due_date"] == "2026-12-31"


def test_task_due_date_default_null():
    team, token_owner, _ = _team_with_owner_and_member()
    r = client.post(f"/teams/{team['id']}/tasks", json={"title": "no due date"}, headers=auth_headers(token_owner))
    assert r.json()["due_date"] is None


def test_task_due_date_update_and_clear():
    team, token_owner, _ = _team_with_owner_and_member()
    task = client.post(f"/teams/{team['id']}/tasks", json={"title": "t"}, headers=auth_headers(token_owner)).json()

    r = client.put(
        f"/tasks/{task['id']}",
        json={"title": "t", "assignee_id": None, "due_date": "2026-01-15"},
        headers=auth_headers(token_owner),
    )
    assert r.status_code == 200
    assert r.json()["due_date"] == "2026-01-15"

    r2 = client.put(
        f"/tasks/{task['id']}",
        json={"title": "t", "assignee_id": None, "due_date": None},
        headers=auth_headers(token_owner),
    )
    assert r2.json()["due_date"] is None


def test_task_due_date_update_requires_permission():
    team, token_owner, token_member = _team_with_owner_and_member()
    task = client.post(f"/teams/{team['id']}/tasks", json={"title": "t"}, headers=auth_headers(token_owner)).json()

    r = client.put(
        f"/tasks/{task['id']}",
        json={"title": "t", "assignee_id": None, "due_date": "2026-01-15"},
        headers=auth_headers(token_member),
    )
    assert r.status_code == 403


def test_unassigned_filter():
    team, token_owner, _ = _team_with_owner_and_member()
    client.post(f"/teams/{team['id']}/tasks", json={"title": "unassigned"}, headers=auth_headers(token_owner))
    r = client.get(f"/teams/{team['id']}/tasks?filter=unassigned", headers=auth_headers(token_owner))
    assert len(r.json()) == 1
    assert r.json()[0]["assignee_id"] is None


# --- Chat (spec: chat) ---

def test_message_send_and_poll():
    team, token_owner, token_member = _team_with_owner_and_member()
    r = client.post(f"/teams/{team['id']}/messages", json={"content": "hi"}, headers=auth_headers(token_owner))
    assert r.status_code == 201

    r2 = client.get(f"/teams/{team['id']}/messages", headers=auth_headers(token_member))
    assert len(r2.json()) == 1

    since = r2.json()[0]["created_at"]
    r3 = client.get(f"/teams/{team['id']}/messages?since={since}", headers=auth_headers(token_member))
    assert r3.json() == []


def test_message_too_long():
    team, token_owner, _ = _team_with_owner_and_member()
    r = client.post(
        f"/teams/{team['id']}/messages", json={"content": "x" * 1001}, headers=auth_headers(token_owner)
    )
    assert r.status_code == 400


def test_message_delete_only_by_author():
    team, token_owner, token_member = _team_with_owner_and_member()
    msg = client.post(
        f"/teams/{team['id']}/messages", json={"content": "hi"}, headers=auth_headers(token_member)
    ).json()

    r = client.delete(f"/messages/{msg['id']}", headers=auth_headers(token_owner))
    assert r.status_code == 403
    assert r.json()["error"]["code"] == "NOT_OWNER"

    r2 = client.delete(f"/messages/{msg['id']}", headers=auth_headers(token_member))
    assert r2.status_code == 200


def test_no_message_loss_across_polls():
    team, token_owner, token_member = _team_with_owner_and_member()
    for i in range(5):
        client.post(f"/teams/{team['id']}/messages", json={"content": f"m{i}"}, headers=auth_headers(token_owner))

    r = client.get(f"/teams/{team['id']}/messages", headers=auth_headers(token_member))
    assert len(r.json()) == 5
