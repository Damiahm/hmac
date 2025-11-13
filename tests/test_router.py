from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)

def example_test_handler() -> None:
    """
    Пример теста для HTTP хэндлера FastAPI

    По такой же логике нужно будет написать реальные тесты для проекта.
    """

    # С помощью тестового клиента отправляем POST запрос на /url с телом запроса {"data": "message"}
    response = client.post('/url', json={'data': 'message'})

    # Проверяем статус ответа
    assert response.status_code == 200

    # Проверяем тело ответа
    assert response.json() == {'ok': True}

