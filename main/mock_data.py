MOCK_PASSENGERS = [
    {"id": 1, "name": "Иван Иванов"},
    {"id": 2, "name": "Мария Петрова"},
]


permissions = {
    "Администратор": {"read": True, "write": True},
    "Пользователь": {"read": True, "write": False},
}
