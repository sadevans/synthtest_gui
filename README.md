# GUI для теста алгоритмов создания синтетического датасета

## Клонирование репозитория

Для того, чтобы пользоваться GUI, необходимо склонировать репозиторий с помощью команды:
```bash
git clone https://github.com/sadevans/synthtest_gui.git
```

## Установка зависимостей

Для начала создайте виртуальную среду:
```bash
python -m venv venv
```

Активируйте ее:
```bash
source venv/bin/activate
```

После установите зависимости из **requirements.txt**:
```bash
pip install -r requirements.txt
```
### Если возникла проблема с PyQt6
Если у вас возникла проблема с установкой PyQt6 с помощью файла requirements, и в командной строке появляется что-то вроед этого:
![image](https://github.com/sadevans/synthtest_gui/assets/82286355/b628b2d6-f8fb-4ded-9c93-5d74c66d584a)

Запустите следующую команду:
```bash
pip install pip setuptools --upgrade && pip3 install PyQt6
```


## Использование GUI
Для запуска GUI необходимо запустить файл **run.py**:
```bash
python run.py
```
Все параметры в конфигураторе изменяемы.

## Инструкция по использованию

Скринкаст с демонстрацией использования можно посмотреть по ссылке: https://drive.google.com/drive/folders/1AVdjsn_6ukyeI6eH3tnN0t5wyG4s5Se9?usp=sharing

