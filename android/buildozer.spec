[app]

# Application title
title = Device Tracker

# Package name
package.name = devicetracker

# Package domain (reverse domain name)
package.domain = com.tracking

# Source code directory
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas

# Application version
version = 1.0.0

# Application requirements
requirements = python3,kivy==2.2.1,requests,pyjnius

# Supported orientations
orientation = portrait

# Android permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE,WAKE_LOCK

# Android API versions
android.api = 31
android.minapi = 21
android.ndk = 25b

# Android architecture
android.archs = arm64-v8a,armeabi-v7a

# Android features
android.features = android.hardware.location.gps

# Presplash background color
presplash.color = #0f172a

# Icon (replace if ada icon)
#icon.filename = %(source.dir)s/data/icon.png

# Presplash (replace jika ada)
#presplash.filename = %(source.dir)s/data/presplash.png

# Android entry point
android.entrypoint = org.kivy.android.PythonActivity

# Android app theme
android.apptheme = @android:style/Theme.NoTitleBar

# Android private storage
android.private_storage = True

# Enable backup
android.allow_backup = True

# Gradle dependencies (if needed)
android.gradle_dependencies = 

# Android release artifact type
android.release_artifact = apk

# Android logcat filters
android.logcat_filters = *:S python:D

# Copy library .so files from local libs directory
android.add_libs_armeabi_v7a = 
android.add_libs_arm64_v8a = 

# Android additional Java imports
android.add_imports = 

# Android additional Java files
android.add_src = 

# Android manifest placeholders
android.manifest.intent_filters = 

# Android services
services = 

# Skip file suffixes
android.skip_update = False

# P4A bootstrap
p4a.bootstrap = sdl2

# P4A branch (use master for latest)
p4a.branch = master

# Extra p4a arguments
p4a.local_recipes = 

# iOS specific (tidak dipakai)
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

[buildozer]

# Log level
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Bin directory
bin_dir = ./bin
