[app]
title = Складской учёт
package.name = warehouse
package.domain = org.baranskiy.warehouse
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
# Исключаем папки бэкенда из APK
source.exclude_dirs = api, database, migrations, __pycache__, tests, .git, .buildozer, venv

requirements = python3==3.10.12,hostpython3==3.10.12,kivy==2.2.1,requests,certifi,urllib3,chardet,idna

orientation = portrait
android.archs = arm64-v8a
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.no_compile_pyo = True
android.release_artifact = apk
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
