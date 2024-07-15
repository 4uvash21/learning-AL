import os
import ydb

YDB_ENDPOINT = os.getenv("YDB_ENDPOINT")
YDB_DATABASE = os.getenv("YDB_DATABASE")


def get_ydb_pool(ydb_endpoint, ydb_database, timeout=30):
    ydb_driver_config = ydb.DriverConfig(
        ydb_endpoint,
        ydb_database,
        credentials=ydb.credentials_from_env_variables(),
        root_certificates=ydb.load_ydb_root_certificate(),
    )

    ydb_driver = ydb.Driver(ydb_driver_config)
    ydb_driver.wait(fail_fast=True, timeout=timeout)
    return ydb.SessionPool(ydb_driver)


def _format_kwargs(kwargs):
    return {"${}".format(key): value for key, value in kwargs.items()}


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_update_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )

    return pool.retry_operation_sync(callee)


# Заготовки из документации
# https://ydb.tech/en/docs/reference/ydb-sdk/example/python/#param-prepared-queries
def execute_select_query(pool, query, **kwargs):
    def callee(session):
        prepared_query = session.prepare(query)
        result_sets = session.transaction(ydb.SerializableReadWrite()).execute(
            prepared_query, _format_kwargs(kwargs), commit_tx=True
        )
        return result_sets[0].rows

    return pool.retry_operation_sync(callee)

# Зададим настройки базы данных
pool = get_ydb_pool(YDB_ENDPOINT, YDB_DATABASE)


# Структура квиза
quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': ['Язык программирования', 'Тип данных', 'Музыкальный инструмент', 'Змея на английском'],
        'correct_option': 0
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': ['int', 'float', 'str', 'natural'],
        'correct_option': 0
    },
    {
        'question': 'Чем отличаются операторы = и ==?',
        'options': ['операторы эквивалентны', 'оператор = менее точный', "оператор = присваивает значения, а == сравнивает их"],
        'correct_option': 2
    },
    {
        'question': 'Данные какого типа возвращает встроенная функция input()?',
        'options': ['логический тип', 'строка', "целое число"],
        'correct_option': 1
    },
    {
        'question': 'Какие из представленых литералов чисел относятся к типу float?',
        'options': ['1.7+4.3j', '5.0', "88"],
        'correct_option': 1
    },
    {
        'question': 'Какой оператор используется для получения остатка от деления в Python?',
        'options': ['//', '/', "%"],
        'correct_option': 2
    },
    {
        'question': 'Какая из встроенных функций Python может быть использована для нахождения модуля числа?',
        'options': ['pow', 'round', "abs"],
        'correct_option': 2
    },
    {
        'question': 'Какой из операторов используется для повторения строки в Python?',
        'options': ['*', '+', "/"],
        'correct_option': 0
    },
    {
        'question': 'Какой из методов используется для преобразования строки в верхний регистр?',
        'options': ['capitalize()', 'upper()', "lower()"],
        'correct_option': 1
    },
    {
        'question': 'Что возвращает функция len() при передаче в неё строки?',
        'options': ['количество символов', 'количество слов', "количество байт"],
        'correct_option': 0
    },
]
