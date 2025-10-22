import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time

@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_homepage_loads(driver):
    driver.get("http://127.0.0.1:5000/")
    
    # Проверяем заголовок
    assert "Покер на костях" in driver.title
    
    # Ждём появления кнопки "Создать игру"
    create_btn = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "create-btn"))
    )
    assert create_btn.is_displayed()

def test_create_game_and_join(driver):
    driver.get("http://127.0.0.1:5000/")
    name_input = driver.find_element(By.ID, "create-player-name")
    name_input.send_keys("Игрок1")
    driver.find_element(By.ID, "max-players").send_keys("2")
    driver.find_element(By.ID, "max-rounds").send_keys("1")
    driver.find_element(By.ID, "create-form").submit()
    time.sleep(1)  # ждем редирект
    assert "game" in driver.current_url

def test_second_player_join(driver):
    # Второй игрок подключается
    driver2 = webdriver.Chrome(options=Options().add_argument("--headless"))
    driver2.get("http://127.0.0.1:5000/")
    game_id = driver.find_element(By.ID, "game-id").get_attribute("value")
    name_input = driver2.find_element(By.ID, "player-name")
    name_input.send_keys("Игрок2")
    game_input = driver2.find_element(By.ID, "game-id")
    game_input.send_keys(game_id)
    driver2.find_element(By.ID, "join-form").submit()
    time.sleep(1)
    assert "game" in driver2.current_url
    driver2.quit()

def test_player_turn_actions(driver):
    # Предполагаем, что Игрок1 ходит
    reroll_btn = driver.find_element(By.ID, "reroll-btn")
    end_turn_btn = driver.find_element(By.ID, "end-turn-btn")
    dice = driver.find_elements(By.CLASS_NAME, "die")
    
    # Выбираем первую кость и делаем переброс
    dice[0].click()
    reroll_btn.click()
    time.sleep(1)
    
    # Завершаем ход
    end_turn_btn.click()
    time.sleep(1)
    
    # Проверяем, что ход завершен и кости обновились
    dice_new = driver.find_elements(By.CLASS_NAME, "die")
    assert dice_new != dice