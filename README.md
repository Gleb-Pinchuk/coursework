# Coursework_1

## Описание

Проект для работы с финансовыми транзакциями.  
Функционал включает:  
- Загрузка транзакций из Excel-файла (`operations.xlsx`).  
- Формирование веб-страниц «Главная» и «События».  
- Реализация сервисов (поиск, кешбэк, инвесткопилка).  
- Генерация отчётов по тратам.  

## Установка

1. Клонируйте репозиторий:

```bash
git clone https://github.com/Gleb-Pinchuk/coursework.git
cd coursework

pip install poetry

poetry install
poetry shell

## Тестирование

poetry run pytest

2. с отчетом покрытия кода:
pytest --cov=src
## Лицензия: этот проект создан для учебных целей
