# CouriersRestAPI

## Установка
Необходимые зависимости устанавливаются с помощью pipenv.

  `$ pip3 install pipenv`
  
Далее в директории проекта прописываем:

  `$ pipenv --python 3.8.5 # или же более позднюю версию` 
  
  `$ pipenv shell`
  
  `$ pipenv install`
## Запуск
  `$ pipenv shell`
  
  `$ python3 main.py [--host] [--port]`
  
  Если не передавать параметры host и port, то по умолчанию запускается на localhost:8888. Пример запуска с параметрами:
  
  `$ python3 main.py --host 0.0.0.0 --port 8080`
  
  Также для работы приложения должна быть установлена база данных postgresql. 
  Необходиме для подключения параметры (имя пользователя, пароль, host, port, имя БД) укажите в файле `config.py`. 
  
  ## Запуск тестов
  Тестировать желательно, когда таблицы пусты, либо же в файле `test/test_main.py` в переменной `START_ID` указать id так, 
  чтобы `[START_ID, START_ID + 6]` не пересекался с индексами заказов и курьеров в базе.
  
  Для запуска тестов перейдите в каталог `test`
  
  `$ python3 -m unittest test_main.py # запуск всех тестов`
  
  `$ python3 -m unittest test_main.TestCouriersLoad.test_usual_load # запуск конкретного теста`
  
  Тесты зависимы друг от друга, поэтому тесты на назначение заказов, обновление информации и т. д. нужно запускать либо после тестов с загрузкой информации, 
  либо загрузив информацию самому.
  