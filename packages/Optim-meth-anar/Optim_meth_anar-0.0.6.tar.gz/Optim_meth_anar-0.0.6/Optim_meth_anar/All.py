import pandas as pd


def brent(func, interval, pression=1e-5, max_iter=500,
          flag_results=False, flag_data=False, type_opt='min'):
    """
    Функция поиска экстремума методом Брента.
    :param func: python function
    :param interval: list consisting of float numbers(left and right bounds)
    :param pression: optimization accuracy
    :param max_iter: maximum amount of iterations
    :param flag_results: output of intermediate results
    :param flag_data: recording intermediate results in a dataset
    :param type_opt: ype of extrema: if min:flag_opt=1
                                      if max: flag_opt=-1
    :return: extrema:the point at which the extremum
             df: intermediate results in a dataset
    """
    if type_opt == 'min':
        flag_opt = 1
    else:
        flag_opt = -1

    data = []
    df = pd.DataFrame(columns=['iter', 'point', 'function', 'step_name'])
    step_name = []
    a, b = interval
    gold_const = (3 - 5 ** 0.5) / 2
    remainder = 0.0

    x_largest = x_middle = x_least = a + gold_const * (b - a)
    f_largest = f_middle = f_least = flag_opt * func(x_least)
    if flag_data:
        data = [[0, x_least, func(x_least), '']]
    if flag_results:
        print(f"Номер итерации {0}, точка {x_least}, функция {func(x_least)} .")

    for i in range(1, max_iter + 1):
        middle_point = (a + b) / 2
        tolerance = pression * abs(x_least) + 1e-9

        if abs(x_least - middle_point) > 2 * tolerance - (b - a) / 2:
            p = q = previous_remainder = 0
            if abs(remainder) > tolerance:

                p = ((x_least - x_largest) ** 2 * (f_least - f_middle) -
                     (x_least - x_middle) ** 2 * (f_least - f_largest))

                q = 2 * ((x_least - x_largest) * (f_least - f_middle) -
                         (x_least - x_middle) * (f_least - f_largest))

                if q > 0:
                    p = -p
                else:
                    q = -q

                previous_remainder = remainder
            if abs(p) < 0.5 * abs(q * previous_remainder) and a * q < x_least * q + p < b * q:
                remainder = p / q
                x_new = x_least + remainder
                name_step = 'parabolic'
                step_name.append((name_step))
                if x_new - a < 2 * tolerance or b - x_new < 2 * tolerance:
                    if x_least < middle_point:
                        remainder = tolerance
                    else:
                        remainder = -tolerance

            else:
                name_step = 'golden'
                step_name.append((name_step))
                if x_least < middle_point:
                    remainder = (b - x_least) * gold_const
                else:
                    remainder = (a - x_least) * gold_const
            if abs(remainder) > tolerance:
                x_new = x_least + remainder
            elif remainder > 0:
                x_new = x_least + tolerance
            else:
                x_new = x_least - tolerance

            f_new = flag_opt * func(x_new)


            if f_new <= f_least:
                if x_new < x_least:
                    b = x_least
                else:
                    a = x_least

                x_largest = x_middle
                f_largest = f_middle

                x_middle = x_least
                f_middle = f_least

                x_least = x_new
                f_least = f_new

            else:
                if x_new < x_least:
                    a = x_new
                else:
                    b = x_new

                if f_new <= f_middle:
                    x_largest = x_middle
                    f_largest = f_middle

                    x_middle = x_new
                    f_middle = f_new

                elif f_new <= f_largest:
                    x_largest = x_new
                    f_largest = f_new

        else:
            print('найдено значение с заданной точностью, code 0')
            break
        if flag_data:

            data.append(([i + 1, x_least, func(x_least), step_name[-1]]))
            df = pd.DataFrame(data, columns=['iter', 'point', 'function', 'step_name'])

        if flag_results:
            print(f"Номер итерации {i + 1}, точка {x_least}, функция {func(x_least)}.")

    return x_least, df
import pandas as pd

