# Продуктовый помощник 

Этот сервис позваляет управлять рецептами
Here you can: 
- Создать собственный рецепт
- Найти новый для вас рецепт, добавить его в избранное или подписаться на автора
- Добавить его в список покупок и скачать в формате .txt
## Установка:
- Скачать репрозиторий:
	- > git clone [git@github.com:yonvik/foodgram-project-react.git](https://github.com/yonvik/foodgram-project-react.git)
- Перейти в директорию infra.
	- > cd  foodgram-project-react/infra
- Создать .env файл внутри и заполнить данные:
	- > DB_ENGINE=django.db.backends.postgresql 
	- > DB_NAME=postgres 
	- > POSTGRES_USER=postgres 
	- > POSTGRES_PASSWORD=12345678 
	- > DB_HOST=db 
	- > DB_PORT=5432 
	- > SECRET_KEY = 'super%difficult%key%123345678' # Здесь нужен ваш ключь
	- > ALLOWED_HOSTS = ['*']
	- > DEBUG = False
- Создать образы докера:
	- > docker-compose up -d --build
- Сделать миграции, загрузить ингридиенты в БД и загрузить статику: 
	- > docker-compose exec backend python manage.py migrate 
	- > docker-compose exec backend python manage.py update
	- > docker-compose exec backend python manage.py collectstatic --no-input
	  
	Создать суперпользователя:
	- - > docker-compose exec backend python manage.py createsuperuser 
## Рабочие ручки
 - > http://localhost/admin/ - страница админа
 - > http://localhost/signin/ - страница приложения

## Автор Backend: 
- [Андрей Янковский](https://github.com/yonvik)
## Автор Frontend:
- [Яндекс.Практикум](https://practicum.yandex.ru/)
