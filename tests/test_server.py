import pytest
from src.app import app as flask_app


@pytest.fixture()
def client():
    flask_app.config.update({"TESTING": True, "SECRET_KEY": "test-key"})
    with flask_app.test_client() as c:
        yield c


def test_create_and_join_and_ready_flow(client):
    rv = client.post("/create_game", json={"max_players": 4, "max_rounds": 1})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["success"] is True
    game_id = data["game_id"]

    rv1 = client.post("/join_game", json={"game_id": game_id, "player_name": "Alice"})
    assert rv1.status_code == 200
    data1 = rv1.get_json()
    assert data1["success"] is True

    client2 = flask_app.test_client()

    rv2 = client2.post("/join_game", json={"game_id": game_id, "player_name": "Bob"})
    assert rv2.status_code == 200
    data2 = rv2.get_json()
    assert data2["success"] is True

    rv = client.post(f"/game/{game_id}/ready", json={})
    assert rv.status_code == 200
    d = rv.get_json()
    assert d["success"] is True
    assert d["game_started"] in (False, True)

    rv = client2.post(f"/game/{game_id}/ready", json={})
    assert rv.status_code == 200
    d2 = rv.get_json()
    assert d2["success"] is True
    assert d2["game_state"]["status"] == "active"

    rv = client.get(f"/game/{game_id}/state")
    assert rv.status_code == 200
    state = rv.get_json()
    assert state["status"] in ("active", "completed")
    if state["status"] == "active":
        assert state["current_turn"]["roll"]

    if any(p["is_current"] and p["name"] == "Alice" for p in state["players"]):
        rv = client.post(f"/game/{game_id}/reroll", json={"dice_to_reroll": [0, 1]})
        assert rv.status_code == 200
        r = rv.get_json()
        assert r["success"] is True

        rv = client.post(f"/game/{game_id}/end_turn", json={})
        assert rv.status_code == 200
        r = rv.get_json()
        assert r["success"] is True
