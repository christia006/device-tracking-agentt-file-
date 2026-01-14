[app]

# Basic info
title = MyApp
package.name = myapp
package.domain = org.example

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
entrypoint = main.py

# Version
version = 1.0.0
version.code = 1

# Requirements
requirements = python3,kivy

# Icon
icon.filename = %(source.dir)s/icon.png

# Orientation
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION

# ---------------- Android Configuration ----------------
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.skip_update = False
android.archs = arm64-v8a,armeabi-v7a

# Tambahan flag untuk menghindari warning macro redefined
android.add_cflags = -Wno-macro-redefined

# Buildozer settings
log_level = 2
warn_on_root = 1
build_dir = ./build
bin_dir = ./bin
