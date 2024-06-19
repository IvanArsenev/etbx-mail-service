# ETBX mail service
 

## API
 

### `POST http://etbx.ru:7070/register`
 
Запрос для регистрации пользователя в почте `@pmc-python.ru`
 
**Параметры:**
 

    {
        "name":"Имя",
        "surname":"Фамилия",
        "birthday":"Дата рождения (формат 31-01-2000)",
        "gender":"Пол (М или Ж)",
        "mail":"Выбранная почта (Пример: test)",
        "phone_num": "Номер телефона (не обязательно)",
        "password": "Пароль"
    }

**Возвращает:**
 

    {
        "token" : "токен пользователя"
    }


### `POST http://etbx.ru:7070/login`
 
**Параметры:**

 
    {
        "email": "Логин с указателем почты. Например: test@pmc-python.ru",
        "password": "Пароль"
    }

**Возвращает:**
 

    {
        "token" : "токен пользователя"
    }


### `POST http://etbx.ru:7070/logout`
 
Функция выхода из аккаунта (выполняется с использованием **Bearer Token)**
 
**Возвращает:**
 

    Сообщение об успешном выходе из аккаунта (токен деактивируется)


### `PUT http://etbx.ru:7070/edit_avatar`
 
Функция добавления аватара пользователя (выполняется с использованием Bearer Token). Если размеры некорректны, то измняет их до 512x512 px
 
**Параметры (form-data):**
 

    {
        "avatar": File.png
    }

**Возвращает:**
 

    {
        "message": "Аватар успешно обновлен"
    }

### `GET http://etbx.ru:7070/users/me`
 
Функция просмотра данных своего профиля (выполняется с использованием **Bearer Token)**
 
**Возвращает:**
 

    {
        "id": id_пользователя,
        "Имя": "Имя",
        "Фамилия": "Фамилия",
        "Дата рождения": "В формате ДД.ММ.ГГГГ",
        "Пол": "М или Ж",
        "Логин": "Логин",
        "Номер_телефона": "Номер телефона или 'Отсутствует', если его нет",
        "Аватар": Путь к изображению или null,
        "token": "Токен пользователя"
    }

### `PUT http://etbx.ru:7070/edit`
 
Функция изменения данных в профиле (выполняется с использованием **Bearer Token)**
 
**Параметры:**
 

    {
        "name":"Имя (не обязательно)",
        "surname":"Фамилия (не обязательно)",
        "birthday":"Дата рождения (не обязательно)",
        "gender":"Пол (не обязательно)",
        "mail":"Выбранная почта (не обязательно)",
        "phone_num": "Номер телефона (не обязательно)",
        "password":"Пароль (не обязательно)"
    }

**Возвращает:**
 

    Сообщение об успешном изменении данных


### `GET http://etbx.ru:7070/avatars/{id}/`
 
Функция просмотра аватара пользователя с id id (выполняется с использованием **Bearer Token)**
 
**Параметры:**
 

    [ID пользователя]

**Возвращает:**
 

    [Изображение аватара]


### `GET http://etbx.ru:7070/users/{id}/`
 
Функция просмотра данных пользователя (выполняется с использованием **Bearer Token)**
 
**Параметры:**
 

    [ID пользователя]

**Возвращает:**
 

    {
        "id": ID пользователя,
        "Имя": "Имя",
        "Фамилия": "Фамилия",
        "Дата рождения": "дата в формате ДД.ММ.ГГГГ",
        "Пол": "М или Ж",
        "Логин": "Логин",
        "Номер_телефона ": "Номер телефона или 'Отсутствует', если его нет",
        "Аватар":  Путь к изображению или null,
    }

### `GET http://etbx.ru:7070/users?page=1&page_size=1`
 
Функция просмотра данных пользователей (выполняется с использованием **Bearer Token)**
 
**Возвращает:**
 

    {
        "total_users": 1,
        "users": [
            {
                "id": ID пользователя,
                "Имя": "Имя",
                "Фамилия": "Фамилия",
                "Дата рождения": "Дата в формате ДД.ММ.ГГГГ",
                "Пол": "М или Ж",
                "Логин": "Логин",
                "Номер телефона": "Номер телефона или 'Отсутствует', если его нет",
                "Аватар":  Путь к изображению или null,
            },
            ...
        ]
    }


### `GET http://etbx.ru:7070/messages/{folder}`
 
Функция получения сообщений из папки (выполняется с использованием **Bearer Token)**

Доступные папки: 

    inbox - Входящие сообщения
    Sent - Отправленные сообщения
    Drafts - Черновики
    Trash - Корзина
    noread - непрочитанные

**Возвращает:**


    {
        "messages": [
            {
                "id": id сообщения 1,
                "Тема": "Тема сообщения 1",
                "Сообщение": "Текст сообщения 1",
                "Отправитель": "отправитель 1@etbx.ru",
                "Получатель": "получатель 1@etbx.ru",
                "Время получения": "24:59 31.12.2024 "
            },
            {
                "id": id сообщения 2,
                "Тема": "Тема сообщения 2",
                "Сообщение": "Текст сообщения 2",
                "Отправитель": "отправитель 2@etbx.ru",
                "Получатель": "получатель 2@etbx.ru",
                "Время получения": "22:40 31.12.2024 "
            },
            ...
        ]
    }


### `POST http://etbx.ru:7070/send`
 
Функция отправки сообщения пользователю (выполняется с использованием **Bearer Token)**
 
**Параметры:**
 

    {
        "theme": "Тема сообщения (не обязательно)",
        "body": "Текст сообщения",
        "reciever": "Адрес получателя (пример: test@etbx.ru)"
    }

**Возвращает:**
 

    Сообщение об успешной отправки сообщения
