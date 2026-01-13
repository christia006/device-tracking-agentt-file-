[app]
title = Device Tracker
package.name = devicetracker
package.domain = org.example
source.dir = .
source.include_exts = py
version = 1.0
requirements = python3,kivy,requests,certifi

# Icon dan splash (opsional - hapus jika tidak ada)
#icon.filename = %(source.dir)s/icon.png
#presplash.filename = %(source.dir)s/presplash.png

# Permissions minimal
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE,WAKE_LOCK

[buildozer]
log_level = 2
warn_on_root = 1

# Android Configuration - OPTIMIZED
android.api = 31
android.minapi = 21
android.ndk = 25b

# CRITICAL: Single architecture untuk ukuran kecil
android.archs = arm64-v8a

# SDK Configuration
android.skip_update = True
android.accept_sdk_license = True

# Gradle optimization
android.gradle_dependencies = 

# Meta-data
android.meta_data = 

# Orientation
android.orientation = portrait

# Fullscreen
#android.fullscreen = 1

# Add python activity
p4a.branch = master
p4a.bootstrap = sdl2

# Whitelist
android.whitelist = lib-dynload/termios.so

# Blacklist (untuk mengurangi ukuran)
android.blacklist = test,tests,__pycache__,*.pyc,*.pyo

# Exclude unnecessary files
android.blacklist_src = tests,spec,docs
