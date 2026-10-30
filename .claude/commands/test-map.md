---
description: Показать проверки, дефекты или API из карты тестирования выборок
argument-hint: [раздел | P1 | defects | api | questions]
---

Покажи из карты тестирования: $ARGUMENTS

- Номер раздела (например 5 или 12.3) → `python brain/brain.py checks --section <номер>`.
- P1/P2/P3 → `python brain/brain.py checks --priority <P>`.
- defects → `python brain/brain.py defects`; api → `python brain/brain.py api`; questions → `python brain/brain.py questions`.
- Иначе → `python brain/brain.py checks --grep "$ARGUMENTS"`.

Ответь коротко: список и вывод в 1–2 предложения.
