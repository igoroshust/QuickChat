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
10. Запустите Redis-server от имени администратора (Redis не ниже 7 версии!)
11. Вернитесь в консоль (cmd) и выполните компанду: daphne backend.asgi:application

### Данные для входа

| Логин       | Пароль  | 
|-------------|---------|
| igor        | myS3cr3tP@ssw0rd! | 
| andrei      | myS3cr3tP@ssw0rd! | 
| veronika    | myS3cr3tP@ssw0rd! | 
