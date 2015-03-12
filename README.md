## Установка и настройка
  * Ставим расширения для Postgresql
    * install postgresql-contrib
  * Загружаем базу dmoz
    * psql < dmozltree-eng.sql
  * Запускаем
    * python server/web.py



## Что работает
  * Отображение дерева тэгов
  * Удаление тэга, включая все дочерние узлы(правая кнопка на узле и Delete)
  * Переименование тэга(дважды нажать на тэге)
  * Открыть дерево на глубину N (вверху depth)
  * Поиск по имени Тэга (вверху указывается точное название)


## Что используется
  * Используется Postgres ltree расширение
    * [PostgreSQL ltree module](http://www.sai.msu.su/~megera/postgres/gist/ltree/)
  * Используется extjs 5.1.0 для отображения деревьев
    * [Ext Js 5](http://www.sencha.com/products/extjs/)
  * Используется web.py для api
    * [web.py](http://webpy.org/)