import sys
import os

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


import unittest
from src.core import DicePokerGame, Combination, GameStatus


class TestDicePokerGame(unittest.TestCase):
    def setUp(self):
        self.game = DicePokerGame(game_id="test-game")

    def test_add_player(self):
        player_id = self.game.add_player("Alice")
        self.assertIn(player_id, self.game.players)
        self.assertEqual(self.game.players[player_id].name, "Alice")

        # Проверка добавления второго игрока
        player_id2 = self.game.add_player("Bob")
        self.assertIn(player_id2, self.game.players)

        # Попытка добавить игрока с одинаковым именем
        with self.assertRaises(ValueError):
            self.game.add_player("Alice")

    def test_start_game_requires_ready_players(self):
        self.game.add_player("Alice")
        self.game.add_player("Bob")

        # Игроки не готовы
        self.assertFalse(self.game.start_game())

        # Отмечаем игроков как ready
        for pid in self.game.players:
            self.game.set_player_ready(pid)

        self.assertTrue(self.game.start_game())
        self.assertEqual(self.game.status, GameStatus.ACTIVE)

    def test_roll_and_reroll_dice(self):
        p1 = self.game.add_player("Alice")
        p2 = self.game.add_player("Bob")
        for pid in self.game.players:
            self.game.set_player_ready(pid)
        self.game.start_game()

        player = self.game.get_current_player()
        self.assertEqual(player.id, p1)

        original_roll = self.game.current_roll.copy()
        # Перебрасываем первые две кости
        success = self.game.reroll_dice(player.id, [0, 1])
        self.assertTrue(success)
        self.assertNotEqual(original_roll[:2], self.game.current_roll[:2])

        # Остаток перебросов уменьшается
        self.assertEqual(self.game.remaining_rerolls, 1)

    def test_end_turn_and_score(self):
        p1 = self.game.add_player("Alice")
        p2 = self.game.add_player("Bob")
        for pid in self.game.players:
            self.game.set_player_ready(pid)
        self.game.start_game()

        player = self.game.get_current_player()
        # Завершаем ход
        success = self.game.end_turn(player.id)
        self.assertTrue(success)

        # Проверяем, что счет обновился
        self.assertGreaterEqual(player.score, 0)

        # Переход к следующему игроку
        next_player = self.game.get_current_player()
        self.assertNotEqual(player.id, next_player.id)

    def test_game_completion(self):
        # Создаем игру с 1 раундом и 2 игроками
        game = DicePokerGame("g2", max_rounds=1)
        p1 = game.add_player("Alice")
        p2 = game.add_player("Bob")
        for pid in game.players:
            game.set_player_ready(pid)
        game.start_game()

        # Завершаем ходы всех игроков
        for _ in range(2):
            current = game.get_current_player()
            game.end_turn(current.id)

        self.assertEqual(game.status, GameStatus.COMPLETED)
        winner_state = game.get_game_state()
        self.assertIn("winner", winner_state)
        self.assertIsNotNone(winner_state["winner"])


if __name__ == "__main__":
    unittest.main()