def golden_ratio(func, interval, pression=10 ** (-5), max_iter=500,
                 flag_results=False, flag_data=False, type_opt='min'):
    """
    Функция поиска экстремума функции одной переменной методом золотого сечения
    :param func: python function
    :param interval: list consisting of float numbers(left and right bounds)
    :param pression: optimization accuracy
    :param max_iter: maximum amount of iterations
    :param flag_results: flag: output of intermediate results
    :param flag_data: flag: recording intermediate results in a dataset
    :param type_opt: type of extrema: if min:flag_opt=1
                                      if max: flag_opt=-1
    :return: extrema:the point at which the extremum
             df: intermediate results in a dataset
    """
    try:
        if type_opt == 'min':
            flag_opt = 1
        else:
            flag_opt = -1

        data = []
        df = pd.DataFrame(columns=['iter', 'point', 'function', 'size'])
        phi = (5 ** 0.5 + 1) / 2
        a = interval[0]
        b = interval[1]
        extrema = (b + a) / 2

        x1 = b - (b - a) / phi
        x2 = a + (b - a) / phi

        if flag_data:
            data = [[0, extrema, func(extrema), 3]]
        if flag_results:
            print(f"Номер итерации {0}, точка {(a+b) / 2}, функция {func((a+b) / 2)}.")

        for i in range(max_iter):
            if abs(a - b) >= pression:
                if flag_opt * func(x1) > flag_opt * func(x2):
                    a = x1
                    x1 = b - (b - a) / phi
                    x2 = a + (b - a) / phi
                else:
                    b = x2
                    x1 = b - (b - a) / phi
                    x2 = a + (b - a) / phi
                extrema = (b + a) / 2
                if i == 499:
                    print('достигнуто максимальное количество итераций code 1')
            else:
                print('найдено значение с заданной точностью, code 0')
                break


            data.append(([i+1, extrema, func(extrema), 3]))
            df = pd.DataFrame(data, columns=['iter', 'point', 'function', 'size'])

            if flag_results:
                print(f"Номер итерации {i+1}, точка {extrema}, функция {func(extrema)}.")
    except Exception:
        print('выполнено с ошибкой. code 2')
    return func, interval,extrema, df
def gradient_descent_fixed(w_init, obj_func, grad_func, learning_rate=0.05,
                           max_iterations=500, threshold=1e-2):
    """
    Функция поиска минимума целевой функции одной переменной методом градиентного спуска, который находит оптимальное решение, делая шаг в сторону максимальной скорости уменьшения функции.
    :param obj_fun: objective function that is going to be minimized (call val,grad = obj_fun(w)).
    :param w_init: starting point Mx1
    :param grad_func: gradiation function that is going to be minimized (call val,grad = obj_fun(w)).
    :param max_iterations: number of epochs / iterations of an algorithm
    :param learning_rate: learning rate
    :return: function optimizes obj_fun using gradient descent. It returns (w,func_values),
    where w is optimal value of w and func_valus is vector of values of objective function [epochs x 1] calculated for each epoch
        """

    w = w_init
    w_history = w
    f_history = obj_func(w)
    delta_w = np.zeros(w.shape)
    i = 0
    diff = 1.0e10

    while i < max_iterations and diff > threshold:
        delta_w = -learning_rate * grad_func(w)
        w = w + delta_w

        # store the history of w and f
        w_history = np.vstack((w_history, w))
        f_history = np.vstack((f_history, obj_func(w)))

        # update iteration number and diff between successive values
        # of objective function
        i += 1
        diff = np.absolute(f_history[-1] - f_history[-2])
        print(f'X = {w_history[-1]}', f'Y = {f_history[-1]}', f'Iter = {i}', sep='\n')
        print({'Значение': f_history[-1], 'Кол-во итераций': i})
    return w_history, f_history
import numpy as np
import sympy as sm
import pandas as pd

