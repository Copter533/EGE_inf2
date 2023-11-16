# Источник: https://inf-ege.sdamgia.ru/test?id=14289935&nt=True&pub=False
from config import debug_print

# Задача:
# Для какого наибольшего целого неотрицательного числа A выражение x A y A 2y + x 110 тождественно истинно то есть
# принимает значение 1 при любых целых неотрицательных x и y?

for A in range(36, 0, -1):
    stop = False
    for x in range(1000, 0, -1):
        if stop: break
        for y in range(1000, 0, -1):
            val = (x > A) or (y > A) or (2 * y + x < 110)
            if not val: stop = True
    else:
        print(A)
        break
