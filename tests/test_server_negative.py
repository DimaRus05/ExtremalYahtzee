import pytest
from src.app import app as flask_app


@pytest.fixture()
def client():
    flask_app.config.update({"TESTING": True, "SECRET_KEY": "test-key"})
    with flask_app.test_client() as c:
        yield c


def test_join_nonexistent_game(client):
    rv = client.post("/join_game", json={"game_id": "no-such", "player_name": "X"})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["success"] is False
    assert "Игра не найдена" in data["error"]


def create_started_game_two_clients():
    c1 = flask_app.test_client()
    c2 = flask_app.test_client()

    rv = c1.post("/create_game", json={"max_players": 4, "max_rounds": 1})
    gid = rv.get_json()["game_id"]

    assert c1.post("/join_game", json={"game_id": gid, "player_name": "Alice"}).get_json()["success"]
    assert c2.post("/join_game", json={"game_id": gid, "player_name": "Bob"}).get_json()["success"]

    assert c1.post(f"/game/{gid}/ready", json={}).get_json()["success"]
    st = c2.post(f"/game/{gid}/ready", json={}).get_json()
    assert st["success"] is True
    assert st["game_state"]["status"] == "active"
    return gid, c1, c2


def test_duplicate_player_name(client):
    rv = client.post("/create_game", json={"max_players": 4, "max_rounds": 1})
    gid = rv.get_json()["game_id"]
    assert client.post("/join_game", json={"game_id": gid, "player_name": "Same"}).get_json()["success"]
    r2 = client.post("/join_game", json={"game_id": gid, "player_name": "Same"})
    data2 = r2.get_json()
    assert data2["success"] is False
    assert "уже существует" in data2["error"]


def test_reroll_and_end_turn_wrong_player():
    gid, c1, c2 = create_started_game_two_clients()

    # Determine current player by state from each client
    st1 = c1.get(f"/game/{gid}/state").get_json()
    players = st1["players"]
    alice_current = any(p["name"] == "Alice" and p["is_current"] for p in players)

    # Choose the other client to attempt action while not current
    wrong_client = c2 if alice_current else c1

    r = wrong_client.post(f"/game/{gid}/reroll", json={"dice_to_reroll": [0]})
    assert r.status_code == 200
    jr = r.get_json()
    assert jr["success"] is False
    assert "Не удалось" in jr["error"]

    r = wrong_client.post(f"/game/{gid}/end_turn", json={})
    assert r.status_code == 200
    jr = r.get_json()
    assert jr["success"] is False
    assert "Не удалось" in jr["error"]
