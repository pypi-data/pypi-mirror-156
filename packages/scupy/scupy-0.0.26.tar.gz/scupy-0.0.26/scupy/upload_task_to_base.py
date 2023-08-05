# -*- coding: utf-8 -*-
# Это программа для разработки, если вы случайно тут, то выйдите, пожалуйста, и ничего не ломайте
# ID меняется вручную, молю всех не продолбить это (я перед экзом поревьюю, но не обещаю)
# если вы не уверены в задаче, но хотите ее добавить в базу, пишите тем, кто знает тервер чтобы проверили
# если вы считаете, что это говнокод и соберете лучше -- пишите свою либу и шерьте со всеми
# если вы пришли с фичреквестом -- пишите dashkaz или rozyev23

import json
import scipy.stats
import statistics
import pathlib

my_own_task = {
    "id" : 1,
    "unit": "test",
    "task_text": 'Распределение баллов на экзамене до перепроверки задано таблицей Оценка работы 2 3 4 5 Число работ 7 22 49 25 Работы будут перепроверять 5 преподавателей, которые разделили все работы между собой поровну случайным образом. Пусть X¯¯¯¯ – средний балл (до перепроверки) работ, попавших к одному из преподавателей. Требуется найти: 1) математическое ожидание E(X¯¯¯¯); 2) стандартное отклонение σ(X¯¯¯¯).',
    "task_solution_code_analytics":
        """
score = [2,3,4,5]
N = sum(number)
n1 = N/n
e = sum([score[i]*number[i] for i in range(4)])/N

v = 1/N*sum([(score[i]**2*number[i]) for i in range(4)])-e**2
var = v*(N-n1)/(n1*(N-1))
e = str(round(e,5)).replace('.', ',')
var = str(round(var**0.5,5)).replace('.', ',')

print('Мат ожидание:', e)
print('Стандартное отклонение:', var)
        """
}
new_task = json.dumps(my_own_task, ensure_ascii=False)
with open(pathlib.Path(pathlib.Path(pathlib.Path.cwd(), "tasks_base.txt")), "a", encoding="UTF8") as f:
    f.write(new_task)
    f.write("\n")
