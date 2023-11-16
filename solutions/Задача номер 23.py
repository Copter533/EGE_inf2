# Источник: https://inf-ege.sdamgia.ru/test?id=14289935&nt=True&pub=False

# Задача:
# Исполнитель ТренерБ преобразует число записанное на экране. У исполнителя три команды которым присвоены номера
# 1.Прибавь 1 2.Прибавь 2 3.Прибавь 6 Первая из них увеличивает число на экране на 1 вторая увеличивает это число на 2 а
# третья на 6. Программа для исполнителя ТренерБ это последовательность команд. Сколько существует программ которые
# число 21 преобразуют в число 30?


def solve(n):
    if n == 30: return 1
    if n > 30: return 0

    return solve(n+1) + solve(n+2) + solve(n+6)


print(solve(21))
