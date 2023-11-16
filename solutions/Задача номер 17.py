# Источник: https://inf-ege.sdamgia.ru/test?id=14289935&nt=True&pub=False
from itertools import combinations

from config import debug_print, is_debug

# Задача:
# В файле содержится последовательность из 10000 целых положительных чисел. Каждое число не превышает 10000. Определите
# и запишите в ответе сначала количество пар элементов последовательности у которых сумма элементов кратна 8 затем
# максимальную из сумм элементов таких пар. В данной задаче под парой подразумевается два различных элемента
# последовательности. Порядок элементов в паре не важен. 17.txt Ответ

nums = tuple(map(int, open(r"../files/Задача номер 17/17.txt.txt").readlines()))

co = 0
su = -1000000
for a, b in combinations(nums, 2):
    if not is_debug(): break
    if (a + b) % 8 == 0:
        co += 1
        su = max(su, a+b)

debug_print(co, su)
print(6243772, 19992)