def lagrange(variab, func, restr, restr_func):
    '''
    Поиск локальных экстремумов функции двух переменных с ограничениями (метод Лагранжа);
    :param variab: кортеж состоящий из переменных, которые являются sympy symbols
    :param func: sympy expression
    :param restr: возвращает словарь, где ключом выступают названия переменных,
    значениями являются списки, с ограничивающими интервалами
    :param restr_func: sympy expression
    :return: Список координат и значение функции в точке, для всех точек локальных экстремумов,
     с указанием типа экстремума (минимум, максимум, седловая точка)
    '''
    x, y, lam = sm.symbols('x, y lambda')

    func = func.subs({variab[0]: x, variab[1]: y})  # заменяем переменные во избежание комплексных ответов
    restr_func = restr_func.subs({variab[0]: x, variab[1]: y})
    lagr_func = func + restr_func * lam
    lagr_func

    func = func.subs({variab[0]: x, variab[1]: y})  # заменяем переменные во избежание комплексных ответов
    lagr_func = func + restr_func * lam  # составляем функцию лагранжа
    restr_func = restr_func.subs({variab[0]: x, variab[1]: y})
    variab1_d = sm.diff(lagr_func, x)  # дифференцируем по каждой из переменных
    variab2_d = sm.diff(lagr_func, y)

    sol = sm.solve([variab1_d,
                    variab2_d,
                    restr_func],
                   [x, y, lam], dict=True)  # приравниваем частные производные и ограничивающую функцию к нулю и
    # решаем систему
    for solution in sol:
        if len(solution) < 3:
            sol.remove(solution)
    if sol == []:
        sol_restr_all = 'бесконечное количество решений'
        sol_restr = ''
    else:
        sol_restr = []
        sol_restr_all = []
        for solution in sol:
            if solution[x].is_real and solution[y].is_real:

                if restr[variab[0]][0] <= solution[x] <= restr[variab[0]][1] and \
                        restr[variab[1]][0] <= solution[y] <= restr[variab[1]][1]:
                    sol_restr.append(solution)
                    sol_restr_all.append(solution)
            else:

                sol_restr_all.append(solution)

        hessian_matrix = sm.hessian(lagr_func, [lam, x, y])  # Hessian matrix

        for dot in sol_restr_all:
            if hessian_matrix.subs(dot).det() > 0:  # смотрим знак определителя матрицы
                dot['type'] = 'max'  # добавляем в словарь с соответствующей точкой ее тип
            elif hessian_matrix.subs(dot).det() < 0:  # смотрим знак определителя матрицы
                dot['type'] = 'min'  # добавляем в словарь с соответствующей точкой ее тип
            else:
                dot['type'] = 'saddle'  # добавляем в словарь с соответствующей точкой ее тип
            dot['func_value'] = func.subs(dot)

        for dot in sol_restr:
            hessian_matrix_with_dot = hessian_matrix.subs(dot)
            hessian_matrix_with_dot = np.array(hessian_matrix_with_dot).astype(np.float64)

            if np.all(np.linalg.eigvals(
                    hessian_matrix_with_dot) > 0):  # матрица положительно определенная, точка минимума
                dot['type'] = 'min'  # добавляем в словарь с соответствующей точкой ее тип
            elif np.all(
                    np.linalg.eigvals(
                        hessian_matrix_with_dot) < 0):  # матрица отрицительно определенная, точка максимума
                dot['type'] = 'max'

            else:
                dot['type'] = 'saddle'
            dot['func_value'] = func.subs(dot)
        output_str = ''
        #     for i in range(len(sol_restr)):
        #         output_str += f'({float(sol_restr[i][x]):.3}, {float(sol_restr[i][y]):.3}, ' +\
        #                     f'{float(sol_restr[i]["func_value"]):.3}) - {sol_restr[i]["type"]} \n'

        sol_restr_all = pd.DataFrame(sol_restr_all)

        sol_restr_all.columns = ['x', 'y', 'lam', 'type', 'z']
        sol_restr_all = sol_restr_all.drop(['lam'], axis=1)
        for i in range(len(sol_restr_all)):
            sol_restr_all.loc[i, ['x', 'y', 'z']] = (sol_restr_all.loc[i, ['x', 'y', 'z']].apply(lambda x: sm.N(x, 4)))
        sol_restr = pd.DataFrame(sol_restr)
        sol_restr.columns = ['x', 'y', 'lam', 'type', 'z']
    return sol_restr_all, sol_restr
import numpy as np
import sympy as sm
import pandas as pd

