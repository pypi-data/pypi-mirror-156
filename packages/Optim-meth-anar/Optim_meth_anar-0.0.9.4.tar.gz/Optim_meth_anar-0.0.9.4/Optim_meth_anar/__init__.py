from . import utils

utils.__doc__ = """
Lagrange
Поиск локальных экстремумов функции двух переменных с ограничениями (метод Лагранжа);
:param variab: кортеж состоящий из переменных, которые являются sympy symbols
:param func: sympy expression
:param restr: возвращает словарь, где ключом выступают названия переменных,
значениями являются списки, с ограничивающими интервалами
:param restr_func: sympy expression
:return: Список координат и значение функции в точке, для всех точек локальных экстремумов,
с указанием типа экстремума (минимум, максимум, седловая точка)

brent
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

golden_ratio
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

parse_variables_tz2
Функция возвращает кориеж состоящий из переменной, которая является sympy symbol
    :return:
    tuple of sympy symbol

parabolic_interpolation
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

plot
Функция отрисовки графиков функции двух переменных с отображением точек экстремума
     :param variab: кортеж состоящий из переменных, которые являются sympy symbols
     :param func: sympy expression
     :param restr: возвращает словарь, где ключом выступают названия переменных,
     значениями являются списки, с ограничивающими интервалами
     :param dots: pd.Dataframe, состоящий из точек экстремума и их типа. Столбцы: x, y, type, z
     :return: go.Figure содержаший два графика: поверхность функции и линии уровня
Anastaisha Kalmykova [https://pypi.org/project/Anar/]
anariem@mail.ru
"""

from .utils.brent import *