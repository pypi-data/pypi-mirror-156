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
    "task_text": r'файл задача с файлом задача номер 6 про файл файлик csv',
    "task_solution_code_analytics":
        """
lnL = -N*ln(2*Pi) - N * ln(theta_1**2) - N/2*ln(1-theta_2**2) - N/(2*theta_1**2*(1-theta_2**2))*((A)+(B)-2*theta_2*(C))
lnL
        """
}
new_task = json.dumps(my_own_task, ensure_ascii=False)
with open(pathlib.Path(pathlib.Path(pathlib.Path.cwd(), "tasks_base.txt")), "a", encoding="UTF8") as f:
    f.write(new_task)
    f.write("\n")
