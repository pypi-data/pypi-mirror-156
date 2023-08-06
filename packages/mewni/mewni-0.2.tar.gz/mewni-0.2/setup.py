# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mewni',
 'mewni.cli',
 'mewni.core',
 'mewni.core.templates',
 'mewni.templates.project',
 'mewni.templates.project.bot',
 'mewni.templates.project.bot.config',
 'mewni.templates.project.bot.controllers',
 'mewni.templates.project.bot.filters',
 'mewni.templates.project.bot.middlewares',
 'mewni.templates.project.bot.models',
 'mewni.templates.project.bot.services',
 'mewni.templates.project.bot.stores',
 'mewni.templates.project.bot.templates',
 'mewni.templates.project.bot.types',
 'mewni.templates.project.bot.utils',
 'mewni.tests',
 'mewni.types',
 'mewni.utils']

package_data = \
{'': ['*'],
 'mewni': ['templates/*'],
 'mewni.templates.project.bot': ['locales/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'Werkzeug>=2.1.2,<3.0.0',
 'aiogram>=2.2.0',
 'aioredis>=2.0.1',
 'aioschedule>=0.5.2,<0.6.0',
 'click>=8.1.3,<9.0.0',
 'cogapp>=3.3.0,<4.0.0',
 'environs>=9.5.0',
 'peewee>=3.14.10']

entry_points = \
{'console_scripts': ['mewni = mewni.cli:main', 'ni = mewni.cli:main']}

setup_kwargs = {
    'name': 'mewni',
    'version': '0.2',
    'description': 'Telegram bot framework',
    'long_description': '# Mewni is the python telegram bot framework \n\n## Установка\nПоддерживаемая версия - `Python 3.10` и выше\n\nВажно! Если вы на Windows, то запускаете скрипт ниже из консоли запущенной с правами админимтратора, иначе скрипт не добавится в переменную `PATH` и команды `ni` и `mewni` работать не будут.\n\nНапишите `pip install mewni` для установки пакета из [PyPI](https://pypi.org).\n\nДля разработки этого пакета требуется установить [Poetry](https://python-poetry.org/) командой `pip install poetry`. Обязательно посмотрите [документацию](https://python-poetry.org/docs/) этого пакетного менеджера!\n\nНапишите `ni init superbot` для инициализации проекта.\n\n## Проект\n### Конфигурация\n`bot/config/env.py` Файл для описния переменных среды. \n\n```python\nclass EnvConfig:\n    BOT_NAME: str\n    BOT_TOKEN: str\n    ADMINS: list[int]\n\n    APP_HOST: str = \'localhost\'\n    APP_PORT: int = 8443\n    DB_HOST: str\n    DB_PORT: int\n    DB_NAME: str\n    DB_USER: str\n    DB_PASSWORD: str\n```\nВзгляните на этот кусок кода:\n```python\nAPPHOST: str = \'localhost\'\n```\n`APP_HOST` это поле класса в которое будет подргужено значение из файла `.env` по ключу `APP_HOST`. \n\n`str` означает, что при подргрузке переменной, ее значение будет приведено к этому типу. \n\n`\'localhost\'` - это значение по умолчанию, которое будет использовано в случае отсутствия ключа или его значения в файле `.env`\n## Контроллеры \n`bot/controllers` - папака для контроллеров\nВсе контроллеры подгружаются и регистрируются автоматически при инициализации приложения.\n\n```python\nfrom mewni import command, send\nfrom bot.config import config\n\n\n@command\nasync def start():\n  await send(f\'Application started at {config.APP_HOST}:{config.APP_PORT}\')\n```\n`@command` - это декоратор, который помечает обработчик команд `start()` как команду. Если вы отправите боту `/start`, то он исполнит тело этого обработчика.\nПо умочанию за имя команду принимается название функции. Вы также можете изменить его изменив значение параметра `name`.\nДля добавления описания функции, которое будет отображатся в списке команд Telegram, используйте поле `description`.\n```python\n@command(name=\'start\', description=\'Start this bot for you\')\ndef rename_me(): pass\n```\n\n`send()` - функция, которая отсылает текст пользователю бота, который вызвал обработку этого коллбека. \n### Получение данных от пользователя \nДля получения данных и текста введеного пользователем, вызовите функцию `message()`\n```python\nfrom mewni import command, message\n\n@command\nasync def start():\n    msg = message()\n    print(msg)\n```\n### Запрос данных у пользователя \n`ask()` Отсылает сообщение с просьбой ввести информацию и возвращает обьект сообщения с этой информацией.\n\n```python\nfrom mewni import command, ask, send\n\n\n@command\nasync def start():\n  name_msg = await ask(\'Введите ваше имя\')\n  age_msg = await ask(\'Теперь введите ваш возраст\')\n\n  print(name_msg)\n  print(age_msg)\n\n  send(f\'Привет {name_msg.text}, которому {age_msg.text} лет\')\n```\n### Другие декораторы для создания контроллеров\n`@startup` - Запускает обработчик при запуске приложения \n\n`@halt` - Запускает обработчик при остановке приложения\n\n`@hear` - Запускает обработчик при получение сообщения с обычным текстом текста\n\n\n## Хранение данных вне обработчиков\nДля сохранения данных введенных пользователем между вызовами разных обработчиков, нужно использовать `UserStore`\n```python\n# bot/stores/user.py\nfrom mewni import UserStore\n\nclass User(UserStore):\n    # \'Петр\' и 10 - это значение по умолчанию \n    name: str = \'Рома\'\n    age: int = 16\n```\n```python\n# bot/controllers/start.py\nfrom mewni import ask, command\nfrom bot.stores.User import User\n\n@command\nasync def start():\n    name = await ask(\'Введите ваше имя\')\n    age = await ask(\'Введите ваш возраст\')\n    user = User()\n    user.name = name.text, \n    user.age = int(age.text)\n\n@command\nasync def info():\n    user = User()\n    await send(f\'Привет {user.name}, которому {user.age} лет\')\n```\nЗдесь класс `User` - сохраняет данные не глобально для всех пользователей, а локально именно для этого пользователя в хранилеще по `id` его чата в `Storage`. По умолчанию используется `MemoryStorage`, но потом мы добавим `RedistStorage`, `MongoStorage` и `FileStorage`\n\n`UserStore.clear()` - востанавливает значение хранилища к значениям по умолчанию, если их нет, то удаляет все данные для этого пользователя.\n`UserStore.delete()` - полностью удаляет данные этого хранилища для этого пользователя.\n\n## Tasks\n- Implement modules autoimport \n- [ ] Implement method `select(message: str, enum: Enum)` which send a message with selection and return option of enum and map selected option to value\n- [ ] Implement `LocalStorage()` with the same syntax `name, email, age = LocalStore()` which create storage for each user. For implementation need to use python AST.\n- [ ] Make architecture for this project\n- [ ] Refactor all project\n- [ ] Make documentation better\n- [ ] Make errors better\n- [ ] Make using Config class from project for type auto complete\n- [ ] Add code formatter - black\n- [ ] Set name to "bot" folder the same as project\n- [ ] Make plugin system\n- [ ] Add Template renderer\n- [ ] Add `@startup`, `@stop` decorators\n- [ ] Add `@hear` decorator\n- [ ] Add the ability to work with inline query\n- [ ] Add checking for existence value in .env file. If value is not defined then raise error\n- [ ] Colorize output\n- [ ] Make beautiful serve message\n- [ ] Add the ability to adding other threads to app\n- [ ] Add `@middleware` decorator\n- [ ] Add `@filter` decorator\n- [ ] Add questions to init project command\n- [ ] Add auto db injection to peewee models\n- [ ] Change every event syntax\n- [ ] Implement overwrite default `/help` command text and reaction for it\n- [ ] Implement `/myuserid` command for improve user experience\n- [ ] Implement `setcommand()` function for showing commands at list\n- [ ] Schedulling with localization\n- [ ] Add logging with structuring for years, month and days\n- [ ] Buy website for mewni project\n- [ ] Make additional cli commands:\n  - [ ] `generate` - generate something project items\n  - [ ] `start` - start server\n  - [ ] `dev` - start server with auto reloading\n  - [ ] `build` - compile all project to one .pyc file\n  - [ ] `deploy` - deploy bot to mewni server\n  - [ ] `auth` - authorize for mewni server for deploy\n- [ ] Implement plugins:\n  - [ ] Role plugin\n  - [ ] Admin plugin\n  - [ ] Analytic plugin\n  - [ ] Payment plugin\n- [ ] Add notification about startup and stopping for bot admins\n- [ ] Detach Mewni from specific service (Telegram) and make it universe:\n  - [ ] Telegram\n  - [ ] WhatsApp\n  - [ ] Discord\n  - [ ] Github\n  - [ ] Twitter and others social networks\n- [ ] Draw logotype for Mewni project\n- [ ] Add choosing between requirements.txt and pyproject.toml files (poetry and pip options).',
    'author': 'Danil Sokolov',
    'author_email': 'danilzyx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sejjax/mewni',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10',
}


setup(**setup_kwargs)
