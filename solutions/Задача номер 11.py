# Источник: https://inf-ege.sdamgia.ru/test?id=14289935&nt=True&pub=False

# Задача:
# Каждый сотрудник предприятия получает электронный пропуск на котором записаны личный код сотрудника и срок действия
# пропуска. Личный код состоит из 19 символов каждый из которых может быть одной из 26 заглавных латинских букв. Для
# записи кода на пропуске отведено минимально возможное целое число байтов при этом используют посимвольное кодирование
# все символы кодируют одинаковым минимально возможным количеством битов. Срок действия записывается как номер года
# число от 0 до 60 означающее год от 2000 до 2060 и номер дня в году число от 1 до 366. Номер года и номер дня записаны
# на пропуске как двоичные числа каждое из них занимает минимально возможное число битов а два числа вместе минимально
# возможное число байтов. Сколько байтов занимает вся информация на пропуске? В ответе запишите только целое число
# количество байтов.

from math import log, ceil


length = 19
alphabet = 26
year = (0, 60)
day = (1, 366)

code = ceil(ceil(log(alphabet, 2)) * length / 8)
y_date = ceil(log(year[1] - year[0] + 1, 2))
d_date = ceil(log(day[1] - day[0] + 1, 2))
date = ceil((y_date + d_date) / 8)
print(code + date)
