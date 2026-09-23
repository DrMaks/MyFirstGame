# Руководство по публикации Pixel Rogue в Steam (Steamworks)

В этом документе описаны все шаги для настройки страницы игры, загрузки сборки через SteamPipe и настройки достижений в Steamworks.

---

## 1. Сборка игры в релизный `.exe`

Перед деплоем соберите автономную версию игры (не требующую установленного Python):

```bash
python build_exe.py
```

Результат сборки появится в папке:
`dist/PixelRogue/`
Внутри находятся:
- `PixelRogue.exe`
- Все необходимые библиотеки SDL2 / Pygame-CE / NumPy
- Файл `steam_appid.txt`

Вы можете запустить `PixelRogue.exe` на любом компьютере с Windows 10/11 без каких-либо дополнительных установок.

---

## 2. Настройка в Steamworks Partner Portal

1. Войдите в [Steamworks Developer Portal](https://partner.steamgames.com/).
2. В разделе **All Applications** выберите вашу игру (или используйте временный тест App ID 480).
3. Замените число `480` в файле `steam_appid.txt` на ваш реальный **Steam App ID**.

---

## 3. Настройка Достижений (Steam Achievements)

В игре уже запрограммированы и готовы к вызову следующие идентификаторы достижений (`src/engine/steam_manager.py`). 
В панели Steamworks перейдите в **Stats & Achievements -> Achievements** и создайте записи с точными именами:

| API Name (ID в коде) | Отображаемое название | Описание |
|---|---|---|
| `ACH_FIRST_BLOOD` | First Blood | Уничтожьте первого монстра в подземелье. |
| `ACH_CHEST_HUNTER` | Treasure Hunter | Откройте спрятанный сундук с сокровищами. |
| `ACH_LEVEL_5` | Seasoned Adventurer | Достигните 5-го уровня за один забег. |
| `ACH_BOSS_SLAYER` | Dungeon Liberator | Победите Владыку Подземелья (Dungeon Overlord)! |
| `ACH_RICH` | Gold Digger | Соберите 100 золотых монет. |

---

## 4. Деплой через SteamPipe (`steamcmd`)

SteamPipe — официальный инструмент Valve для быстрой и инкрементальной загрузки сборок в Steam.

1. Скачайте `steamcmd` с официального сайта Valve.
2. В файлах `steam_deploy/app_build_config.vdf` и `steam_deploy/depot_build_config.vdf`:
   - Замените `YOUR_APP_ID` на номер вашей игры в Steam.
   - Замените `YOUR_DEPOT_ID` на номер вашего Depot (обычно `AppID + 1`).
   - Укажите путь к собранной папке `dist/PixelRogue`.
3. Запустите загрузку сборки в Steam:

```bash
steamcmd.exe +login <ВАШ_STEAM_ЛОГИН> +run_app_build C:\путь_к_проекту\steam_deploy\app_build_config.vdf +quit
```

4. В Steamworks перейдите во вкладку **Builds**, выберите загруженную сборку и переведите её в ветку `default` (или `beta` для закрытого тестирования).

---

## 5. Конфигурация запуска (Launch Options) в Steamworks

В панели управления игрой:
- **Installation -> General Installation**:
  - Executable: `PixelRogue.exe`
  - OS: Windows 64-bit
  - Тип: Launch (Standard Game)
