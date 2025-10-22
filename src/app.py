from flask import Flask, render_template, request, jsonify, session
from core import GameManager

app = Flask(__name__)
app.secret_key = "poker-dice-secret-key-2024"

# Инициализация менеджера игр
game_manager = GameManager()


@app.route("/")
def index():
    """Главная страница"""
    return render_template("index.html")


@app.route("/create_game", methods=["POST"])
def create_game():
    """Создает новую игру"""
    data = request.get_json()
    max_players = data.get("max_players", 4)
    max_rounds = data.get("max_rounds", 3)

    try:
        game_id = game_manager.create_game(max_players, max_rounds)
        return jsonify({"success": True, "game_id": game_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/join_game", methods=["POST"])
def join_game():
    """Присоединяет игрока к игре"""
    data = request.get_json()
    game_id = data.get("game_id")
    player_name = data.get("player_name")

    if not game_id or not player_name:
        return jsonify({"success": False, "error": "Неверные данные"})

    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({"success": False, "error": "Игра не найдена"})

    try:
        player_id = game.add_player(player_name)
        session["player_id"] = player_id
        session["game_id"] = game_id
        session["player_name"] = player_name

        return jsonify(
            {
                "success": True,
                "player_id": player_id,
                "game_state": game.get_game_state(player_id),
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/game/<game_id>")
def game_page(game_id):
    """Страница игры"""
    game = game_manager.get_game(game_id)
    if not game:
        return "Игра не найдена", 404

    player_id = session.get("player_id")
    if not player_id or player_id not in game.players:
        return "Игрок не найден в этой игре", 403

    return render_template("game.html", game_id=game_id)


@app.route("/game/<game_id>/state")
def get_game_state(game_id):
    """Возвращает текущее состояние игры"""
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({"error": "Игра не найдена"}), 404

    player_id = session.get("player_id")
    return jsonify(game.get_game_state(player_id))


@app.route("/game/<game_id>/ready", methods=["POST"])
def set_player_ready(game_id):
    """Отмечает игрока как готового"""
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({"success": False, "error": "Игра не найдена"})

    player_id = session.get("player_id")
    if not player_id or player_id not in game.players:
        return jsonify({"success": False, "error": "Игрок не найден"})

    # Устанавливаем игрока как готового
    game.set_player_ready(player_id)

    # Пытаемся начать игру, если все готовы
    game_started = game.start_game()

    return jsonify(
        {
            "success": True,
            "game_started": game_started,
            "game_state": game.get_game_state(player_id),
        }
    )


@app.route("/game/<game_id>/reroll", methods=["POST"])
def reroll_dice(game_id):
    """Перебрасывает выбранные кости"""
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({"success": False, "error": "Игра не найдена"})

    player_id = session.get("player_id")
    if not player_id:
        return jsonify({"success": False, "error": "Игрок не авторизован"})

    data = request.get_json()
    dice_to_reroll = data.get("dice_to_reroll", [])

    success = game.reroll_dice(player_id, dice_to_reroll)

    if success:
        return jsonify({"success": True, "game_state": game.get_game_state(player_id)})
    return jsonify({"success": False, "error": "Не удалось перебросить кости"})


@app.route("/game/<game_id>/end_turn", methods=["POST"])
def end_turn(game_id):
    """Завершает ход текущего игрока"""
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({"success": False, "error": "Игра не найдена"})

    player_id = session.get("player_id")
    if not player_id:
        return jsonify({"success": False, "error": "Игрок не авторизован"})

    success = game.end_turn(player_id)

    if success:
        return jsonify({"success": True, "game_state": game.get_game_state(player_id)})
    return jsonify({"success": False, "error": "Не удалось завершить ход"})


@app.route("/game/<game_id>/leave", methods=["POST"])
def leave_game(game_id):
    """Покидает игру"""
    game = game_manager.get_game(game_id)
    if game and "player_id" in session:
        player_id = session["player_id"]
        if player_id in game.players:
            del game.players[player_id]

    session.pop("player_id", None)
    session.pop("game_id", None)
    session.pop("player_name", None)

    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
