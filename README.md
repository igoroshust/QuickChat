## Установка программы

1. Скачайте проект;
2. Откройте консоль (cmd) от имени администатора;
3. Перейдите по пути расположения проекта и выполните команды (4-9);
4. python -m venv venv
5. venv\scripts\activate
6. pip install -r requirements.txt
7. cd backend
8. set DJANGO_SETTINGS_MODULE=backend.settings
9. echo %DJANGO_SETTINGS_MODULE% (проверка, должно вернуть backend.settings)
10. Запуститe Redis (не ниже 7 версии!) от имени администратора. [Скачать Redis](https://github.com/redis-windows/redis-windows/releases)
11. Вернитесь в консоль (cmd) и выполните компанду: daphne backend.asgi:application
12. Откройте браузер, введите адрес: http://127.0.0.1:8000/

### Данные для входа

| Логин    | Пароль  | 
|----------|---------|
| igor     | myS3cr3tP@ssw0rd! | 
| andrei   | myS3cr3tP@ssw0rd! | 
| veronika | myS3cr3tP@ssw0rd! | 
| victor   | myS3cr3tP@ssw0rd! | 
| anna     | myS3cr3tP@ssw0rd! | 


### Ключевые маршруты
- http://127.0.0.1:8000/ - Авторизация/Регистрация
- http://127.0.0.1:8000/main/ - Главная страница
- http://127.0.0.1:8000/edit-profile/ - Мой профиль (редактирование, выход из учётной записи)
- http://127.0.0.1:8000/user-list/ - Список пользователей (с возможностью написать сообщение)
- http://127.0.0.1:8000/create-group/ - Создание группы