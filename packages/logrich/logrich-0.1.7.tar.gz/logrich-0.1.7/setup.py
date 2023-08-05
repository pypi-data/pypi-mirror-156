# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['logrich']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.6.0,<0.7.0',
 'pydantic[dotenv]>=1.9.1,<2.0.0',
 'rich>=12.4.4,<13.0.0',
 'toml==0.10.2',
 'watchdog==2.0.3']

setup_kwargs = {
    'name': 'logrich',
    'version': '0.1.7',
    'description': 'loguru + rich = logrich',
    'long_description': '### Логгер\n\n#### Совместная работа [loguru](https://loguru.readthedocs.io) & [rich](https://rich.readthedocs.io).\n\n[Screenshot logger](https://disk.yandex.ru/i/JexFefETxnJavA)\n\n![Screenshot logger](wiki/screenshot_logger.png?raw=True "Screenshot")\n\nУровень вывода исключений определяется в переменных окружения.\nЦвета, ширины и шаблоны вывода также могут быть определены в окружении.\n\nОбработчики записей логов можно определять дополнительно, например запись в файл или отправка в канал.\n\n#### Как развернуть:\n\n```shell\ngit clone \ncd logrich\npoetry shell\npoetry install\n```\n\n#### Запустить тест(ы):\n\n```shell\npytest\n# монитор тестов\nptw\n```\n',
    'author': 'Dmitry Mavlin',
    'author_email': 'mavlind@list.ru',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
