[app]
title = Device Tracker
package.name = devicetracker
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy

[buildozer]
log_level = 2
warn_on_root = 1

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk_path = ~/.buildozer/android/platform/android-sdk
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.accept_sdk_license = True
android.skip_update = True
android.arch = arm64-v8a
