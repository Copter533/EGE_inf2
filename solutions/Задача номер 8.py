# Источник: https://inf-ege.sdamgia.ru/test?id=14289935&nt=True&pub=False

# Задача:
# Все 5-буквенные слова составленные из букв В И Н Т записаны в алфавитном порядке и пронумерованы. Вот начало списка
# 1.ВВВВВ 2.ВВВВИ 3.ВВВВН 4.ВВВВТ 5.ВВВИВ Запишите слово которое стоит под номером 1019.

from itertools import product
from config import debug_print, is_debug

num = 0
for seq in product("ВИНТ", repeat=5):
    num += 1
    word = "".join(seq)
    debug_print(f"{num:0>4}", "-", word)
    if num == 1019:
        print(word)
        if not is_debug(): break