def local_extrema(variab, func, restr):
    """
    Функцция поиска локальных экстремумов функции двух переменных
    :param variab: кортеж состоящий из переменных, которые являются sympy symbols
    :param func: sympy expression
    :param restr: возвращает словарь, где ключом выступают названия переменных,
    значениями являются списки, с ограничивающими интервалами
    :return: Список координат и значение функции в точке, для всех точек локальных экстремумов,
     с указанием типа экстремума (минимум, максимум, седловая точка)
    """
    x, y = sm.symbols('x, y')  # !!! комплексные переменные

    func = func.subs({variab[0]: x, variab[1]: y})  # заменяем переменные во избежание комплексных ответов
    variab1_d = sm.diff(func, x)  # дифференцируем по каждой из переменных
    variab2_d = sm.diff(func, y)

    sol = sm.solve([variab1_d,
                    variab2_d],
                   [x, y], dict=True)  # приравниваем частные производные к нулю и решаем систему

    sol_restr_all = []  # !!!
    sol_restr = []
    for solution in sol:
        if solution[x].is_real and solution[y].is_real:
            if restr[variab[0]][0] <= solution[x] <= restr[variab[0]][1] and \
                    restr[variab[1]][0] <= solution[y] <= restr[variab[1]][1]:
                sol_restr.append(solution)
                sol_restr_all.append(solution)

        else:

            sol_restr_all.append(solution)

    hessian_matrix = sm.hessian(func, [x, y], )  # Hessian matrix

    for dot in sol_restr_all:
        hessian_matrix_with_dot = hessian_matrix.subs(dot)
        hessian_matrix_with_dot = np.array(hessian_matrix_with_dot).astype(complex)

        if np.all(np.linalg.eigvals(hessian_matrix_with_dot) > 0):  # матрица положительно определенная, точка минимума
            dot['type'] = 'min'  # добавляем в словарь с соответствующей точкой ее тип
        elif np.all(
                np.linalg.eigvals(hessian_matrix_with_dot) < 0):  # матрица отрицительно определенная, точка максимума
            dot['type'] = 'max'

        else:
            dot['type'] = 'saddle'
        dot['func_value'] = func.subs(dot)

    for dot in sol_restr:
        hessian_matrix_with_dot = hessian_matrix.subs(dot)
        hessian_matrix_with_dot = np.array(hessian_matrix_with_dot).astype(np.float64)

        if np.all(np.linalg.eigvals(hessian_matrix_with_dot) > 0):  # матрица положительно определенная, точка минимума
            dot['type'] = 'min'  # добавляем в словарь с соответствующей точкой ее тип
        elif np.all(
                np.linalg.eigvals(hessian_matrix_with_dot) < 0):  # матрица отрицительно определенная, точка максимума
            dot['type'] = 'max'

        else:
            dot['type'] = 'saddle'
        dot['func_value'] = func.subs(dot)

    output_str = ''
    if sol == []:
        output_str += 'нет точек экстремума'  # !!!
    else:

        for i in range(len(sol_restr_all)):
            output_str += f'({(sol_restr_all[i][x])},{(sol_restr_all[i][y])},' + \
                          f'{(sol_restr_all[i]["func_value"]):}) - {sol_restr_all[i]["type"]} \n'
        sol_restr_all = pd.DataFrame(sol_restr_all)
        sol_restr_all.columns = ['x', 'y', 'type', 'z']
        for i in range(len(sol_restr_all)):
            sol_restr_all.loc[i, ['x', 'y', 'z']] = (sol_restr_all.loc[i, ['x', 'y', 'z']].apply(lambda x: sm.N(x, 4)))

        sol_restr = pd.DataFrame(sol_restr)
        sol_restr.columns = ['x', 'y', 'type', 'z']

    return sol_restr_all, sol_restr
import pandas as pd


