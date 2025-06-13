from types import SimpleNamespace
from bot import start, art_find

def test_start_authorized():
    message = SimpleNamespace(chat=SimpleNamespace(id=2042899865), text="/start")
    try:
        start(message)
        return True
    except Exception as e:
        print("Ошибка в test_start_authorized:", e)
        return False

def test_start_unauthorized():
    message = SimpleNamespace(chat=SimpleNamespace(id=111111111), text="/start")
    try:
        start(message)
        return False  
    except Exception as e:
        print("Ожидаемая ошибка в test_start_unauthorized:", e)
        return True

def test_art_find_valid():
    message = SimpleNamespace(chat=SimpleNamespace(id=2042899865), text="369880738")
    try:
        art_find(message)
        return True
    except Exception as e:
        print("Ошибка в test_art_find_valid:", e)
        return False

def test_art_find_invalid():
    message = SimpleNamespace(chat=SimpleNamespace(id=2042899865), text="000000000")
    try:
        art_find(message)
        return True 
    except Exception as e:
        print("Ошибка в test_art_find_invalid:", e)
        return False


print(test_start_authorized())
print(test_start_unauthorized())
print(test_art_find_valid())
print(test_art_find_invalid())