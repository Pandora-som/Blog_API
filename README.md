**Блог-платформа API**

Проект представлен в качестве API для блог-платформы (Вариант-2),
который включает в себя ключевые элементы управления и реализует
следующий функционал:

-   Работа со статьями (получение статей с возможностью их фильтрации и
    пагинации, получение статьи по id, создание, редактирование и
    удаление статей)

-   Работа с комментариями (получение всех комментариев, получение
    комментария по id, создание, редактирование и удаление комментариев)

-   Работа с категориями (получение всех категорий, получение категории
    по id, создание, редактирование и удаление категорий)

Дополнительной функцией является возможность добавления лайков к статьям
и сортировка по популярности.

Также данный API поддерживает разделение пользователей на роли
(читатель, автор, модератор).

Для авторизаци используется заголовок Authorization со значением Bearer {"token": "Токен, полученный в api/login"}

Данные для входа:

-   Читатель:
    name: Ami-reader
    password: AmiReader

-   Автор:
    name: Ami-avtor
    password: AmiAvtor

-   Модератор:
    name: Ami-moderator
    password: AmiModerator

**Используемые технологии и их версии:**

Для разработки API был использован веб-фреймворк FastAPI 0.113.0, а
также библиотеки:

-   sqlalchemy 2.0.41

-   pydantic-settings 2.9.1

-   passlib 1.7.4

-   PyJWT 2.10.1

-   bcrypt 4.3.0

**Инструкция по запуску:**

1.  Создание. venv: python -m venv .venv

2.  Активация. venv:

source ./venv/bin/activate -- для Linux

.venv\\Scripts\\activate -- для Windows

3.  Установка зависимостей: pip install -r requirements.txt

4.  Запуска посева: python seed.py

5.  Запуск проекта: fastapi dev main.py

**Описание API**

Методология: Restful API

Способ передачи данных: через URL/в теле запроса

Документация: <http://127.0.0.1:8000/docs>

---

| Метод и маршрут                   | Параметры / Тело запроса                                                                    | Правила валидации                                                                     |
| --------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **GET /api/posts**                | `limit: int = 10`                                                                           | `limit < 100` — ограничение количества статей                                         |
|                                   | `page: int = 1`                                                                             | `page >= 1` — нумерация страниц                                                       |
|                                   | `category: Optional[str]`                                                                   | Если указан — фильтрация по категории                                                 |
|                                   | `status: Optional[str]`                                                                     | Если указан — фильтрация по статусу                                                   |
|                                   | `order_by: Optional[str] = "desc"`                                                                    | `"asc"` или `"desc"` — сортировка по количеству лайков если указан                                |
| **GET /api/post/{id}**            | —                                                                                           | Статья с ID должна существовать                                                       |
| **POST /api/posts**               | `title`, `content`, `date_publication`, `status_id`, `author_id`, `category_id`             | Все поля обязательны; проверка существования автора                                   |
| **PUT /api/post/{id}**            | `title`, `content`, `date_publication`, `status_id`, `author_id`, `category_id`, `likes_id` | Только автор или модератор; если роль модератор — можно обновлять лайки по `likes_id` |
| **DELETE /api/post/{id}**         | —                                                                                           | Только автор или роль модератор; проверка существования статьи                        |
| **PATCH /api/post/{id}/like**     | —                                                                                           | Статья должна существовать; пользователь не должен был ставить лайк                   |
| **PATCH /api/post/{id}/unlike**   | —                                                                                           | Статья должна существовать; пользователь **должен был** ставить лайк                  |
| **POST /api/register**            | `name`, `email`, `password`, `role_id`                                                      | Имя пользователя должно быть уникальным; пароль хэшируется                            |
| **POST /api/login**               | `name`, `password`                                                                          | Пользователь должен существовать; верификация пароля                                  |
| **GET /api/comments**             | —                                                                                           | Если комментариев нет — ошибка `404`                                                  |
| **GET /api/comment/{id}**         | —                                                                                           | Комментарий должен существовать                                                       |
| **POST /api/comment**             | `text`, `date`, `state_id`, `user_id`                                                       | Статья и пользователь должны существовать                                             |
| **PUT /api/comment/{id}**         | `text`, `date`, `state_id`, `user_id`                                                       | Только автор или роль модератор; проверка ID статьи, пользователя и комментария       |
| **DELETE /api/comment/{id}**      | —                                                                                           | Только автор или роль модератор; проверка существования комментария                   |
| **GET /api/categories**           | —                                                                                           | —                                                                                     |
| **GET /api/category/{id}**        | —                                                                                           | Проверка существования категории                                                      |
| **POST /api/category/{name}**     | —                                                                                           | Только модератор; имя категории должно быть уникальным                                |
| **PUT /api/category/{id}/{name}** | —                                                                                           | Только модератор; новая категория не должна дублировать существующую                  |
| **DELETE /api/category/{id}**     | —                                                                                           | Только модератор; проверка существования категории                                    |                                              |

**Описание ролей пользователей и их прав:**

Читатель -- чтение всех статей, возможность оставлять комментарии,
редактировать и удалять их, возможность поставить и удалить свой лайк на
статью.

Автор -- создание статей, редактирование своих статей (кроме лайков),
удаление своих статей.

Модератор -- управление (создание, редактирование, удаление) всеми
статьями и комментариями.

**Контакты:**

e-mail: <testirovsik0005@mail.ru>

Номер телефона: +7 906 814 37 89
