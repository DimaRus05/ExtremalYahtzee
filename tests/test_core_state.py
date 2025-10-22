import pytest

from src.core.game_logic import GameManager


def _start_two_player_game(max_rounds=2):
    gm = GameManager()
    gid = gm.create_game(max_players=4, max_rounds=max_rounds)
    game = gm.get_game(gid)
    p1 = game.add_player("A")
    p2 = game.add_player("B")
    game.set_player_ready(p1)
    game.set_player_ready(p2)
    assert game.start_game() is True
    return game, p1, p2


def test_remaining_rerolls_decrement_and_reset(monkeypatch):
    game, p1, _ = _start_two_player_game()

    # At start of turn should be 2
    assert game.remaining_rerolls == 2

    # Make deterministic reroll results
    monkeypatch.setattr("src.core.game_logic.random.randint", lambda a, b: 6)

    # One reroll decrements
    assert game.reroll_dice(p1, [0, 1]) is True
    assert game.remaining_rerolls == 1

    # Second reroll decrements to 0
    assert game.reroll_dice(p1, [2]) is True
    assert game.remaining_rerolls == 0

    # Third reroll blocked
    assert game.reroll_dice(p1, [3]) is False

    # End turn -> next player's turn resets rerolls to 2
    assert game.end_turn(p1) is True
    assert game.remaining_rerolls == 2


def test_add_player_duplicate_name_raises():
    gm = GameManager()
    gid = gm.create_game()
    game = gm.get_game(gid)
    game.add_player("Same")
    with pytest.raises(ValueError):
        game.add_player("Same")


def test_get_game_state_contains_expected_shape():
    game, p1, _ = _start_two_player_game(max_rounds=1)
    state = game.get_game_state(p1)
    assert set(state.keys()) >= {"game_id", "status", "current_round", "max_rounds", "players"}
    assert isinstance(state["players"], list) and len(state["players"]) == 2
    if state["status"] == "active":
        ct = state["current_turn"]
        assert set(ct.keys()) >= {"roll", "remaining_rerolls", "combination"}


def test_reroll_changes_only_selected_indices(monkeypatch):
    game, p1, _ = _start_two_player_game()
    before = list(game.current_roll)
    # Force reroll to set 6
    monkeypatch.setattr("src.core.game_logic.random.randint", lambda a, b: 6)
    assert game.reroll_dice(p1, [0, 4]) is True
    after = list(game.current_roll)
    for i in range(5):
        if i in (0, 4):
            assert after[i] == 6
        else:
            assert after[i] == before[i]
