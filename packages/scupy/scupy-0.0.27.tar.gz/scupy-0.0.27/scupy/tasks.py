import json
import os
from typing import Dict, Any
from typing import Union
from typing import Optional

import pathlib
from IPython.display import display, Markdown, Latex


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

import string
def find_by_words(words: str, unit: Optional[str]):
    words = words.split()
    all_tasks = load_all_tasks()
    counter = [0 for _ in range(len(all_tasks) + 4)]
    for task in all_tasks:
        task_words = task.task_text.translate(str.maketrans('', '', string.punctuation))
        task_words = task_words.split(" ")
        task_words = [w.lower().replace("ё", "е") for w in task_words]
        for word in words:
            if word in task_words:
                counter[task.id] += 1

    c = [[counter[i], i] for i in range(len(counter))]
    c.sort(reverse=True)
    for el in c:
        if el[0] > 0:
            i = el[1]
            text = all_tasks[i - 1].task_text
            if unit:
                if all_tasks[i - 1].unit == unit:
                    print(i, "\n".join([text[128 * i:128 * (i + 1)] for i in range(0, (len(text) - 1) // 128 + 1)]))
            else:
                print(i, "\n".join([text[128*i:128*(i + 1)] for i in range(0, (len(text) - 1) // 128 + 1)]))


def load_all_unit_tasks(unit: str):
    all_tasks = load_all_tasks()
    for task in all_tasks:
        if task.unit == unit:
            print(task.id, task.task_text)


def sample_and_sample_choice_function():
    display(Markdown(r"""
    $ n\hat{F(x)}  \sim Bin(n, F(x)); F(x) = \frac{x-a}{b-a} $  

$ a)P((\hat{F(6)}=\hat{F(8)}) = P(X_i  \nsubseteq [5,8]) = (1-\frac{2}{3})^6 \approx 0,0014$  

$ б) Y = 6\hat{F(7)}\sim Bin(6, \frac{2}{3})  $  
$ P(\hat{F(7)})=\frac{1}{2} = P(Y=3) = С^3_6 p^3 (1-p)^3 = \frac{4 \cdot 5 \cdot 6}{6} \cdot (\frac{2}{3})^3 \cdot (\frac{1}{3})^3  \approx 0,2195$  
    """))


def sample_and_sample_choice_function():
    display(Markdown(r"""
    $ n\hat{F(x)}  \sim Bin(n, F(x)); F(x) = \frac{x-a}{b-a} $  

$ a)P((\hat{F(6)}=\hat{F(8)}) = P(X_i  \nsubseteq [5,8]) = (1-\frac{2}{3})^6 \approx 0,0014$  

$ б) Y = 6\hat{F(7)}\sim Bin(6, \frac{2}{3})  $  
$ P(\hat{F(7)})=\frac{1}{2} = P(Y=3) = С^3_6 p^3 (1-p)^3 = \frac{4 \cdot 5 \cdot 6}{6} \cdot (\frac{2}{3})^3 \cdot (\frac{1}{3})^3  \approx 0,2195$  
    """))

def sample_and_gen_function():
    display(Markdown(r"""
$ X_1,..., X_n$ - выборка 

$ X_i  \thicksim L_\theta(X)$ 

$L_\theta(x)$ имеет функцию распределния $F(x)$

$ X_{(1)},.., X_{(n)} $ - вариационный ряд

$ X_{(1)}\leq..\leq X_{(n)} \Rightarrow X_{(1)} = \min(X_1,.., X_n); X_{(n)}=\max(X_1,.., X_n) $

$ 1) F_{X_{(n)}} = P(X_{(n)} < x) = P(\max(X_1,.., X_n)<x) = P(X_1<x) \cdot...\cdot P(X_n<x)= F(x)\cdot...\cdot F(x) = (F(x))^n   $

$ 2) F_{X_{(1)}} = P(X_{(1)} < x) = P(\min(X_1,.., X_n)<x) = 1 - P(\min(X_1,.., X_n) > x)= 1 - P(X_1>x) \cdot...\cdot P(X_n>x) = 1 - \prod^n_{k=1}[1-P(X_k <x)] = 1 - \prod^n_{k=1}[1- F(x)] = 1-(1-F(x))^n $


  """))

def unmoved_marks():
    display(Markdown(r"""
а) $E(X^2) = \{Var(X) = E(X^2) - [E(X)]^2 \} = Var(X) + [E(X)]^2 = \sigma^2 + \theta^2 \neq \theta^2  \Rightarrow$ не явлется несмещенной  
б) $E(Z) = E(X \cdot Y) = E(X) \cdot E(Y) = \theta \cdot \theta = \theta^2  \Rightarrow несмещенная $
      """))


def prove_std():
    display(Markdown(r"""
$ E[(\hat{\theta} − \theta)^2] = E[(\hat{\theta})^2 - 2 \cdot \theta \cdot \hat{\theta} + \theta^2] = E((\hat{\theta})^2) - 2 \cdot \theta \cdot E(\hat{\theta}) + \theta^2 = \{Var(\hat{\theta}) = E((\hat{\theta})^2) - [E(\hat{\theta})]^2 \} = Var(\hat{\theta}) + [E(\hat{\theta})]^2 -  2 \cdot \theta \cdot E(\hat{\theta}) + \theta^2 = Var(\hat{\theta}) + (E[\hat{\theta}] - \theta))^2 = Var(\hat{\theta}) + b^2$ 
      """))


# todo: 6b
def prove_random_facts():
    display(Markdown(r"""
$a)\mu_3(\bar{X}) = \mu_3(\frac{X_1+...+X_n}{n}) = \{\mu_3(\frac{X_i}{n}) = E([\frac{X_i}{n}-E(\frac{X_i}{n})]^3) = E(\frac{1}{n^3}[X_i - E(X_i)]^3) = \frac{1}{n^3}\mu_3(X_i)\} = \frac{1}{n^3}[\mu_3(X_1)+...+\mu_3(X_n)] = \frac{1}{n^3} \cdot n \mu_3(X) = \frac{\mu_3(X)}{n^2}  $  

$б) \mu_4(\bar{X}) = $

         """))

def gen_dist_unmoved():
    display(Markdown(r"""
$ a) \hat{\theta}_1 = c_1(X_1 - X_2)^2 $  
$ E(\hat{\theta}_1) = E(c_1(X_1 - X_2)^2) = c_1E(X_1^2)-2c_1E(X_1\cdot X_2) +c_1E(X_2^2) = \{ E(X_1^2) = Var(X_1) + [E(X_1)]^2 = \theta + \mu^2 \} = c_1(\theta + \mu^2) - 2c_1E(X_1)E(X_2) + c_1(\theta + \mu^2) = 2c_1(\theta + \mu^2) -2c_1\mu^2 = 2c_1\theta \Rightarrow c_1 = \frac{1}{2}    $


$ б) \hat{\theta}_2 = c_2[(X_1 - X_2)^2 + (X_1 - X_3)^2 + (X_2 - X_3)^2] $

$ E(\hat{\theta}_2) = c_2(E[(X_1 - X_2)^2] + E[(X_1 - X_3)^2] + E[(X_2 - X_3)^2]) $

$ E((X_1-X_2)^2) = E(X_1^2)-2E(X_1\cdot X_2) +E(X_2^2) = 2\theta $ пункт a  

$ E(\hat{\theta}_2) = c_2(2\theta + 2\theta +2\theta) = 6c_2\theta \Rightarrow c_2 = \frac{1}{6} $
         """))


def example_dist_unmoved():
    display(Markdown(r"""
$ a) 1) E(\hat{\theta}_1) = E(\frac{X1+2X2+3X3+4X4}{10}) = \frac{1}{10}[E(X_1) + 2E(X_2) + 3E(X_3) + 4E(X_4)] = \theta10 \cdot \frac{1}{10} = \theta \Rightarrow $ несмещанная  
$ 2) E(\hat{\theta}_2) = E(\frac{X1+4X2+4X3+X4}{10}) = \frac{1}{10}[E(X_1) + 4E(X_2) + 4E(X_3) + 1E(X_4)] = \theta10 \cdot \frac{1}{10} = \theta \Rightarrow $ несмещанная  
Оптимальная та, у который  $ б) min(Var(X_i))$  
$ 1) Var((\hat{\theta}_1) = Var(\frac{X1+2X2+3X3+4X4}{10}) = \frac{1}{100}[Var(X_1) + 4Var(X_2) + 9Var(X_3) + 16Var(X_4)] = \theta30 \cdot \frac{1}{100} = \frac{3}{10}\theta $  
$ 2) Var((\hat{\theta}_2) = Var(\frac{X1+4X2+4X3+1X4}{10}) = \frac{1}{100}[Var(X_1) + 16Var(X_2) + 16Var(X_3) + 1Var(X_4)] = \theta36 \cdot \frac{1}{100} = \frac{36}{100}\theta$  
$ \frac{3}{10} < \frac{36}{100} \Rightarrow \hat{\theta}_1$ оптимальнее  

         """))


def gen_dist_tetta():
    display(Markdown(r"""
$ a) 1) E(\hat{\theta}_1) = E(\frac{X_1+X_2}{2}) = \frac{1}{2}[E(X_1)+E(X_2)]= \frac{1}{2}\cdot2\theta = \theta  \Rightarrow $ несмещанная  
$ 2) E(\hat{\theta}_2) = E(\frac{X_1+X_n}{4} + \frac{X_2+...+X_(n-1)}{2(n-2)}) = \frac{1}{4}[E(X_1)+E(X_n)] + \frac{1}{2(n-2)}[E(X_2)+...+E(X_(n-1)] = \frac{2}{4}\theta + \frac{(n-2)}{2(n-2)}\theta = \theta \Rightarrow $ несмещанная  
$ 3) E(\hat{\theta}_3) = E(\bar{X}) = E( \frac{X_1+...+X_n}{n}) = \frac{1}{n}[E(X_1)+..+E(X_n)] = \frac{1}{n} \cdot n\theta = \theta \Rightarrow $ несмещанная  


$ б) 1) Var(\hat{\theta}_1) = Var(\frac{X_1+X_2}{2}) = \frac{1}{4}[Var(X_1)+Var(X_2)]= \frac{1}{4}\cdot2\sigma^2 = \frac{1}{2}\sigma^2; \lim\limits_{n\to\infty}(\frac{1}{2}\sigma^2)\neq 0\Rightarrow $ несостоятельная  
$ 2) Var(\hat{\theta}_2) = Var(\frac{X_1+X_n}{4} + \frac{X_2+...+X_(n-1)}{2(n-2)}) = \frac{1}{16}[Var(X_1)+Var(X_n)] + \frac{1}{4(n-2)^2}[Var(X_2)+...+Var (X_(n-1)] =  \frac{1}{8}\sigma^2 + \frac{1}{4(n-2)}\sigma^2 ; \lim\limits_{n\to\infty}(\frac{1}{8}\sigma^2 + \frac{1}{4(n-2)}\sigma^2 )\neq 0\Rightarrow $ несостоятельная  
$ 3) Var(\hat{\theta}_3) = Var(\bar{X})= \frac{1}{n^2}[Var(X_1) +...+Var(X_n)] = \frac{1}{n^2} \cdot n\sigma^2 = \frac{1}{n}\sigma^2; \lim\limits_{n\to\infty}(\frac{1}{n}\sigma^2 = 0\Rightarrow $ состоятельная 
         """))


def uniform_dist_tetta():
    display(Markdown(r"""
$ F_x(x) = \frac{x}{\theta}$

$ f_x(x) = \frac{1}{\theta}$

$ E(X) = \frac{\theta}{2}$

$ Var(X) = \frac{\theta^2}{12}$


$ \hat{\theta}_1 = 2\bar{X}$

$ E(\hat{\theta}_1) = E(2\bar{X}) = 2E(\frac{X_1+...+X_2}{n}) = \frac{2}{n}E(X_1+..+X_2) =\frac{2}{n}E(X_i) = \frac{2}{n} \cdot n \cdot \frac{\theta}{2} = \theta \Rightarrow $ несмещенная


$ Var(\hat{\theta}_1) = Var(2\bar{X}) = 4[Var(\frac{X_1+...+X_n}{n})] = 4 \cdot \frac{1}{n} \cdot Var(X_i) = \frac{4 \cdot \theta^2}{n \cdot 12} = \frac{ \theta^2}{n \cdot 3}; \lim\limits_{n\to\infty}(\frac{ \theta^2}{n \cdot 3}) = 0\Rightarrow $ состоятельная  


$ \hat{\theta}_2 = \frac{n+1}{n}X_{(n)} $  

$ F_{x_{(n)}}(x) = F_{X_{(n)}} = P(X_{(n)} < x) = P(\max(X_1,.., X_n)<x) = P(X_1<x) \cdot...\cdot P(X_n<x)= F(x)\cdot...\cdot F(x) = (F(x))^n = (\frac{x}{\theta})^n  $

$ f_{x_{(n)}}(x) = ((F(x))^n)' = nF^{n-1}(x) = n * \frac{x^{n-1}}{\theta^n} $



$ E(\hat{\theta}_2) = E(\frac{n+1}{n}X_{(n)}) = \frac{n+1}{n} \cdot \int_{0}^\theta x * n * \frac{x^{n-1}}{\theta^n} dx = \frac{n+1}{n} * \frac{n}{\theta^n} \int_{0}^\theta x^n dx  = \theta \Rightarrow $ несмещенная


         """))


def uniform_tetta_another_version():
    display(Markdown(r"""
$ F_x(x) = \frac{x}{\theta}$

$ f_x(x) = \frac{1}{\theta}$

$ E(X) = \frac{\theta}{2}$

$ Var(X) = \frac{\theta^2}{12}$


$ \hat{\theta}_1 = 2\bar{X}$

$ E(\hat{\theta}_1) = E(2\bar{X}) = 2E(\frac{X_1+...+X_2}{n}) = \frac{2}{n}E(X_1+..+X_2) =\frac{2}{n}E(X_i) = \frac{2}{n} \cdot n \cdot \frac{\theta}{2} = \theta  \Rightarrow $ несмещенная

$ Var(\hat{\theta}_1) = Var(2\bar{X}) = 4[Var(\frac{X_1+...+X_n}{n})] = 4 \cdot \frac{1}{n} \cdot Var(X_i) = \frac{4 \cdot \theta^2}{n \cdot 12} = \frac{ \theta^2}{n \cdot 3}; \lim\limits_{n\to\infty}(\frac{ \theta^2}{n \cdot 3}) = 0\Rightarrow $ состоятельная  
         """))


def rand_value_3():
    display(Markdown(r"""
$ E(X_i) = \frac{0+\theta}{2} = \frac{\theta}{2}; Var(X_i) = \frac{(\theta-0)^2}{12}= \frac{\theta^2}{12}; f(x,\theta)= \frac{1}{\theta}; n=3 $  
$ \hat{\theta} = c \cdot \bar{X} = c \cdot \frac{X_1+X_2+X_3}{3}$  
$ a) E(\hat{\theta}) = E(c \cdot \frac{X_1+X_2+X_3}{3}) = \frac{c}{3}[E(X_1)+E(X_2)+E(X_3)] = \frac{3cE(X_i)}{3} = c \cdot \frac{\theta}{2} = \theta \Rightarrow c=2  $  
$ б) Var(\hat{\theta}) = \frac{1}{nI(\theta)}; I(\theta)= nE[(\frac{\partial lnf(x,\theta)}{\partial \theta})^2] $  
$ \ln(f(x,\theta)) = \ln(\frac{1}{\theta})= -\ln(\theta)$  
$ (\frac{\partial lnf(x,\theta)}{\partial \theta})^2 = (\frac{-1}{\theta})^2= \frac{1}{\theta^2}  $  
$ I(\theta)= nE[\frac{1}{\theta^2}] = \frac{n}{\theta^2} $  
$ Var(\hat{\theta}) = Var(c \cdot \frac{X_1+X_2+X_3}{3}) = \frac{c^2}{9}[Var(X_1)+Var(X_2)+Var(X_3)]= \frac{c^2}{9}Var(X_i)= \frac{c^2\theta^2}{36} $  
$ \frac{c^2\theta^2}{36} = \frac{1}{\frac{9}{\theta^2}} \Rightarrow \frac{c^2}{36} =\frac{1}{9} \Rightarrow c =2  $
         """))


def sqrt_param_tetta():
    display(Markdown(r"""
$ a) E(\hat{\theta}) = E[\frac{3}{n}((X_1)^2+(X_2)^2+(X_3)^2))]= 3 \cdot \frac{3}{n}E[(X_i)^2] = 3 (Var(X_i) + [E(X_I)]^2) = 3( \frac{(b-a)^2}{12} + \frac{a+b}{2}) = 3(\frac{(\theta - (-\theta))^2}{12} = \frac{3\cdot4\theta^2}{12}= \theta^2 \Rightarrow $ несмещенная  
$ б) E(\sqrt{\hat{\theta}}) = E[\sqrt{\frac{3}{n}((X_1)^2+(X_2)^2+(X_3)^2)}) = E[\sqrt{3(X_i)^2}]= \sqrt{3}\left\lvert X_i \right\rvert = \sqrt{3} \int_{-\theta}^\theta \left\lvert X_i \right\rvert \cdot \frac{1}{2\theta} dX = \frac{\sqrt{3}}{2\theta}(-\int_{-\theta}^0 xdx + \int_{0}^\theta xdx) = \frac{\sqrt{3}}{2\theta} (\frac{\theta^2}{2}+ \frac{\theta^2}{2}) = \frac{\sqrt{3}}{2}\theta \Rightarrow $  
смещанная
         """))


def beta_eps_eq():
    display(Markdown(r"""
$$ \hat{\beta} =  \frac{\sum_{k=1}^{n}Y_k}{\sum_{k=1}^{n}x_i} = \frac{\sum_{k=1}^{n}\beta x_k + \epsilon_k}{\sum_{k=1}^{n}x_i} = \frac{\beta\sum_{k=1}^{n} x_k + \sum_{k=1}^{n}\epsilon_k}{\sum_{k=1}^{n}x_i}  = \beta + \frac{\sum_{k=1}^{n}\epsilon_k}{\sum_{k=1}^{n}x_i} $$
$ E(\hat{\beta}) = E(\beta + \frac{\sum_{k=1}^{n}\epsilon_k}{\sum_{k=1}^{n}x_i}) = \beta + E[\sum_{k=1}^{n}\epsilon_k] \cdot \frac{1}{\sum_{k=1}^{n}x_i} = \beta + n \cdot 0 \cdot \frac{1}{\sum_{k=1}^{n}x_i} = \beta  $
         """))


def beta_eps_another_version():
    display(Markdown(r"""
$ E(\hat{\beta}) = E[\frac{1}{n}\sum_{k=1}^{n}(\frac{Y_k}{x_k})] = \frac{1}{n}E[\sum_{k=1}^{n}(\frac{\beta x_k + \epsilon_k}{x_k})] = \frac{1}{n}E[\sum_{k=1}^{n}(\beta  + \frac{\epsilon_k}{x_k})] = \frac{1}{n}[E(\sum_{k=1}^{n}\frac{\epsilon_k}{x_k}) + \sum_{k=1}^{n}\beta] = \frac{1}{n}[n\cdot \beta + E(\frac{\epsilon_1}{x_1}+...+E(\frac{\epsilon_k}{x_k}=\frac{1}{n}(n\cdot \beta + \frac{0}{x_1} + \frac{0}{x_k}) = \beta   $
         """))


def poisson_moment():
    display(Markdown(r"""
$ a) \nu_1 = \hat{\nu_1}$ 

$\nu_1 = E(x) = \theta$

$\hat{\nu_1} = \bar{X} = \frac{0*146+1*97+..+10*2}{400}= 1,5375 = \hat{\theta}=\hat{\lambda} $


$ P(X>3) = 1 - P(X<3) = 1 - P(X=0) - P(X=1) - P(X=2) $

$ P(X=k)= \frac{\lambda^k\cdot \exp^{-\lambda}}{k!} $


$ P(X=0) = \frac{1,5375^0\cdot \exp^{-1,5375}}{0!} = 0,2149 $  
$ P(X=1) = \frac{1,5375^1\cdot \exp^{-1,5375}}{1!} = 0,3304 $  
$ P(X=2) = \frac{1,5375^2\cdot \exp^{-1,5375}}{2!} = 0,2540 $

$ P(X>3) = 1 - P(X<3) = 1 - P(X=0) - P(X=1) - P(X=2) = 1 - 0,2149 - 0,3304 - 0,2540 = 0,2007    $

$ б) P(X>3) = 1 - P(X<3) = 1 - (\frac{146+97+73}{400}) = 0.21 $

         """))


def moment_eval():
    display(Markdown(r"""
$V_1 = E(x) = \frac{(b-a)}{2} = \frac{(4\theta-0)}{2} = 2\theta $

$\hat{V_1}=\bar{X}  \Rightarrow 2\hat{\theta} = \bar{X} \Rightarrow \hat{\theta} = \frac{\bar{X}}{2}$

$ a) E(\hat{\theta}) = E(\frac{\bar{X}}{2}) = \frac{1}{2}E(\frac{X_1+...+X_n}{n}) = \frac{n}{2} \cdot nE(X_i) = \frac{1}{2} \cdot  2\theta = \theta \Rightarrow $ несмещенная


$Var(X_i) = \frac{(b-a)^2}{12}$

$ б) \lim\limits_{n\to\infty}(Var(\hat{\theta}) = \lim\limits_{n\to\infty}(Var(\frac{\bar{X}}{2}) = \lim\limits_{n\to\infty}\frac{1}{4}Var(\frac{X_1+..+X_n}{n}) = \lim\limits_{n\to\infty}\frac{1}{n^2 \cdot 4}Var(X_i) = \lim\limits_{n\to\infty}\frac{1(4\theta-0)^2}{n^2 \cdot 4} = \lim\limits_{n\to\infty}\frac{16\theta^2}{n^2 \cdot 4} = 0 \Rightarrow  $ состоятельная
         """))

