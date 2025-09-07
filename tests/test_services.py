from src import services


def test_cashback_service():
    tx = [{"category": "Еда", "amount": 100}]
    result = services.cashback_categories(2020, 5, tx)

    assert "report" in result
    assert result["report"] == "cashback_service"


def test_invest_saver():
    tx = [{"amount": 97}]
    result = services.invest_piggybank(5, tx, 10)

    assert "report" in result
    assert "savings" in result


def test_simple_search():
    tx = [{"desc": "Перевод"}]
    result = services.simple_search("Перевод", tx)

    assert result["matches"]


def test_phone_search():
    tx = [{"desc": "Перевод на +79991234567"}]
    result = services.phone_search(tx)

    assert result["matches"]


def test_transfer_search():
    tx = [{"desc": "Перевод Иванов Иван"}]
    result = services.p2p_search(tx)

    assert result["matches"]
