import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from src.app import app as flask_app


@pytest.fixture()
def client():
    flask_app.config.update({"TESTING": True, "SECRET_KEY": "test-key"})
    with flask_app.test_client() as c:
        yield c


def test_join_requires_fields(client):
    # Missing player_name
    rv = client.post("/join_game", json={"game_id": "x"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["success"] is False

    # Missing game_id
    rv = client.post("/join_game", json={"player_name": "X"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["success"] is False


def test_reroll_end_turn_require_session(client):
    # Create a new game but don't join -> no session
    rv = client.post("/create_game", json={"max_players": 4, "max_rounds": 1})
    gid = rv.get_json()["game_id"]

    r = client.post(f"/game/{gid}/reroll", json={"dice_to_reroll": [0]})
    assert r.status_code == 200
    jr = r.get_json()
    assert jr["success"] is False
    assert "авторизован" in jr["error"]

    r = client.post(f"/game/{gid}/end_turn", json={})
    assert r.status_code == 200
    jr = r.get_json()
    assert jr["success"] is False
    assert "авторизован" in jr["error"]


def test_game_page_guards():
    c = flask_app.test_client()
    # No such game -> 404
    resp = c.get("/game/nope")
    assert resp.status_code == 404

    # Create and join
    gid = c.post("/create_game", json={"max_players": 2, "max_rounds": 1}).get_json()["game_id"]
    c.post("/join_game", json={"game_id": gid, "player_name": "A"})

    # Access OK
    ok = c.get(f"/game/{gid}")
    assert ok.status_code == 200

    # Another client without session gets 403
    c2 = flask_app.test_client()
    resp2 = c2.get(f"/game/{gid}")
    assert resp2.status_code == 403


def test_leave_clears_session_and_removes_player():
    c = flask_app.test_client()
    gid = c.post("/create_game", json={"max_players": 2, "max_rounds": 1}).get_json()["game_id"]
    j = c.post("/join_game", json={"game_id": gid, "player_name": "A"}).get_json()
    assert j["success"] is True
    pid = j["player_id"]

    # Ensure player present
    st = c.get(f"/game/{gid}/state").get_json()
    assert any(p["id"] == pid for p in st["players"])

    # Leave
    r = c.post(f"/game/{gid}/leave", json={})
    assert r.get_json()["success"] is True

    # Now session cleared -> get_game_state still works but without session
    st2 = c.get(f"/game/{gid}/state").get_json()
    # And player removed from game
    assert all(p["id"] != pid for p in st2["players"])
