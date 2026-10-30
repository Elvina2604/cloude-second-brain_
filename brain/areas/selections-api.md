---
title: Публичное API выборок
summary: 27 публичных методов (Public Service Contract) в 8 объектах и что в них проверять.
tags: [area, selections, api, postman]
updated: 2026-10-30
---

# Публичные методы сервиса выборок

## Public Service Contract (v.26.5100)

По автодокументации wi.saby.ru v.26.5100 (сборка 26.5100-184 от 22.10.2026) публичными отмечены 27 методов в 8 объектах; в скобках — версия метода. Остальные методы — Internal, Internal Application, Service и Trusted Application Contract — вне этого раздела. Проверять через Postman: валидный вызов, пустые и неверные параметры, навигация (для списочных — версия 4), вызов без прав.

| Объект (модуль) | Метод | Назначение | Что проверить | Приоритет |
| --- | --- | --- | --- | --- |
| CoreV3 (ClientsFilteringService) | ReadSelection(1) | Чтение выборки по параметрам | Данные = карточка (счётчик, статус, фильтр); несуществующая и чужая выборка | P1 |
| CoreV3 | ReadSelectionList(1) | Чтение выборки по параметрам | Чем отличается от ReadSelection — описание совпадает (см. вопросы); набор выборок, пустой список | P1 |
| CoreV3 | Collecting(1) | Итерация одной страницы выборки | Последовательные вызовы добирают состав без дублей; вызов для завершённой и отменённой выборки | P1 |
| CoreV3 | Cancel(1) | Отмена выборки | Расчёт остановлен, статус finish, найденное сохранено; повторная отмена; отмена завершённой | P1 |
| CoreV3 | CancelTask(1) | Отмена набора выборки | Чем отличается от Cancel — уточнить; те же проверки | P1 |
| CoreV3 | DeleteTask(1) | Удаление выборок | Удаление во время расчёта; данные в prefetch и TaskNEW очищены; чужая выборка | P1 |
| CoreV3 | PreCacheHeavyFilters(1) | Кэширование тяжёлых фильтров с заменой на пересечение по И | Результат выборки с кэшем и без совпадает; TTL кэша (TaskCache) | P2 |
| Filters (FiltersView) | FiltersToTextView(1), (2) | Набор фильтров → текст | Все типы фильтров; пустые значения (Д-2, Д-8, Д-9); локализация; разница версий 1 и 2 | P1 |
| Filters (PredicateClients) | ClientsByCD(4) | Физлица по набору фильтров (контактные данные) | Телефон / email / оба; навигация | P2 |
| Filters (PredicateClients) | GetClientsFromSPP(4) | Юрлица по набору фильтров | Фильтры СПП, навигация | P2 |
| Filters (PredicateClients) | GetClietnsBySPPFilter(4) | Юрлица по набору фильтров | Опечатка в имени (Clietns) и то же описание, что у GetClientsFromSPP — уточнить | P3 |
| FiltersOnline | GetLocalClients(1) | Идентификаторы локальных клиентов | Пустая схема, удалённые клиенты | P2 |
| FiltersOnline | CheckSppIdsInLocalScheme(2) | Проверка наличия СПП-идентификаторов в схеме клиента | Есть / нет / смешанный набор | P2 |
| FiltersOnline | GetClientsWithSPPId(3) | СПП-идентификаторы клиентов | Клиенты без СПП-идентификатора не возвращаются | P2 |
| FiltersOnline | GetEliminatedClients(1) | Ликвидированные из переданных | Действующие не возвращаются | P3 |
| FiltersOnline | CustomersBirthday(4) | Клиенты с ДР в ближайшие N дней | N = 0, 1, через конец года, 29 февраля (как 3.1.3) | P1 |
| FiltersOnline | ClientsExpiredContact(4) | Клиенты с просроченными контактами (пока только плановые) | Просроченная плановая активность попадает, выполненная — нет | P2 |
| FiltersOnline | GetAggPinnedClients(0) | Количество закреплённых клиентов | Число совпадает с реестром | P3 |
| FiltersOnline | GetFullStaffList(1) | Сотрудники переданных подразделений | Вложенные подразделения, уволенные (фильтр «Кроме сотрудников») | P2 |
| FiltersOnline | FilterUsersByRoles(4) | Фильтрация пользователей по ролям | В описании: «метод не списочный, только описывает сигнатуру» — уточнить, вызывается ли | P3 |
| FiltersOnline | CollectSPPCategory(2) | Сбор видов деятельности / ОКВЭД | Deprecated с .2100, но остаётся публичным — уточнить, тестировать ли | P3 |
| FiltersProxy (Online) | GetActivityHierarchyAll(4) | Иерархия сценариев активности с обработкой удалённых | Удалённые сценарии не предлагаются, сохранённые в выборках не ломаются (см. Д-8) | P1 |
| FiltersProxy (Online) | RetailWithoutDiscCardsClients(4) | Физлица без переданных дисконтных карт | Связка с фильтром «Без карт» | P2 |
| FiltersProxy (AccountsSelection, inside) | GetActivityHierarchyAll(4) | Proxy над online.FiltersProxy.GetActivityHierarchyAll | Результат совпадает с online-версией; права inside | P2 |
| Retail | GetDiscountCardList(4) | Список дисконтных карт | Навигация, поиск | P3 |
| Selections | MoveContentToFolder(3) | Объединение двух папок выборок | Содержимое перенесено, счётчики пересчитаны; папка сама в себя; вложенные | P2 |

Состав публичного API меняется: у CoreV3.SaveSelection(2) и (4) пометка «после 26.5100 будет добавлено новое API» — сверить список перед тестированием.

## Как смотреть остальные методы
Категории на wi.saby.ru: Internal, Internal Application Contract, Service Contract, Public Service Contract, Trusted Application Contract. Публичными считаем только Public Service Contract. Число в скобках — версия метода; списочные методы — версия 4.
