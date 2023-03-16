# aiohttp_black_jack
Black Jack Бот в ВКонтакте

## Стек
- Python 3.11
  - AIOHTTP
  - SQLAlchemy
  - Marshmallow
  - Pytest
- PostgreSQL
- Docker + Docker Compose
- RabbitMQ

## Как начать игру?
1. Перейдите в группу [Black Jack Bot](https://vk.com/club218833701)
2. Добавьте бота в свой чат с помощью кнопки "Добавить в чат"
3. Сделайте бота администратором беседы
4. Начните игру с помощью команды ```/start_game```

## Команды бота
```/start``` - Запускает бота и отправляет приветствие.   
```/help``` - Выдает список всех команд бота.   
```/start_game``` - Запускает игру.   
```/stop_game``` - Останавливает игру.   

## Документация
Документация API доступна по роуту ```/docs```   

## Cхема базы данных
[Ссылка](https://dbdiagram.io/d/63ff4e2b296d97641d84a283)