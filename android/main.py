name: Build Android APK

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04
    
    steps:
    # 1️⃣ Checkout repository
    - name: Checkout repository
      uses: actions/checkout@v4
    
    # 2️⃣ Setup Python
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.10"
    
    # 3️⃣ Install system dependencies
    - name: Install system dependencies
      run: |
        sudo apt update
        sudo apt install -y \
          zip unzip openjdk-17-jdk \
          python3-pip \
          build-essential \
          libffi-dev \
          libssl-dev \
          python3-dev \
          git wget curl \
          autoconf automake libtool \
          pkg-config zlib1g-dev \
          libncurses5-dev libncursesw5-dev \
          cmake ccache \
          libltdl-dev
    
    # 4️⃣ Setup Android SDK
    - name: Setup Android SDK
      run: |
        export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
        mkdir -p $ANDROID_HOME/cmdline-tools
        mkdir -p $ANDROID_HOME/tools/bin
        
        cd $ANDROID_HOME/cmdline-tools
        wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
        unzip -q commandlinetools-linux-9477386_latest.zip
        mv cmdline-tools latest
        rm commandlinetools-linux-9477386_latest.zip
        
        ln -s $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager $ANDROID_HOME/tools/bin/sdkmanager
        ln -s $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager $ANDROID_HOME/tools/bin/avdmanager
        
        echo "ANDROID_HOME=$ANDROID_HOME" >> $GITHUB_ENV
        echo "ANDROID_SDK_ROOT=$ANDROID_HOME" >> $GITHUB_ENV
        echo "PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH" >> $GITHUB_ENV
    
    # 5️⃣ Install SDK components
    - name: Install SDK components
      run: |
        export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
        yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME --licenses || true
        $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME \
          "platform-tools" \
          "platforms;android-31" \
          "build-tools;31.0.0"
    
    # 6️⃣ Install Buildozer
    - name: Install Buildozer
      run: |
        pip install --upgrade pip setuptools wheel
        pip install buildozer==1.5.0
        pip install cython==0.29.36
    
    # 7️⃣ Cache Buildozer
    - name: Cache Buildozer
      uses: actions/cache@v3
      with:
        path: |
          ~/.buildozer
          android/.buildozer
        key: buildozer-single-arch-${{ hashFiles('android/buildozer.spec') }}-v4
        restore-keys: |
          buildozer-single-arch-
    
    # 8️⃣ Build APK (SINGLE ARCHITECTURE)
    - name: Build APK
      working-directory: android
      run: |
        export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk
        export ANDROID_SDK_ROOT=$ANDROID_HOME
        export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH
        
        # Build dengan verbose untuk debugging
        buildozer -v android debug
      timeout-minutes: 90
    
    # 9️⃣ Upload APK
    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: device-tracker-apk
        path: android/bin/*.apk
        if-no-files-found: warn
    
    # 🔟 Upload build logs jika gagal
    - name: Upload build logs
      if: failure()
      uses: actions/upload-artifact@v4
      with:
        name: buildozer-logs
        path: |
          android/.buildozer/android/platform/build-*/
          ~/.buildozer/android/logs/
