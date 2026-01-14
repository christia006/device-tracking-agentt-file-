# buildozer.spec

[app]

# (str) Title of your application
title = MyApp

# (str) Package name
package.name = myapp

# (str) Package domain (reverse domain style)
package.domain = org.example

# (str) Source code directory
source.dir = .

# (list) Source files to include (let empty to include all)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application version
version = 1.0.0

# (int) Application version code (for Android)
version.code = 1

# (str) Python entry point
entrypoint = main.py

# (list) Requirements
requirements = python3,kivy

# (bool) Include data files in APK
# include all *.kv and images by default
# source.include_exts already menangani ini

# (str) Icon of the app
icon.filename = %(source.dir)s/icon.png

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (bool) fullscreen or not
fullscreen = 0

# (list) Android permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION

# ---------------- Android configuration ----------------

# (int) Target Android API, should be as high as possible
android.api = 34

# (int) Minimum API your APK / AAB will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# (str) Path to custom SDK/NDK (optional)
# android.sdk_path =
# android.ndk_path =

# (str) Android entry point, default is ok for Kivy
# android.entrypoint = org.kivy.android.PythonActivity

# (list) Android additional libraries to copy to APK
# android.add_libs_armeabi_v7a = libs/*.so
# android.add_libs_arm64_v8a = libs/*.so

# (list) Android Java source files (if needed)
# android.add_src =

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (bool) Copy Android assets (e.g., fonts) automatically
# android.copy_assets = 1

# ---------------- Buildozer behavior ----------------

# (str) Command to use for build
# buildozer-cmd already diatur di GitHub Actions

# (bool) Clear previous builds
# clean_build = True

# (bool) Verbose mode
log_level = 2

# (str) Path to build directory
build_dir = ./build

# (str) Path to bin directory (APK output)
bin_dir = ./bin
