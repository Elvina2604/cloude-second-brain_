---
title: Сервис выборок (clients-filtering)
summary: Ключевые факты о выборках: устройство, расчёт, ответы аналитика, риски.
tags: [area, selections, clients-filtering]
updated: 2026-10-30
---

# Сервис выборок

## Статус
Документация изучена (13 PDF + 8 PDF по ЕКЛ). Карта тестирования: https://claude.ai/artifact/51oWHufZQ4gL53bygGM3f3, копия — [references/selections-test-map.md](../references/selections-test-map.md).

## Факты
- Точка входа — page/clients-segments; выборки = записи ПапкаКонтрагентов (Вид 8 — в CRM, Вид 9 — только в рассылках), фильтр в hstore Filter.
- Результат хранится в prefetch; статические — 1 год, затем заглушка «Данные устарели».
- Лимит набора — 1 000 000 (ответ 29.10; в документации устаревшее 20 000).
- Расчёт: нормализация → DNF → статистика → опорный предикат ((N/LIMIT)×t) → набор через DWC → дофильтрация → И внутри мегапредиката → ИЛИ → prefetch.
- Выключатель дофильтрации: параметр облака ClientsFiltering.UseEnhancedMerge = false, фича filtering_enhanced_merge.
- Набор фильтров зависит от приложения (Clients/Presto/Retail/Hotel, CRM, Profile, прочие); в KZ/UZ скрыты 33 фильтра блока «Компании».
- Типы фильтров: bool, дата (min/max+type или type+count), список (ids/names/type), диапазон, кастомный.
- Права: участок «Компании» + ограничения «Изменение разделов», «Массовые операции»; аккаунты — участок «Выборки».
- Аккаунты: источник — биллинг, конвертации sppid↔accountid через ИНН/КПП, пачки по 100.
- Таблицы: TaskNEW, TaskMetaNEW, ResultDataNEW, ResultDataCache, TaskCache, HandlerStat, Megapredicate(Link).

## Ответы аналитика (29.10)
- Область: весь сервис, кроме выборок для маршрутов помощи, рассылок и кандидатов; контактные лица (реестр ЕКЛ) входят.
- Название выборки обязательно, 1–255 символов, дубли разрешены.
- Остановка расчёта: найденное сохраняется, статус finish.

## Риски
- Неверный состав при сложной И/ИЛИ из-за оптимизации — сверять с UseEnhancedMerge = false.
- В примере DNF в документации, вероятно, опечатка — не подтверждено.

## Связанные области
- [selections-stands.md](selections-stands.md) — результаты исследования стендов, Д-1…Д-19.
- [selections-api.md](selections-api.md) — публичные методы.
- [selections-contacts.md](selections-contacts.md) — выборки контактных лиц.
