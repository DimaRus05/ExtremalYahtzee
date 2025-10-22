import pytest

from src.core.game_logic import DicePokerGame, Combination, GameManager


def make_game(players=2, max_rounds=1):
    gm = GameManager()
    game_id = gm.create_game(max_players=4, max_rounds=max_rounds)
    game = gm.get_game(game_id)
    ids = [game.add_player(f"P{i}") for i in range(players)]
    for pid in ids:
        game.set_player_ready(pid)
    assert game.start_game() is True
    return game, ids


def test_can_start_with_two_ready_players():
    game, ids = make_game(players=2, max_rounds=1)
    state = game.get_game_state(ids[0])
    assert state["status"] == "active"
    assert len(state["players"]) == 2
    assert state["current_turn"]["roll"] and len(state["current_turn"]["roll"]) == 5


def test_reroll_limits_and_indices_do_not_crash():
    game, ids = make_game(players=2, max_rounds=1)
    p0 = ids[0]
    # First reroll
    assert game.reroll_dice(p0, [0, 1]) is True
    # Second reroll
    assert game.reroll_dice(p0, [2]) is True
    # Third reroll should be rejected
    assert game.reroll_dice(p0, [3, 4]) is False


def test_end_turn_records_history_and_moves_to_next_player():
    game, ids = make_game(players=2, max_rounds=1)
    p0 = ids[0]
    assert game.end_turn(p0) is True
    # One turn stored
    assert len(game.turns_history) == 1
    # Score of player 0 increased (HIGH_DIE at least 1)
    assert game.players[p0].score >= 1
    # It should now be player 1's turn
    assert game.get_current_player().id == ids[1]


def test_round_completion_and_winner():
    game, ids = make_game(players=2, max_rounds=1)
    # Player 0 ends
    assert game.end_turn(ids[0]) is True
    # Player 1 ends -> game should complete (max_rounds=1)
    assert game.end_turn(ids[1]) is True
    assert game.status.value == "completed"
    state = game.get_game_state(ids[0])
    assert state["winner"] is not None
    assert set(state["winner"].keys()) == {"id", "name", "score"}


def test_evaluate_combinations_direct():
    gm = GameManager()
    gid = gm.create_game()
    game = gm.get_game(gid)

    assert game._evaluate_combination([6, 6, 6, 6, 6]) == Combination.FIVE_OF_A_KIND
    assert game._evaluate_combination([2, 2, 2, 2, 5]) == Combination.FOUR_OF_A_KIND
    assert game._evaluate_combination([3, 3, 3, 5, 5]) == Combination.FULL_HOUSE
    assert game._evaluate_combination([1, 2, 3, 4, 5]) == Combination.STRAIGHT
    assert game._evaluate_combination([2, 3, 4, 5, 6]) == Combination.STRAIGHT
    assert game._evaluate_combination([2, 2, 2, 4, 5]) == Combination.THREE_OF_A_KIND
    assert game._evaluate_combination([1, 1, 3, 3, 5]) == Combination.TWO_PAIRS
    assert game._evaluate_combination([6, 6, 2, 3, 4]) == Combination.ONE_PAIR
    assert game._evaluate_combination([1, 3, 4, 5, 6]) == Combination.HIGH_DIE
