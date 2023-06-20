# FishBot

Боты предназначены для викторины: "вопрос-ответ"

#### Пример работы бота [Телеграм](https://t.me/spv_quiz_bot)

#### Требования перед установкой:
1. Создайте бота в телеграм - напишите отцу ботов [@BotFather](https://t.me/BotFather)
2. Аналогично создайте еще одного бота - он будет высылать вам отчеты об ошибках
3. Получите ID своего чата - в него будут приходить сообщения об ошибках [@userinfobot](https://t.me/userinfobot)
4. Зарегистрируйтесь на сайте [elasticpath](https://www.elasticpath.com/) создайте магазин с товарами
5. Получите _API Base URL, Client ID и Client Secret_ на вкладке _Application Keys_
6. Получите url, порт и пароль для подключения к облачному сервису [Redis](https://redis.com/) 

[Установите Python](https://www.python.org/), если этого ещё не сделали.

Проверьте, что `python` установлен и корректно настроен. Запустите его в командной строке:
```sh
python --version
```
**Важно!** Версия Python должна быть не ниже 3.9.

Возможно, вместо команды `python` здесь и в остальных инструкциях этого README придётся использовать `python3`. Зависит это от операционной системы и от того, установлен ли у вас Python старой второй версии.

#### Установка и запуск:
Скопируйте файлы из репозитория в папку:
```sh
git clone https://github.com/spawlov/FishBot.git
```

В каталоге проекта создайте виртуальное окружение:
```sh
python -m venv venv
```
Активируйте его. На разных операционных системах это делается разными командами:

- Windows: `.\venv\Scripts\activate`
- MacOS/Linux: `source venv/bin/activate`

В корне проекта создайте файл _.env_ со следующим содержимым:

```text
API_BASE_URL=<Здесь укажите ваш API Base URL>
CLIENT_ID=<Здесь укажите ваш Client ID>
CLIENT_SECRET=<Здесь укажите ваш Client Secret>

SHOP_BOT=<Токен вашего бота в телеграм>

LOGGER_BOT_TOKEN=<Токен вашего бота-логгера в телеграм>
LOGGER_CHAT_ID=<ID вашего чата, в который будут прилодить сообщения от логера>

REDIS_HOST=<URL для подключения к Redis>
REDIS_PORT=<Порт для подключения к Redis>
REDIS_PASSWORD=<Пароль для Redis>
```

Установите зависимости:

```sh
pip install -r requirements.txt
```

Запуск бота осуществляется командой:

```sh
python main.py
```