def parabolic_interpolation(func, interval, pression=1e-5, max_iter=500,
                            flag_results=False, flag_data=False, type_opt='min'):
    """
    Функция поиска экстремума функции методом парабол
    :param func: python function
    :param interval: list consisting of float numbers(left and right bounds)
    :param pression: optimization accuracy
    :param max_iter: maximum amount of iterations
    :param flag_results: output of intermediate results
    :param flag_data: recording intermediate results in a dataset
    :param type_opt: type of extrema: if min:flag_opt=1
                                      if max: flag_opt=-1
    :return: extrema:the point at which the extremum
             df: intermediate results in a dataset
    """

    if type_opt == 'min':
        flag_opt = 1
    else:
        flag_opt = -1

    data = []
    df = pd.DataFrame(columns=['iter', 'point', 'function'])
    x0 = interval[0]
    x1 = interval[1]
    x2 = (x0 + x1) / 2

    f0 = flag_opt * func(x0)
    f1 = flag_opt * func(x1)
    f2 = flag_opt * func(x2)
    f_x = {x0: f0, x1: f1, x2: f2}
    x2, x1, x0 = sorted([x0, x1, x2], key=lambda x: f_x[x])

    if flag_data:
        data = [[0, x2, func(x2)]]
    if flag_results:
        print(f"Номер итерации {0}, точка {x2}, функция {func(x2)} .")


    for i in range(max_iter):

        num = (x1 - x2) ** 2 * (f2 - f0) + (x0 - x2) ** 2 * (f1 - f2)
        den = 2 * ((x1 - x2) * (f2 - f0) + (x0 - x2) * (f1 - f2))
        x_extr = x2 + num / den

        if x_extr == x0 or x_extr == x1 or x_extr == x2:
            print('code 2, точка совпала с уже имеющимися')

        if den == 0:
            print('code 2, невозможно вычислить точку')

        if interval[0] > x_extr > interval[1]:
            print('code 2, точка вышла за интервал')

        f_extr = flag_opt * func(x_extr)

        if f_extr < f2:
            x0, f0 = x1, f1
            x1, f1 = x2, f2
            x2, f2 = x_extr, f_extr

        elif f_extr < f1:
            x0, f0 = x1, f1
            x1, f1 = x_extr, f_extr

        elif f_extr < f0:
            x0, f0 = x_extr, f_extr
        if i == 499:
            print('достигнуто максимальное количество итераций code 1')

        elif abs(x1 - x2) < pression and abs(f1 - f2) < pression:
            print('найдено значение с заданной точностью, code 0')
            break

        if flag_data:
            data.append(([i + 1, x_extr, func(x_extr)]))
            df = pd.DataFrame(data, columns=['iter', 'point', 'function'])

        if flag_results:
            print(f"Номер итерации {i + 1}, точка {x_extr}, функция {func(x_extr)}.")


    return x_extr, df
import sympy as sm
import numpy as np
import re

def parse__restr_function(variables):
    '''
    Функция возвращает словарь, где ключом выступают названия переменных,
    значениями являются списки, с ограничивающими интервалами
    :param variables:
    :return: dict: key=variables, value=list
    '''
    restr_function = None
    flag_func = False
    while not flag_func:

        try:
            restr_function = input('Введите  огранеичивающую функцию: ')
            restr_function = sm.parsing.sympy_parser.parse_expr(restr_function.replace('–', '-'))
#             check_var = restr_function.free_symbols.difference(variables)
#             if len(check_var) != 0:
#                 print('Введены лишние переменные')
#                 raise Exception
            flag_func = True
        except Exception:
            print('Ошибка ввода. Введите функцию еще раз: ')
    return restr_function
import sympy as sm
import numpy as np
import re

def parse_restriction(variables):
    '''
    Функция возвращает словарь, где ключом выступают названия переменных,
    значениями являются списки, с ограничивающими интервалами
    :param variables:
    :return: dict: key=variables, value=list
    '''
    restr_val = None
    flag_restriction = False
    while not flag_restriction:
        try:
            restrictions = input('Есть ли ограничения ? 1-да/ 0 – нет : ')
            if len(restrictions.strip()) == 1:
                restrictions = int(restrictions)
            else:
                raise Exception

            restr_val = {}
            if restrictions == 1:
                for var in variables:
                    restr_values = input(f'Введите ограничения по {str(var)}, если нет ограничений-введите 0:  -1 1 ')
                    restr_values = restr_values.strip()  # убираем пробелы в конце и начале
                    if restr_values == '0':
                        restr_val[var] = [-np.inf, np.inf]  # при отстутствии ограничений

                    else:
                        restr_values = restr_values.replace(',', ' ')  # проверка вводов
                        restr_values = re.sub(" +", " ", restr_values)  # убираем лишние пробелы

                        restr_val[var] = list(map(int, restr_values.split(' ')))
                        if len(restr_val[var]) != 2:
                            raise Exception
            elif restrictions == 0:
                for var in variables:
                    restr_val[var] = [-np.inf, np.inf]

            else:
                raise Exception

            flag_restriction = True
        except Exception:
            print('Ошибка ввода: ')
    return restr_val
import sympy as sm
import numpy as np
import re


