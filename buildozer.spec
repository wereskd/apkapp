[app]
title = Складской учёт
package.name = warehouse
package.domain = org.baranskiy.warehouse
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json

requirements = python3,kivy==2.3.1,sqlalchemy,psycopg2cffi,cffi

orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

[buildozer]
warn_on_root = 1

[python-for-android]
p4a.bootstrap = sdl2
