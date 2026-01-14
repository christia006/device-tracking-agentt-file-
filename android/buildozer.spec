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

# Requirements - FIXED: Versi Kivy yang stabil
requirements = python3==3.11.5,kivy==2.2.1,requests,certifi

# Icon
icon.filename = %(source.dir)s/icon.png

# Orientation
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE

# ---------------- Android Configuration ----------------
android.api = 34
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.skip_update = False
android.archs = arm64-v8a,armeabi-v7a

# CRITICAL FIX: Tambahan flag untuk mencegah error kompilasi
android.add_compile_options = -Wno-error=implicit-function-declaration
android.add_cflags = -Wno-macro-redefined -Wno-unused-command-line-argument
android.add_ldflags = -llog

# P4A Configuration - PENTING untuk stabilitas
p4a.branch = master
p4a.bootstrap = sdl2

# Buildozer settings
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin
