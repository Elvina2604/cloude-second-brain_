---
title: Второй мозг
summary: Точка входа в базу знаний: что где лежит и как читать.
tags: [index, brain, navigation]
updated: 2026-10-30
---

# Второй мозг

Сжатая база знаний для работы с Claude: тестирование сервиса выборок Saby (clients-filtering). Не история чата. Читать по частям.

## С чего начать
| Задача | Действие |
|---|---|
| Текущий фокус | [STATE.md](STATE.md) или `/brain` |
| Контекст под задачу | `py -3 brain/brain.py pack "<задача>"` |
| Найти факт | `py -3 brain/brain.py search "<термин>"` |
| Проверки из карты | `py -3 brain/brain.py checks --section 5 --priority P1` |
| Подозрения на дефекты | `py -3 brain/brain.py defects` |
| Публичные методы API | `py -3 brain/brain.py api` |
| Сохранить итоги | `/brain-save` |

## Карта знаний
- [PROJECT.md](PROJECT.md) — продукт, стенды, инструменты, источники истины.
- [areas/selections.md](areas/selections.md) — сервис выборок: факты, ответы аналитика, риски.
- [areas/selections-stands.md](areas/selections-stands.md) — что найдено на стендах fix-crm и fix-inside.
- [areas/selections-api.md](areas/selections-api.md) — публичные методы БЛ.
- [areas/selections-contacts.md](areas/selections-contacts.md) — выборки контактных лиц (ЕКЛ).
- [references/selections-test-map.md](references/selections-test-map.md) — полная карта тестирования (экспорт, ~470 строк, читать разделами).
- [GLOSSARY.md](GLOSSARY.md) — термины и синонимы для поиска.
- [DECISIONS.md](DECISIONS.md) — принятые решения.
- [inbox.md](inbox.md) — неразобранные заметки.
- [playbooks/work.md](playbooks/work.md) — протокол работы со вторым мозгом.
- [playbooks/stand-exploration.md](playbooks/stand-exploration.md) — как исследовать стенд в браузере.
- sessions/ — журналы по датам; sessions/auto/ — автожурнал хука (черновик).
- templates/ — шаблоны сессии, области, решения, дефекта.

## Правила
1. Один факт — одно место; ссылка вместо копии.
2. Источник истины — требования, автодокументация wi.saby.ru, стенд. Если brain противоречит — обновить brain.
3. Пароли, токены, логины тестовых пользователей не хранить.
4. Непроверенное помечать «не подтверждено».
5. Область ≤ ~300 строк, сессия ≤ ~80, STATE ≤ ~60.
