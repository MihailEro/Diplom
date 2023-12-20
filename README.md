# Дипломная работа

##  Задание: Сервис авторизации по номеру телефона

* Авторизация по номеру телефона. Первый запрос на ввод номера телефона. Имитировать отправку 4хзначного кода авторизации(задержку на сервере 1-2 сек). Второй запрос на ввод кода
* Если пользователь ранее не авторизовывался, то записать его в бд
* Если пользователь ранее не авторизовывался, то записать его в бд
* Пользователю нужно при первой авторизации нужно присвоить рандомно сгенерированный 6-значный инвайт-код(цифры и символы)
* В профиле у пользователя должна быть возможность ввести чужой инвайт-код(при вводе проверять на существование). В своем профиле можно активировать только 1 инвайт код, если пользователь уже когда-то активировал инвайт код, то нужно выводить его в соответсвующем поле в запросе на профиль пользователя
* В API профиля должен выводиться список пользователей(номеров телефона), которые ввели инвайт код текущего пользователя.


## Для работы с проектом:

* Создать виртуальное окружение
```
python -m venv env
```
* активировать его
```
env\Scripts\activate
```
* Создать файл .env (пример в .env.sample)
* Создать базу данных
* Установить зависимости
```
pip install -r requirements.txt
```
* Создать и выполнить миграции
```
python manage.py makemigrations

python manage.py migrate
```
* Запустить сервер
```
python manage.py runserver
```

### К проекту приложена коллекция запросов Postman
### Для удобного тестирования проект так же залит на 
```
https://www.pythonanywhere.com
```

## В проекте использованы тезнологии:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Postman](https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=postman&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