def parse_variables():
    '''
    Функция возвращает кориеж состоящий из переменных, которые являются sympy symbols
    :return:
    tuple of sympy symbols
    '''
    variables = ''
    flag_vars = False
    while not flag_vars:

        try:
            variables = input('Введите названия переменных, разделенных пробелом: ')
            if '(' in variables or ')' in variables:  # проверка на наличие не предусмотренных символов
                raise Exception
            if ',' in variables:
                variables = sm.parsing.sympy_parser.parse_expr(variables.replace(' ', ''))
                # при наличии ',', приведение к нужному формату убирая пробелы
            else:
                variables = sm.parsing.sympy_parser.parse_expr(variables.replace(' ', ','))
                # приведение к нужному формату
            flag_vars = True

        except Exception:
            print('Ошибка ввода. Введите две переменные через пробел, пример: x y')
    return variables


def parse_function(variables):
    '''
    Запускает парсер функции. Возвращает sympy expression
    :param variables: tuple of sympy symbols
    :return:
    sympy expression
    '''
    function = None
    flag_func = False
    while not flag_func:

        try:
            function = input('Введите функцию: ')
            function = sm.parsing.sympy_parser.parse_expr(function.replace('–', '-'))
            # заменяем минусы
#             check_var = function.free_symbols.difference(variables)
#             # проверяем не содержит ли функция лишние переменные
#             if len(check_var) != 0:
#                 print('Введены лишние переменные')
#                 raise Exception
            flag_func = True
        except Exception:
            print('Ошибка ввода. Введите функцию еще раз: ')
    return function
import sympy as sm
import re


def parse_variables_tz2():
    '''
    Функция возвращает кориеж состоящий из переменной, которая является sympy symbol
    :return:
    tuple of sympy symbol
    '''

    variables = input('Введите названия переменной ')

    return variables


def parse_function_tz2(variables):
    '''
    Запускает парсер функции. Возвращает sympy expression
    :param variables: tuple of sympy symbols
    :return:
    sympy expression
    '''

    function = input('Введите функцию: ')
    function = sm.parsing.sympy_parser.parse_expr(function.replace('–', '-'))
    function = sm.lambdify(variables, function)

    return function


def parse_restriction_tz2(variables):
    '''
    Функция возвращает словарь, где ключом выступают названия переменных,
    значениями являются списки, с ограничивающими интервалами
    :param variables:
    :return: dict: key=variables, value=list
    '''

    restr_values = input(f'Введите ограничения  ')
    restr_values = restr_values.strip()  # убираем пробелы в конце и начале

    restr_values = restr_values.replace(',', ' ')  # проверка вводов
    restr_values = re.sub(" +", " ", restr_values)  # убираем лишние пробелы
    restr_val = restr_values
    restr = restr_val.split()
    interval = [float(restr[0]), float(restr[1])]
    return interval


def parser_task_gr():
    '''
    Функция почередно проверяющая все входные данные
    :return: tuple containing of: tuple, sympy expression, dict
    '''
    variables = parse_variables_tz2()
    func = parse_function_tz2(variables)
    interval = parse_restriction_tz2(variables)
    return variables, func, interval
def parser_task1():
    '''
    Функция почередно проверяющая все входные данные
    :return: tuple containing of: tuple, sympy expression, dict
    '''
    variables = parse_variables()
    func = parse_function(variables)
    restr = parse_restriction(variables)
    return variables, func, restr
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sympy as sm
import pandas as pd

np.seterr(all='ignore')


