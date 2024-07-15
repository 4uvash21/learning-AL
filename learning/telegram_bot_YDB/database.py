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
        'question': 'Что произойдет, если вы попытаетесь использовать Python как летающий ковер?',
        'options': [
            'Он начнет исполнять код в воздухе',
            'Вы получите ошибку `IndentationError: unexpected unindent',
            'Он превратится в реальную змею',
            'Вы полетите на PyCon'],
        'correct_option': 1
    },
    {
        'question': 'Что Python скажет другим языкам программирования на вечеринке?',
        'options': [
            'Я могу выполнять все ваши задачи одной левой', 
            'У меня есть библиотека для этого', 
            'Почему все так любят мои декораторы?', 
            'Давайте не будем об ошибках'],
        'correct_option': 1
    },
    {
        'question': 'Как Python решает проблемы с зависимостями?',
        'options': [
            'Он использует `pip` как волшебную палочку',
            'Он просто удаляет все и начинает сначала',
            'Он пишет PEP о том, как все должно работать',
            'Он устраивает сессию с медитацией для кода'],
        'correct_option': 0
    },        
    {
        'question': 'Что делает Python, когда ему скучно?',
        'options': [
            'Играет в змейку на собственном терминале',
            'Пишет асинхронные haiku',
            'Организует встречу со всеми своими фреймворками',
            'Смотрит туториалы по себе на YouTube'],
        'correct_option': 3
    },
    {    
        'question': 'Как Python предпочитает свой кофе?',
        'options': [
            'В виде Java',
            'С декораторами',
            'С байт-кодом на дне',
            'В виде Pythonic way latte'],
        'correct_option': 3
    },    
    {
        'question': 'Что Python делает перед сном?',
        'options': [
            'Проверяет, нет ли утечек памяти',
            'Читает PEP перед сном',
            'Медитирует, чтобы собрать сборщик мусора',
            'Пишет дневник обо всех исправленных ошибках'],
        'correct_option': 1
    },
    {
        'question': 'Какой закон физики Python нарушает чаще всего?',
        'options': [
            'Закон сохранения энергии, потому что он такой эффективный',
            'Закон гравитации, потому что он всегда в облаках',
            'Закон всемирного тяготения, потому что он притягивает всех разработчиков',
            'Ни один, Python уважает все законы'],
        'correct_option': 3
    },    
    {
        'question': 'Что бы сказал Python, если бы умел говорить?',
        'options': [
            "Я люблю упрощать сложное",
            "Мой Zen лучше вашего",
            "Давайте все будем дружить с отступами",
            "Все вышеперечисленное"],
        'correct_option': 2    
    },
    {
        'question': 'Какой самый популярный спорт среди Python-разработчиков?',
        'options': [    
            'Дебаггинг марафон',
            'Спринт по написанию кода',
            'Прыжки через версии',
            'Синхронное программирование'],
        'correct_option': 2    
    },
    {
        'question': 'Что было бы, если бы Python-скрипты взбунтовались?',
        'options': [    
            'Они бы начали исполняться в обратном порядке',
            'Они бы стерли все комментарии',
            'Они бы написали PEP о своих правах',
            'Они бы устроили (острое) сражение с другими языками'],
        'correct_option': 1   
    }
]    
