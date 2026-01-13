[app]
title = Device Tracker
package.name = devicetracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
version = 0.1
requirements = python3,kivy

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE

[buildozer]
log_level = 2
warn_on_root = 1

# Android specific
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.accept_sdk_license = True
android.skip_update = True
android.arch = arm64-v8a

# Build optimization
android.gradle_dependencies = 
android.add_jars = 
android.add_src = 
android.add_aars = 

# Meta-data
android.meta_data = 

# Presplash
#android.presplash.filename = %(source.dir)s/data/presplash.png

# Icon
#icon.filename = %(source.dir)s/data/icon.png

# Orientation
#android.orientation = portrait
