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
android.sdk = 34
android.ndk = 25b
android.ndk_api = 21

# Accept licenses otomatis
android.accept_sdk_license = True

# Skip update jika SDK sudah ada
android.skip_update = False

# Architecture
android.archs = arm64-v8a,armeabi-v7a

# Buildozer settings
log_level = 2
warn_on_root = 1
build_dir = ./build
bin_dir = ./bin
