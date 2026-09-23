# Инструкция по сборке и публикации в Google Play Market

Данное руководство описывает полный процесс сборки Android App Bundle (`.aab`) и публикации мобильной версии игры **Pixel Rogue: Dungeon of the Ancients** в **Google Play Store**.

---

## 📱 Архитектура мобильной версии

- **Точка входа**: `main_mobile.py`
- **Сенсорный ввод**: Виртуальный аналоговый стик слева, сенсорные кнопки атаки, дэша, свитков и сундуков справа (`src/engine/touch_controls.py`).
- **Мультитач**: Поддержка одновременных нажатий несколькими пальцами (ходьба + атака).
- **Google Play Games Services**: Архитектура достижений и лидербордов в `src/services/google_play_manager.py`.
- **Конфигурация сборки**: `buildozer.spec` (Target SDK 34, Android App Bundle `.aab`, 64-bit `arm64-v8a`).

---

## 🛠️ 1. Подготовка окружения для сборки (Buildozer)

Buildozer компилирует Python-код, Pygame-CE и зависимости в нативный бинарный формат Android. Рекомендуется выполнять сборку под **Linux / WSL2 (Ubuntu)** или через **GitHub Actions**:

```bash
# 1. Установка системных зависимостей (Ubuntu / WSL2)
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 2. Установка Buildozer и Cython
pip3 install --user --upgrade buildozer cython virtualenv
```

---

## 🔑 2. Генерация релизного ключа подписи (Keystore)

Для выкладки в Google Play требуется подписать приложение вашим персональным сертификатом:

```bash
keytool -genkey -v -keystore pixel_rogue_release.keystore \
    -alias pixelrogue \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000
```
> Сохраните файл `pixel_rogue_release.keystore` и пароль в надежном месте! Он потребуется для всех будущих обновлений игры.

---

## 📦 3. Сборка Android App Bundle (.aab)

Google Play требует пакеты в формате `.aab` (Android App Bundle):

```bash
# Тестовая отладочная сборка (.apk для проверки на телефоне)
buildozer android debug

# Релизная сборка для Google Play (.aab)
buildozer android release
```

После завершения файл будет сохранен в папке `bin/`:
`bin/pixelrogue-1.0.0-arm64-v8a_armeabi-v7a-release-unsigned.aab`

Подпишите полученный бандл вашим ключом:
```bash
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
    -keystore pixel_rogue_release.keystore \
    bin/pixelrogue-1.0.0-release-unsigned.aab pixelrogue
```

---

## 🚀 4. Публикация в Google Play Console

1. Зайдите в [Google Play Console](https://play.google.com/console).
2. Нажмите **Создать приложение**:
   - Название: `Pixel Rogue: Dungeon of the Ancients`
   - Язык по умолчанию: Русский / English
   - Тип: Игра / Бесплатно (или платно)
3. **Настройка страницы в магазине**:
   - Значок приложения: 512×512 px (PNG с альфа-каналом).
   - Картинка для описания (Feature Graphic): 1024×500 px.
   - Скриншоты геймплея (горизонтальные 16:9, минимум 2 шт.).
4. **Google Play Games Services**:
   - Перейдите в раздел `Play Games Services` -> `Настройка и управление`.
   - Добавьте достижения из списка:
     - `ACH_FIRST_BLOOD` (Первая кровь)
     - `ACH_CHEST_HUNTER` (Охотник за сокровищами)
     - `ACH_LEVEL_5` (Опытный герой)
     - `ACH_BOSS_SLAYER` (Победитель повелителя подземелья)
     - `ACH_RICH` (Богач)
     - `ACH_FLOOR_4` (Хранитель глубин)
   - Скопируйте сгенерированные ID достижений в `src/services/google_play_manager.py`.
5. **Загрузка билда**:
   - В меню слева выберите **Внутреннее тестирование** или **Рабочая версия**.
   - Перетащите подписанный `.aab` файл.
   - Заполните опросник о возрастных ограничениях и политику конфиденциальности.
   - Отправьте приложение на проверку Google Play.
