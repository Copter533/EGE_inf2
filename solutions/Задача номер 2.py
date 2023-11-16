# Источник: https://inf-ege.sdamgia.ru/test?id=14289935&nt=True&pub=False

# Задача:
# Логическая функция F задаётся выражением x y z y z w. На рисунке приведён частично заполненный фрагмент таблицы
# истинности функции F содержащий неповторяющиеся строки. Определите какому столбцу таблицы истинности функции F
# соответствует каждая из переменных x y z w. ????F1111001111 В ответе напишите буквы x y z w в том порядке в котором
# идут соответствующие им столбцы. Буквы в ответе пишите подряд никаких разделителей между буквами ставить не нужно.

from config import debug_print  # Это будет заменено на просто print на ЕГЭ
from itertools import product, permutations


table1 = """
x111
x00x
x1x1
""".replace("\n", "")
table2 = ""

for x, y, z, w in product([0, 1], repeat=4):
    val = (not x or y or z) == (not y and z and w)
    if val:
        debug_print(f"{x} | {y} | {z} | {w} = TRUE")
        table2 += f"{x}{y}{z}{w}"

for p1 in permutations(range(len(table2) // 4)):
    for p2 in permutations(range(4)):
        for i, e in enumerate(table1):
            j = p2[i % 4] + p1[i // 4] * 4
            if not (e == "x" or table2[j] == e): break
        else:
            print(''.join(['xyzw'[i] for i in p2]))
