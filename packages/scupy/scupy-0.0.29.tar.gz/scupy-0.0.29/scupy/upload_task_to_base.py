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
    "unit": "q3",
    "task_text": r'17.  Пусть случайная величина X равномерно распределена на отрезке [0; 4θ]. Найдите методом моментов оценку для параметра θ. Является ли оценка а) несмещенной; б) состоятельной? Ответ обосновать',
    "task_solution_code_analytics":
        """
scupy.moment_eval()
        """
}
new_task = json.dumps(my_own_task, ensure_ascii=False)
with open(pathlib.Path(pathlib.Path(pathlib.Path.cwd(), "tasks_base.txt")), "a", encoding="UTF8") as f:
    f.write(new_task)
    f.write("\n")