def plot(variab, func, restr, dots):
    """
    Функция отрисовки графиков функции двух переменных с отображением точек экстремума
    :param variab: кортеж состоящий из переменных, которые являются sympy symbols
    :param func: sympy expression
    :param restr: возвращает словарь, где ключом выступают названия переменных,
    значениями являются списки, с ограничивающими интервалами
    :param dots: pd.Dataframe, состоящий из точек экстремума и их типа. Столбцы: x, y, type, z
    :return: go.Figure содержаший два графика: поверхность функции и линии уровня
    """

    x, y = variab
    if isinstance(dots, pd.DataFrame):
        if restr[x] == [-np.inf, np.inf]:  # определяем ограничения по осям
            x_min = float(dots.x.min())
            x_max = float(dots.x.max())

            x_min = x_min - max((x_max - x_min) * 0.1, 1)  # во избежание отрисовки точек на границах графика
            x_max = x_max + max((x_max - x_min) * 0.1, 1)
        else:
            x_min = restr[x][0]
            x_max = restr[x][1]

        if restr[y] == [-np.inf, np.inf]:
            y_min = float(dots.y.min())
            y_max = float(dots.y.max())
            y_min = y_min - max((y_max - y_min) * 0.1, 1)
            y_max = y_max + max((y_max - y_min) * 0.1, 1)
        else:
            y_min = restr[y][0]
            y_max = restr[y][1]

        cnt_dots = 100
        # возвращаем sympy функцию к python функции,  в которую можно передать х,у позиционно
        func = sm.lambdify([x, y], func)
        # значения для подстановки в функцию
        x, y = np.linspace(x_min, x_max, cnt_dots), np.linspace(y_min, y_max, cnt_dots)

        z = np.zeros((cnt_dots, cnt_dots))
        for i in range(cnt_dots):
            for j in range(cnt_dots):
                z[i, j] = func(x[i], y[j])  # значения функции

        fig = make_subplots(rows=1, cols=2,
                            specs=[[{'is_3d': True}, {'is_3d': False}]],
                            subplot_titles=('Поверхность', 'Линии уровня'))  # создаем фигуру
        fig.add_trace(go.Surface(z=z.T, x=x, y=y, colorscale='pinkyl', opacity=0.7),
                      1, 1)  # добавляем саму поверхность функции
        fig.add_trace(go.Scatter3d(z=dots.z.astype(float), x=dots.x.astype(float),
                                   y=dots.y.astype(float), showlegend=False, mode='markers'), 1, 1)  # точки экстремума
        fig.add_trace(go.Contour(z=z.T, x=x, y=y, showscale=False, colorscale='pinkyl'),
                      1, 2)  # линии уровня
        fig.add_trace(go.Scatter(x=dots.x.astype(float), y=dots.y.astype(float),
                                 showlegend=False, mode='markers'), 1, 2)  # точки экстремума

    else:
        cnt_dots = 101
        # возвращаем sympy функцию к python функции,  в которую можно передать х,у позиционно
        func = sm.lambdify([x, y], func)
        # значения для подстановки в функцию
        x, y = np.linspace(-1, 1, cnt_dots), np.linspace(-1, 1, cnt_dots)  # !!!

        z = np.zeros((cnt_dots, cnt_dots))
        for i in range(cnt_dots):
            for j in range(cnt_dots):
                #                 if y[j]==0:  #!!!
                #                     z[i, j] = np.nan
                #                 else:

                z[i, j] = func(x[i], y[j])  # значения функции
        fig = make_subplots(rows=1, cols=2,
                            specs=[[{'is_3d': True}, {'is_3d': False}]],
                            subplot_titles=('Поверхность', 'Линии уровня'))  # создаем фигуру
        fig.add_trace(go.Surface(z=z.T, x=x, y=y, colorscale='pinkyl', opacity=0.7),
                      1, 1)  # добавляем саму поверхность функции

        fig.add_trace(go.Contour(z=z.T, x=x, y=y, showscale=False, colorscale='pinkyl'),
                      1, 2)  # линии уровня

        fig.update_layout(scene=dict(
            xaxis_title='X у. е.',
            yaxis_title='Y у. е.',
            zaxis_title='Z у. е.')  # подписи осей

        )
        fig.update_xaxes(title_text="X у. е.", row=1, col=2)
        fig.update_yaxes(title_text="Y у. е.", row=1, col=2)

    return fig
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

def plot(func, interval):
    """
       Функция отрисовки графиков функции двух переменных с отображением точек экстремума
       :param func: sympy expression
       :param interval: интервал функции
       :return: go.Figure содержаший два графика: поверхность функции и линии уровня
       """

    fig = px.scatter(df, x='point', y='function', size='size',
                     animation_frame='iter',
                     size_max=7,
                     title='График функции')
    x_ax = np.linspace(interval[0], interval[1], 200)
    y_ax = func(x_ax)
    fig.add_trace(go.Scatter(x=x_ax, y=y_ax, name='функция'))

    fig.update_layout(
        xaxis_title='значение х, у.е.',
        yaxis_title='значении f(x) у.е.')
    return fig