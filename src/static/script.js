class PokerDiceGame {
    constructor() {
        this.gameId = null;
        this.playerId = null;
        this.playerName = null;
        this.pollInterval = null;
        this.currentSelectedDice = [];
        this.currentRerolls = 0;
        this.isInteractive = false;
        
        this.initializeEventListeners();
        this.initializeGamePage();
    }
    
    initializeEventListeners() {
        // Форма присоединения
        document.getElementById('join-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.joinGame();
        });
        
        // Форма создания игры
        document.getElementById('create-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.createGame();
        });
        
        // Игровые кнопки
        document.getElementById('ready-btn')?.addEventListener('click', () => this.setReady());
        document.getElementById('reroll-btn')?.addEventListener('click', () => this.rerollDice());
        document.getElementById('end-turn-btn')?.addEventListener('click', () => this.endTurn());
        document.getElementById('leave-game')?.addEventListener('click', () => this.leaveGame());
        document.getElementById('new-game-btn')?.addEventListener('click', () => window.location.reload());
    }
    
    initializeGamePage() {
        // Если мы на странице игры, запускаем опрос состояния
        if (window.location.pathname.includes('/game/')) {
            this.gameId = window.location.pathname.split('/').pop();
            
            // Получаем данные из sessionStorage
            this.playerId = sessionStorage.getItem('playerId');
            this.playerName = sessionStorage.getItem('playerName');
            
            if (this.gameId && this.playerId) {
                console.log('Initializing game page for game:', this.gameId, 'player:', this.playerId);
                this.startPolling();
            } else {
                console.error('Missing gameId or playerId');
            }
        }
    }
    
    async createGame() {
        const playerName = document.getElementById('create-player-name').value;
        const maxPlayers = document.getElementById('max-players').value;
        const maxRounds = document.getElementById('max-rounds').value;
        
        if (!playerName.trim()) {
            this.showMessage('Введите имя игрока', 'error');
            return;
        }
        
        try {
            const response = await fetch('/create_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    max_players: parseInt(maxPlayers), 
                    max_rounds: parseInt(maxRounds) 
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.gameId = data.game_id;
                // Сохраняем в sessionStorage
                sessionStorage.setItem('playerName', playerName);
                await this.joinGameWithId(playerName);
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка соединения', 'error');
        }
    }
    
    async joinGame() {
        const gameId = document.getElementById('game-id').value;
        const playerName = document.getElementById('player-name').value;
        
        if (!gameId.trim() || !playerName.trim()) {
            this.showMessage('Заполните все поля', 'error');
            return;
        }
        
        this.gameId = gameId;
        await this.joinGameWithId(playerName);
    }
    
    async joinGameWithId(playerName) {
        try {
            const response = await fetch('/join_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    game_id: this.gameId, 
                    player_name: playerName 
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.playerId = data.player_id;
                this.playerName = playerName;
                
                // Сохраняем в sessionStorage
                sessionStorage.setItem('playerId', this.playerId);
                sessionStorage.setItem('playerName', this.playerName);
                
                window.location.href = `/game/${this.gameId}`;
            } else {
                this.showMessage(data.error, 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка соединения', 'error');
        }
    }
    
    async setReady() {
        try {
            const response = await fetch(`/game/${this.gameId}/ready`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Player ready, game started:', data.game_started);
                if (data.game_started) {
                    this.startPolling();
                }
                this.updateGameState(data.game_state);
            } else {
                console.error('Failed to set ready:', data.error);
            }
        } catch (error) {
            console.error('Error setting ready:', error);
        }
    }
    
    startPolling() {
        console.log('Starting game state polling...');
        
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        
        // Первый запрос сразу
        this.updateGameStateFromServer();
        
        // Затем каждые 2 секунды
        this.pollInterval = setInterval(() => {
            this.updateGameStateFromServer();
        }, 2000);
    }
    
    async updateGameStateFromServer() {
        try {
            const response = await fetch(`/game/${this.gameId}/state`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const gameState = await response.json();
            
            if (gameState.error) {
                console.error('Game error:', gameState.error);
                this.showMessage(`Ошибка игры: ${gameState.error}`, 'error');
                return;
            }
            
            this.updateGameState(gameState);
            
        } catch (error) {
            console.error('Error fetching game state:', error);
        }
    }
    
    updateGameState(gameState) {
        this.updatePlayersList(gameState.players);
        this.updateGameInfo(gameState);
        this.updateGameControls(gameState);
        this.updateDiceArea(gameState);
        
        if (gameState.status === 'completed') {
            console.log('Game completed, stopping polling');
            if (this.pollInterval) {
                clearInterval(this.pollInterval);
                this.pollInterval = null;
            }
            this.showResults(gameState);
        }
    }
    
    updatePlayersList(players) {
        const playersList = document.getElementById('players-list');
        if (!playersList) return;
        
        playersList.innerHTML = players.map(player => {
            const isCurrent = player.is_current;
            const isYou = player.id === this.playerId;
            let classes = 'player-item';
            
            if (isCurrent) classes += ' current';
            if (isYou) classes += ' you';
            
            return `
                <div class="${classes}">
                    <span>${player.name} ${isCurrent ? '🎲' : ''} ${isYou ? '(Вы)' : ''}</span>
                    <span class="player-score">${player.score}</span>
                </div>
            `;
        }).join('');
    }
    
    updateGameInfo(gameState) {
        const roundInfo = document.getElementById('round-info');
        const gameStatus = document.getElementById('game-status');
        
        if (roundInfo) {
            roundInfo.textContent = `Раунд: ${gameState.current_round}/${gameState.max_rounds}`;
        }
        
        if (gameStatus) {
            const statusText = {
                'waiting': '⏳ Ожидание игроков',
                'active': '🎮 Идет игра',
                'completed': '🏁 Игра завершена'
            };
            gameStatus.textContent = `Статус: ${statusText[gameState.status] || gameState.status}`;
        }
    }
    
    updateGameControls(gameState) {
        const lobbyControls = document.getElementById('lobby-controls');
        const activeControls = document.getElementById('active-controls');
        const waitingControls = document.getElementById('waiting-controls');
        
        // Сначала скрываем все контролы
        if (lobbyControls) lobbyControls.style.display = 'none';
        if (activeControls) activeControls.style.display = 'none';
        if (waitingControls) waitingControls.style.display = 'none';
        
        if (gameState.status === 'waiting') {
            // Режим лобби - показываем кнопку "Готов"
            if (lobbyControls) {
                lobbyControls.style.display = 'block';
                
                // Проверяем, готов ли уже текущий игрок
                const currentPlayer = gameState.players.find(p => p.id === this.playerId);
                const readyBtn = document.getElementById('ready-btn');
                if (readyBtn && currentPlayer) {
                    if (currentPlayer.is_ready) {
                        readyBtn.textContent = 'Ожидание других игроков...';
                        readyBtn.disabled = true;
                    } else {
                        readyBtn.textContent = 'Готов к игре';
                        readyBtn.disabled = false;
                    }
                }
            }
        } 
        else if (gameState.status === 'active') {
            const currentPlayer = gameState.players.find(p => p.is_current);
            const isMyTurn = currentPlayer && currentPlayer.id === this.playerId;
            
            if (isMyTurn) {
                // Ход текущего игрока - показываем игровые контролы
                if (activeControls) activeControls.style.display = 'block';
                this.isInteractive = true;
            } else {
                // Ход другого игрока - показываем ожидание
                if (waitingControls) waitingControls.style.display = 'block';
                const currentPlayerName = document.getElementById('current-player-name');
                if (currentPlayerName && currentPlayer) {
                    currentPlayerName.textContent = currentPlayer.name;
                }
                this.isInteractive = false;
            }
            
            // Обновляем информацию о перебросах
            if (gameState.current_turn) {
                this.updateRerollsInfo(gameState.current_turn.remaining_rerolls);
            }
        }
        
        this.updateSelectionInfo();
    }
    
    updateDiceArea(gameState) {
        const diceContainer = document.getElementById('dice-container');
        const combinationDisplay = document.getElementById('combination-display');
        
        if (gameState.current_turn && gameState.current_turn.roll) {
            this.renderDice(
                gameState.current_turn.roll, 
                gameState.current_turn.remaining_rerolls, 
                this.isInteractive
            );
            
            if (combinationDisplay) {
                combinationDisplay.textContent = gameState.current_turn.combination || 'Определяется...';
            }
        } else {
            if (diceContainer) {
                diceContainer.innerHTML = '<div class="dice-placeholder">Ожидание броска...</div>';
            }
            if (combinationDisplay) {
                combinationDisplay.textContent = '-';
            }
        }
    }
    
    renderDice(dice, remainingRerolls, interactive = true) {
        const diceContainer = document.getElementById('dice-container');
        if (!diceContainer) return;
        
        if (!dice || dice.length === 0) {
            diceContainer.innerHTML = '<div class="dice-placeholder">Ожидание броска...</div>';
            return;
        }
        
        this.currentRerolls = remainingRerolls;
        this.isInteractive = interactive;
        
        // Если это не наш ход, сбрасываем выбор костей
        if (!interactive) {
            this.currentSelectedDice = [];
        }
        
        diceContainer.innerHTML = dice.map((value, index) => {
            const isSelected = this.currentSelectedDice.includes(index);
            const canSelect = interactive && remainingRerolls > 0;
            
            const classes = [
                'die',
                isSelected ? 'selected' : '',
                !canSelect ? 'disabled' : ''
            ].filter(Boolean).join(' ');
            
            return `
                <div class="${classes}" 
                     data-index="${index}"
                     onclick="game.handleDieClick(${index})">
                    ${value}
                </div>
            `;
        }).join('');
        
        this.updateSelectionInfo();
        this.updateRerollButton();
    }
    
    handleDieClick(index) {
        console.log('Die clicked:', index, 'Interactive:', this.isInteractive, 'Rerolls left:', this.currentRerolls);
        
        if (!this.isInteractive || this.currentRerolls === 0) {
            console.log('Dice selection disabled');
            return;
        }
        
        this.toggleDie(index);
    }
    
    toggleDie(index) {
        const position = this.currentSelectedDice.indexOf(index);
        
        if (position === -1) {
            // Добавляем кость в выбранные
            this.currentSelectedDice.push(index);
            console.log('Die selected:', index, 'Selected dice:', this.currentSelectedDice);
        } else {
            // Убираем кость из выбранных
            this.currentSelectedDice.splice(position, 1);
            console.log('Die deselected:', index, 'Selected dice:', this.currentSelectedDice);
        }
        
        // Обновляем отображение костей
        this.updateDiceSelection();
        
        // Обновляем информацию о выборе и кнопках
        this.updateSelectionInfo();
        this.updateRerollButton();
    }
    
    updateDiceSelection() {
        const diceElements = document.querySelectorAll('.die');
        diceElements.forEach((die, index) => {
            if (this.currentSelectedDice.includes(index)) {
                die.classList.add('selected');
            } else {
                die.classList.remove('selected');
            }
        });
    }
    
    updateSelectionInfo() {
        const selectedCount = document.getElementById('selected-count');
        if (selectedCount) {
            selectedCount.textContent = this.currentSelectedDice.length;
        }
    }
    
    updateRerollsInfo(remainingRerolls) {
        const rerollsLeft = document.getElementById('rerolls-left');
        if (rerollsLeft) {
            rerollsLeft.textContent = remainingRerolls;
        }
        this.currentRerolls = remainingRerolls;
        this.updateRerollButton();
    }
    
    updateRerollButton() {
        const rerollBtn = document.getElementById('reroll-btn');
        if (rerollBtn) {
            const canReroll = this.currentSelectedDice.length > 0 && this.currentRerolls > 0;
            rerollBtn.disabled = !canReroll;
        }
    }
    
    async rerollDice() {
        if (this.currentSelectedDice.length === 0) {
            alert('❌ Выберите кости для переброса! Кликните на кости, которые хотите перебросить.');
            return;
        }
        
        if (this.currentRerolls <= 0) {
            alert('❌ Не осталось перебросов!');
            return;
        }
        
        console.log('Rerolling dice:', this.currentSelectedDice);
        
        try {
            const response = await fetch(`/game/${this.gameId}/reroll`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dice_to_reroll: this.currentSelectedDice })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Dice rerolled successfully');
                this.updateGameState(data.game_state);
            } else {
                alert('❌ ' + (data.error || 'Ошибка при перебросе костей'));
            }
        } catch (error) {
            console.error('Error rerolling dice:', error);
            alert('❌ Ошибка соединения с сервером');
        }
    }
    
    async endTurn() {
        try {
            const response = await fetch(`/game/${this.gameId}/end_turn`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Turn ended successfully');
                this.currentSelectedDice = []; // Сбрасываем выбор после завершения хода
                this.updateGameState(data.game_state);
            } else {
                alert('❌ ' + (data.error || 'Ошибка при завершении хода'));
            }
        } catch (error) {
            console.error('Error ending turn:', error);
            alert('❌ Ошибка соединения с сервером');
        }
    }
    
    async leaveGame() {
        if (confirm('Вы уверены, что хотите покинуть игру?')) {
            try {
                await fetch(`/game/${this.gameId}/leave`, { method: 'POST' });
                // Очищаем sessionStorage
                sessionStorage.removeItem('playerId');
                sessionStorage.removeItem('playerName');
                window.location.href = '/';
            } catch (error) {
                console.error('Error leaving game:', error);
            }
        }
    }
    
    showResults(gameState) {
        const modal = document.getElementById('results-modal');
        const winnerInfo = document.getElementById('winner-info');
        const finalScores = document.getElementById('final-scores');
        
        if (modal && winnerInfo && finalScores) {
            winnerInfo.innerHTML = `
                <h3>🏆 Победитель: ${gameState.winner.name}</h3>
                <p>Счет: ${gameState.winner.score} очков</p>
            `;
            
            finalScores.innerHTML = `
                <h4>Итоговые результаты:</h4>
                ${gameState.players.map(player => `
                    <p><strong>${player.name}:</strong> ${player.score} очков</p>
                `).join('')}
            `;
            
            modal.style.display = 'flex';
        }
    }
    
    showMessage(message, type = 'info') {
        const messageEl = document.getElementById('message');
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = `message ${type}`;
            messageEl.style.display = 'block';
            
            setTimeout(() => {
                messageEl.style.display = 'none';
            }, 5000);
        }
    }
}

// Инициализация игры при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    window.game = new PokerDiceGame();
});