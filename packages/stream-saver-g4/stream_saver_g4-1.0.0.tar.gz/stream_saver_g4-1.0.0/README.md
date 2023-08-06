![Language](https://img.shields.io/badge/English-brigthgreen)

# Stream saver

![PyPI](https://img.shields.io/pypi/v/stream-saver-g4)
![PyPI - License](https://img.shields.io/pypi/l/stream-saver-g4)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stream-saver-g4)

Python module for save stream to disk

***

## Installation

### Package Installation from PyPi

```bash
$ pip install stream-saver-g4
```

### Package Installation from Source Code

The source code is available on [GitHub](https://github.com/Genzo4/stream_saver).  
Download and install the package:

```bash
$ git clone https://github.com/Genzo4/stream_saver
$ cd stream_saver
$ pip install -r requirements.txt
$ pip install .
```

***

## Basic usage

- ### Import:
```python
from stream_saver_g4 import StreamSaver
```

- ### Create instance:
Create an instance of the StreamSaver. You can specify additional options:
- streamURL - Stream URL.
  Default value: ''
- outputTemplate - Output template.
  Default value: 'output_%Y-%m-%d_%H-%M-%S.ts'
- segmentTime - Segment length.
  Default value: '01:00:00'


```python
stream = StreamSaver(streamURL='rtsp://cam_1.local:554/live1.sdp',
                     outputTemplate='output_%H-%M-%S.ts',
                     segmentTime='00:30:00'
                     )
```

- ### Run saving stream
Stream saving is running in the background.

```python
stream.run()
```

- ### Stop saving stream

```python
stream.stop()
```

[Changelog](https://github.com/Genzo4/stream_saver/blob/main/CHANGELOG.md)
***

![Language](https://img.shields.io/badge/Русский-brigthgreen)

# Stream saver

![PyPI](https://img.shields.io/pypi/v/stream-saver-g4)
![PyPI - License](https://img.shields.io/pypi/l/stream-saver-g4)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stream-saver-g4)

Python модуль для сохранения видеопотока на диск.

***

## Установка

### Установка пакета с PyPi

```bash
$ pip install stream-saver-g4
```

### Установка пакета из исходного кода

Исходный код размещается на [GitHub](https://github.com/Genzo4/stream_saver).  
Скачайте его и установите пакет:

```bash
$ git clone https://github.com/Genzo4/stream_saver
$ cd stream_saver
$ pip install -r requirements.txt
$ pip install .
```

***

## Использование

- ### Подключаем:
```python
from stream_saver_g4 import StreamSaver
```

- ### Создаём экземпляр
Создаём экземпляр StreamSaver. Можно указать дополнительные параметры:
- streamURL - адрес потока.
  Значение по умолчанию: ''
- outputTemplate - шаблон выходных файлов.
  Значение по умолчанию: 'output_%Y-%m-%d_%H-%M-%S.ts'
- segmentTime - длина одного сегмента.
  Значение по умолчанию: '01:00:00'

```python
stream = StreamSaver(streamURL='rtsp://cam_1.local:554/live1.sdp',
                     outputTemplate='output_%H-%M-%S.ts',
                     segmentTime='00:30:00'
                     )
```

- ### Запускаем сохрание потока
Сохранение потока идёт в фоновом режиме.

```python
stream.run()
```

- ### Останавливаем сохранение потока

```python
stream.stop()
```

[Changelog](https://github.com/Genzo4/stream_saver/blob/main/CHANGELOG.md)
