# Tree structure generator
Приложение, извлекающее из БД SQL иерархическую структуру данных сотрудников компании
и выводящее ее в наглядном виде в командную строку, html-файл и json-файл.

### Требования
1. Docker version 20.10.21


### Инструкция по запуску
1. Клонируем репозиторий и переходим в директорию проекта
```sh
git clone git@github.com:artemyev1003/tree_view.git
cd git@github.com:artemyev1003/tree_view.git
```

2. Собираем образ и запускаем контейнер 
```sh
docker-compose up --build
```

Сгенерированные файлы в формате .html и .json сохраняются в директории ```/data```.
