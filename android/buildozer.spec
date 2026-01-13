[app]
title = Device Tracker
package.name = devicetracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
version = 0.1

# CRITICAL: Hapus python3 dari requirements
requirements = kivy

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE

[buildozer]
log_level = 2
warn_on_root = 1

# Android specific
android.api = 31
android.minapi = 21
android.ndk = 25b

# CRITICAL: Gunakan SINGLE architecture saja (arm64-v8a)
android.archs = arm64-v8a

# SDK paths
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.accept_sdk_license = True
android.skip_update = True

# Build optimization
android.gradle_dependencies = 
android.add_compile_options = 

# Whitelist
android.whitelist = lib-dynload/termios.so

# Debugging
p4a.branch = master
