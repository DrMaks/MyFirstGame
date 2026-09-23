[app]

# (str) Title of your application
title = Pixel Rogue: Dungeon of the Ancients

# (str) Package name (lower case, no special characters)
package.name = pixelrogue

# (str) Package domain (needed for android/ios packaging)
package.domain = org.pixelrogue.dungeon

# (str) Source code where the main.py lives (mobile entry point)
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,src/*,src/**/*

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,pygame-ce,numpy

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = sensorLandscape

# (bool) Indicate if the application should be fullscreen to not
fullscreen = 1

# (list) Permissions
android.permissions = VIBRATE,INTERNET,ACCESS_NETWORK_STATE

# (int) Target Android API, should be 34 as per latest Google Play policy
android.api = 34

# (int) Minimum API your APK / AAB will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 25b

# (list) List of architectures to build for (arm64-v8a is required for Google Play)
android.archs = arm64-v8a, armeabi-v7a

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Entry point for python
android.entrypoint = org.kivy.android.PythonActivity

# (list) Android application meta-data to set (key=value format)
# android.meta_data = com.google.android.gms.games.APP_ID=@string/game_services_project_id

# (bool) If True, then the app will be built as an Android App Bundle (.aab) instead of .apk
# Set to True when generating the final build for upload to Google Play Console
android.aab = True

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug with command output)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, default is ./.buildozer
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab) storage
bin_dir = ./bin
