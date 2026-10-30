---
name: second-brain
description: Use at the start of a non-trivial work task, when looking for known project facts, or when the user says /brain, /brain-search, /brain-save, «сохрани итоги», «что мы знаем про…».
---

# Второй мозг

Файловая база знаний `brain/` (в репозитории cloude-second-brain_) или документы `brain/` в Project «For work» на claude.ai. Цель: не переспрашивать известное, находить проверенные факты, сохранять итоги и handoff.

## Где работаю
- Есть `brain/brain.py` (Claude Code, репозиторий) → пользуюсь CLI.
- Нет файлов, но есть Project «For work» → `project_search` / `project_read` / `project_write` по тем же путям `brain/...`.

## CLI
| Команда | Зачем |
|---|---|
| `python brain/brain.py brief` | STATE + последняя сессия + карта |
| `python brain/brain.py pack "задача"` | контекст под задачу, ≤ 7000 символов |
| `python brain/brain.py search "термин"` | BM25 + префиксы + синонимы из GLOSSARY |
| `python brain/brain.py note "мысль"` | в inbox.md |
| `python brain/brain.py new-session` | журнал на сегодня |
| `python brain/brain.py lint` | frontmatter, ссылки, размеры, секреты |
| `checks` / `defects` / `api` / `questions` | карта тестирования выборок |

На Windows вместо `python` — `py -3`, если `python` не найден.

## Чтение
1. `pack` по формулировке задачи; если неясно — `brief`.
2. Открывать только найденные разделы. `references/` и большие файлы — разделами.
3. Источник истины — требования, wi.saby.ru, стенд. Противоречие → обновить brain.

## Запись (/brain-save)
1. `new-session`, просмотреть `sessions/auto/` (черновик хука Stop).
2. `sessions/ГГГГ-ММ-ДД.md`: задача, сделано, найдено, решения, следующие шаги.
3. `STATE.md`: фокус, вопросы, шаги. Факты → `areas/`, решения → `DECISIONS.md`.
4. `lint` без ошибок. В ответе — изменённые файлы.
5. В Project писать редко и пачкой (каждая запись сбрасывает кэш чатов); документ правится целиком: read → правка → write.

## Правила
- Один факт — одно место; ссылка + вывод + дата.
- Не писать пароли, токены, логины тестовых пользователей, персональные данные.
- Непроверенное — «не подтверждено».
- Лимиты: STATE ≤ 60 строк, сессия ≤ 80, область ≤ 300.
- Пользователь — тестировщик, не программист: ответы кратко, по-русски, без кода, если не просили.
