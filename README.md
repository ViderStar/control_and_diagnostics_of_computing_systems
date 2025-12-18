## RU

**Контроль и диагностика вычислительных систем — ЛР 1–7 (вариант 3)**  
Небольшой набор скриптов, которые я написал для сдачи лабораторных по тестированию логических схем и ОЗУ.

### Что сделано

- **ЛР1**: Single Path Activation (поиск тестов для stuck-at)
- **ЛР2**: D-алгоритм (сокращённое тестовое множество)
- **ЛР3**: LFSR — подбор сида для покрытия тестов ЛР1
- **ЛР4**: ОЗУ — Walking 0/1 + MATS++ (классические неисправности)
- **ЛР5**: ОЗУ — маршевые тесты (кодочувствительные неисправности)
- **ЛР6**: Controlled Random Testing (CRT) по THD/TCD + оценка покрытия на схеме ЛР1–2
- **ЛР7**: FAR (centroid) + OCRT (для N=8) + оценка покрытия на схеме ЛР1–2

> В файле `docs/Lab_6_7.docx` задания подписаны как «ЛР7» и «ЛР8». В этом проекте я оформил их как **ЛР6** и **ЛР7**.

### Установка

```bash
python3 -m pip install -r requirements.txt
```

### Запуск

```bash
# ЛР1–2
python3 main.py --suite logic

# ЛР3
python3 main.py --suite lfsr

# ЛР4–5
python3 main.py --suite memory

# ЛР6–7
python3 main.py --suite prob

# всё подряд
python3 main.py --suite all
```

### Схема (вариант 3)

```
F1 = NAND(x1, x2)
F2 = NOT(x4)
F3 = NOR(F2, x6)
F4 = AND(x3, F3)
F5 = OR(F1, F4)  → output
```

---

## ENG

**Computing Systems Control & Diagnostics — Labs 1–7 (variant 3)**  
A compact set of scripts I wrote to complete the labs on logic-circuit testing and RAM testing.

### Implemented

- **Lab 1**: Single Path Activation (stuck-at test search)
- **Lab 2**: D-algorithm (reduced test set)
- **Lab 3**: LFSR — seed search to cover Lab1 tests
- **Lab 4**: RAM — Walking 0/1 + MATS++ (classic faults)
- **Lab 5**: RAM — march tests (pattern-sensitive faults)
- **Lab 6**: Controlled Random Testing (CRT) using THD/TCD + fault coverage estimate on the Lab1–2 circuit
- **Lab 7**: FAR (centroid) + OCRT (N=8) + fault coverage estimate on the Lab1–2 circuit

### Install

```bash
python3 -m pip install -r requirements.txt
```

### Run

```bash
python3 main.py --suite logic
python3 main.py --suite lfsr
python3 main.py --suite memory
python3 main.py --suite prob
python3 main.py --suite all
```