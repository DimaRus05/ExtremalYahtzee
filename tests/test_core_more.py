import pytest

from src.core.game_logic import DicePokerGame, Combination, GameManager


def test_start_game_requires_two_players_and_all_ready():
    gm = GameManager()
    gid = gm.create_game()
    game = gm.get_game(gid)

    # Not enough players
    p1 = game.add_player("A")
    game.set_player_ready(p1)
    assert game.start_game() is False

    # Enough players but not all ready
    p2 = game.add_player("B")
    assert game.start_game() is False

    # All ready -> can start
    game.set_player_ready(p2)
    assert game.start_game() is True


def test_reroll_wrong_player_and_invalid_indices():
    gm = GameManager()
    gid = gm.create_game()
    game = gm.get_game(gid)
    p1 = game.add_player("A")
    p2 = game.add_player("B")
    game.set_player_ready(p1)
    game.set_player_ready(p2)
    assert game.start_game() is True

    # Wrong player tries to reroll
    other = p2 if game.get_current_player().id == p1 else p1
    assert game.reroll_dice(other, [0, 1]) is False

    # Valid player uses invalid indices (ignored) and valid index
    current = game.get_current_player().id
    before = list(game.current_roll)
    assert game.reroll_dice(current, [-1, 5, 10, 0]) is True
    after = list(game.current_roll)
    # Only index 0 can legally change
    assert before[1:] == after[1:]


def test_is_straight_requires_unique_values():
    gm = GameManager()
    gid = gm.create_game()
    game = gm.get_game(gid)
    # Duplicate breaks straight
    assert game._evaluate_combination([1, 2, 3, 4, 4]) != Combination.STRAIGHT


def test_score_table_values():
    gm = GameManager()
    gid = gm.create_game()
    game = gm.get_game(gid)

    cases = [
        ([6, 6, 6, 6, 6], Combination.FIVE_OF_A_KIND, 100),
        ([2, 2, 2, 2, 5], Combination.FOUR_OF_A_KIND, 40),
        ([3, 3, 3, 5, 5], Combination.FULL_HOUSE, 25),
        ([1, 2, 3, 4, 5], Combination.STRAIGHT, 20),
        ([4, 4, 4, 1, 2], Combination.THREE_OF_A_KIND, 15),
        ([1, 1, 3, 3, 5], Combination.TWO_PAIRS, 10),
        ([6, 6, 2, 3, 4], Combination.ONE_PAIR, 5),
        ([1, 3, 4, 5, 6], Combination.HIGH_DIE, 6),
    ]
    for dice, comb, points in cases:
        assert game._evaluate_combination(dice) == comb
        assert game._calculate_score(comb, dice) == points


def test_turn_order_multiple_players_and_rounds():
    gm = GameManager()
    gid = gm.create_game(max_rounds=2)
    game = gm.get_game(gid)
    ids = [game.add_player(n) for n in ("A", "B", "C")]
    for pid in ids:
        game.set_player_ready(pid)
    assert game.start_game() is True

    # There are 2 rounds * 3 players = 6 turns
    total_turns = 0
    while game.status.value != "completed":
        cur = game.get_current_player().id
        assert game.end_turn(cur) is True
        total_turns += 1

    assert total_turns == 6
    assert game.current_round == 3  # advanced past max_rounds


def test_game_manager_remove_game():
    gm = GameManager()
    gid = gm.create_game()
    assert gm.get_game(gid) is not None
    gm.remove_game(gid)
    assert gm.get_game(gid) is None
