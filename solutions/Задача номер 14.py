# Источник: https://inf-ege.sdamgia.ru/test?id=14289935&nt=True&pub=False
from config import debug_print


# Задача:
# Значение выражения 256 + 518 5? записали в системе счисления с основанием 5. Сколько цифр 4 содержится в этой записи?

def convert(num, base):
    res = ""
    while num > 0:
        res = str(num % base) + res
        num = num // base
    return res


result = convert(25 ** 6 + 5 ** 18 - 5, 5)
debug_print(result)

print(result.count("4"))
