import json
import os
from typing import Dict, Any
from typing import Union

import pathlib


class Task:
    class Fields:
        ID = "id"
        UNIT = "unit"
        TASK_TEXT = "task_text"
        TASK_SOLUTION_CODE_ANALYTICS = "task_solution_code_analytics"
        TASK_SOLUTION_CODE = "task_solution_code"

    def __init__(self, id: int = 0, unit: str = "test", task_text: str = "нет", task_solution_code_analytics: str = "нет", task_solution_code: str = "нет"):
        self.id = id
        self.unit = unit
        self.task_text = task_text
        self.task_solution_code_analytics = task_solution_code_analytics
        self.task_solution_code = task_solution_code

    @staticmethod
    def deserialize(data: Dict[str, Any]) -> 'Task':
        return Task(
            id=data.get(Task.Fields.ID),
            unit=data.get(Task.Fields.UNIT),
            task_text=data.get(Task.Fields.TASK_TEXT),
            task_solution_code_analytics=data.get(Task.Fields.TASK_SOLUTION_CODE_ANALYTICS),
            task_solution_code=data.get(Task.Fields.TASK_SOLUTION_CODE)
        )


def load_all_tasks():
    all_tasks = []
    with open(pathlib.Path(pathlib.Path(os.path.dirname(os.path.abspath(__file__)), "tasks_base.txt")), encoding="UTF8") as f:
        for row in f:
            all_tasks.append(Task.deserialize(json.loads(row)))
    return all_tasks


def get_task_by_id(id: int) -> Union['Task', str]:
    all_tasks = load_all_tasks()
    for task in all_tasks:
        if task.id == id:
            return task
    return "NO TASK WITH THAT WORD, CHECK IT"


def find_by_words(words: str):
    words = words.split()
    all_tasks = load_all_tasks()
    counter = [0 for _ in range(len(all_tasks) + 4)]
    for task in all_tasks:
        task_words = task.task_text.split(" ")
        task_words = [w.lower().replace("ё", "е") for w in task_words]
        for word in task_words:
            if word in task_words:
                counter[task.id] += 1

    c = [[counter[i], i] for i in range(len(counter))]
    c.sort(reverse=True)
    for el in c:
        if el[0] > 0:
            i = el[1]
            text = all_tasks[i - 1].task_text
            print(i, "\n".join([text[128*i:128*(i + 1)] for i in range(0, (len(text) - 1) // 128 + 1)]))
