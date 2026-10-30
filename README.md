# cloude-second-brain_

Переносимый «второй мозг» для Claude (Claude Code и claude.ai): файловая база знаний `brain/`, локальный поиск и сборка контекста без внешних сервисов и без вызовов LLM. Сделан по образцу [opencode-second-brain](https://github.com/RRKalinovskiy/opencode-second-brain) и наполнен знаниями о тестировании сервиса выборок Saby (clients-filtering).

Помогает Claude:
- не перечитывать всё перед каждой задачей;
- находить проверенные факты, решения и проверки из карты тестирования;
- сохранять итоги сессий и handoff;
- держать контекст в пределах бюджета.

## Состав

```
.claude/
  settings.json          # хуки: SessionStart → brief, Stop → автожурнал
  hooks/auto_journal.py  # автожурнал сессий (без LLM, с маскировкой секретов)
  commands/              # /brain, /brain-search, /brain-save, /test-map
  skills/                # second-brain, selections-testing, stand-exploration
brain/
  brain.py               # CLI
  INDEX.md STATE.md PROJECT.md GLOSSARY.md DECISIONS.md inbox.md
  areas/                 # selections, selections-stands, selections-api, selections-contacts
  references/            # selections-test-map.md — карта тестирования
  sessions/              # журналы; sessions/auto/ — автожурнал (в .gitignore)
  playbooks/             # work.md, stand-exploration.md
  templates/             # session, area, decision, defect
CLAUDE.md                # правила для Claude в этом репозитории
```

## Установка

1. Клонировать репозиторий и открыть его папку в Claude Code (или скопировать `.claude/`, `brain/`, `CLAUDE.md` в свой проект).
2. Нужен Python 3.10+ (только стандартная библиотека). На Windows, если команда `python` не находится, замените в `.claude/settings.json` и командах `python` на `py -3`.
3. Проверить:
   ```
   python brain/brain.py brief
   python brain/brain.py lint
   ```

## Команды CLI

```
python brain/brain.py brief                    # STATE + последняя сессия + карта
python brain/brain.py pack "задача"            # контекст под задачу, ≤ 7000 символов
python brain/brain.py search "термин"          # BM25 + префиксы + синонимы
python brain/brain.py note "мысль"             # в inbox.md
python brain/brain.py new-session              # журнал на сегодня
python brain/brain.py lint                     # frontmatter, ссылки, размеры, секреты
python brain/brain.py stats                    # размеры файлов

python brain/brain.py checks --section 4 --priority P1   # проверки из карты
python brain/brain.py checks --grep "лимит"
python brain/brain.py defects                  # подозрения Д-1…Д-19
python brain/brain.py api --grep CoreV3        # публичные методы
python brain/brain.py questions                # открытые вопросы
```

Команды в Claude Code: `/brain <задача>`, `/brain-search <термин>`, `/brain-save`, `/test-map <раздел|P1|defects|api|questions>`.

## Автожурнал

Хук `Stop` после каждого ответа дописывает последний запрос и ответ в `brain/sessions/auto/ГГГГ-ММ-ДД.md`: без LLM, с обрезкой и маскировкой типовых секретов. Это черновик — итоги переносятся вручную через `/brain-save`. Чтобы версионировать автожурнал, уберите строку из `.gitignore`.

## claude.ai (Project «For work»)

Те же файлы `brain/` лежат документами в Project. Навык `second-brain` работает в обоих местах: в репозитории — через CLI, в Project — через поиск по документам.

## Границы

Учётные данные стендов и рабочих систем в репозитории не хранятся. Исходные PDF документации — у владельца.
