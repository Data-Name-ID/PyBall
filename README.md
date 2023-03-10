# PyBall Game | Проект Яндекс Лицей

## Содержание
0. [Инструкция по установке и запуску](#0-инструкция-по-установке-и-запуску)
1.  Введение
    1.  [Идея проекта](#11-идея-проекта)
    2.  [Игровой процесс](#12-игровой-процесс)
2.  Описание реализации
    1.  [Структура игры](#21-структура-игры)
    2.  [Особенности реализации](#22-особенности-реализации)
    3.  [Используемые технологии](#23-используемые-технологии)
3.  Заключение
    1. [Планы на будущее](#31-планы-на-будущее)

## 0. Инструкция по установке и запуску
1. [Скачать](https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe) и установить Python **v3.9.x** или выше
2. [Скачать](https://github.com/Data-Name-ID/PyBall/releases/tag/Releases) последнюю версию игры из раздела релизов
3. Установить зависимости с помощью pip `pip install -r requirements.txt`
4. Запустить игру `python PyBall.py`

P.S. Вы можете ускорять или замедлять временя в игре с помощью клавиш - или = 

## 1.1 Идея проекта

#### [Пояснительная записка](https://github.com/Data-Name-ID/PyBall/raw/master/%D0%9F%D0%BE%D1%8F%D1%81%D0%BD%D0%B8%D1%82%D0%B5%D0%BB%D1%8C%D0%BD%D0%B0%D1%8F%20%D0%B7%D0%B0%D0%BF%D0%B8%D1%81%D0%BA%D0%B0.docx)
#### [Презентация](https://github.com/Data-Name-ID/PyBall/raw/master/PyBall.pptx)

**PyBall** - небольшая, но увлекательная игра, игровой процесс которой заключается в прохождении уровней, разрушая блоки различной прочности.

**Примечание**: на анимации здесь и далее могут наблюдаться артефакты, искажённые цвета и низкая частота кадров из-за особенностей формата gif. В игре таких проблем нет.

![1](https://user-images.githubusercontent.com/68386017/220633947-a6fcdca9-fec8-429d-b575-a48e059dcf94.gif)

## 1.2 Игровой процесс

На каждом уровне игроку доступно некоторое количество шариков, которое определяется конкретным уровнем. Он можжет стрелять ими в блоки направление выстрела задаётся с помощью мыши. Шарики, попадая в блоки, снимают определённое количество прочности блока и отскакивают от него, соблюдая закон отражения. Блоки, когда теряют прочность, меняют свой цвет, а при достижении прочности 0 - разрушаются. После каждого хода блоки опускаются к ограничивающей линии. Игрок побеждает, если все блоки были разрушены, до того, как они достигнут ограничивающей линии. Пока шарики находятся в полёте игрок не может выстелить ещё раз. Особое внимание было уделено звуковым и визуальным эффектам. Присутствует возможность ускорять время.

![2](https://user-images.githubusercontent.com/68386017/220634055-9674eded-2d29-492f-add6-0893044f92ea.gif)
![3](https://user-images.githubusercontent.com/68386017/220634074-ce8011ba-3236-4e2b-9ee2-31488478fdea.gif)

## 2.1 Структура игры
![teh](https://user-images.githubusercontent.com/68386017/220634438-a65008e2-eb16-4175-a373-00680bba37e6.png)

1. **PyBall.py** - главный файл игры
2. **requirements.txt** - файл с перечнем зависимостей
3. **fonts** - папка с используемыми в игре шрифтами, на данных момент
необходим только один
4. **img** - папка, содержащая изображения для спрайтов
5. **levels** - папка, в которой находятся уровни игры
6. **sounds** - содержит все звуки и музыку
7. **Data** - папка с пользовательскими данными
8. **game_save.data** - файл сохранения игрового прогресса, в
зашифрованном виде
9. **secret.key** - файл, содержащий уникальный ключ для расшифровки
game_save.data
10. **LICENSES** - папка, содержащая лицензии используемых ресурсов

## 2.2 Особенности реализации
- Простое добавление новых уровней
- Шифрование файла сохранения игрового процесса
- Простое добавление новых механик в будущем
- Все магические данные вынесены в виде констант
- Использование ООП и спрайтов
    1. **GameMap** - основной класс, управляющий игровым процессом
    2. **Block** и **Ball** - классы соответствующих названию спрайтов, описывающие их поведение
    3. **TextRender** - класс для более удобного размещения текста на экране
    4. **BottomLine** - класс, описывающий ограничивающую линию, является спрайтом
    5. **AnimatedSprite** - класс анимированного спрайта для добавления милой лисы на главный экран
    6. **Button** - класс кнопки, описывает её поведение и определяет логику взаимодействия, является спрайтом
    7. **SimpleBall** - класс, описывающий поведение декоративных шариков на главном экране
    8. **Particle** - класс для создания эффекта разрушения блока
    9. **Image** - класс, для добавления картинки на экран в виде спрайта

## 2.3 Используемые технологии
- Python **3.9.13**
- PyGame **2.1.2**
- Cryptography **39.0.1**
- PhotoShop **2020**

## 3.1 Планы на будущее
- Добавление новых уровней и механик, к примеру подбор новых шариков, бустеры и т.п.
- Добавление валюты и скинов для блоков и шариков
- Добавление настроек приложения прямо в его интерфейсе
- Мелкие улучшения
