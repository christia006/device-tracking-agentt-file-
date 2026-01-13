"""
Android Device Tracking Agent - PRODUCTION VERSION
Optimized for small APK size
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

# Android imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    LocationManager = autoclass('android.location.LocationManager')
    Context = autoclass('android.content.Context')
    BatteryManager = autoclass('android.os.BatteryManager')
    Intent = autoclass('android.content.Intent')

# Requests import
try:
    import requests
except ImportError:
    requests = None

# CONFIGURATION
API_BASE_URL = "https://datakah06.pythonanywhere.com"
LOCATION_INTERVAL = 120  # seconds
BATCH_SIZE = 10
MAX_CACHE_SIZE = 100


class LocationCollector:
    def __init__(self):
        self.location_manager = None
        self.context = None
        
        if platform == 'android':
            self.context = PythonActivity.mActivity
            self.location_manager = self.context.getSystemService(Context.LOCATION_SERVICE)
    
    def get_battery_level(self):
        try:
            if platform == 'android':
                intent_filter = autoclass('android.content.IntentFilter')(Intent.ACTION_BATTERY_CHANGED)
                battery_status = self.context.registerReceiver(None, intent_filter)
                level = battery_status.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                scale = battery_status.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                return int((level / float(scale)) * 100) if scale > 0 else 100
            return 100
        except:
            return 100
    
    def get_location(self):
        try:
            if platform == 'android':
                for provider in [LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER]:
                    location = self.location_manager.getLastKnownLocation(provider)
                    if location:
                        return {
                            "lat": location.getLatitude(),
                            "lng": location.getLongitude()
                        }
            
            # Fallback to IP geolocation
            if requests:
                response = requests.get("http://ip-api.com/json/", timeout=5)
                data = response.json()
                if data.get("status") == "success":
                    return {"lat": data.get("lat", 0.0), "lng": data.get("lon", 0.0)}
        except:
            pass
        
        return {"lat": -6.175, "lng": 106.827}  # Default Jakarta
    
    def collect(self):
        location = self.get_location()
        return {
            "timestamp": datetime.now().isoformat(),
            "lat": location["lat"],
            "lng": location["lng"],
            "battery": self.get_battery_level(),
            "network": "online" if requests else "offline"
        }


class DeviceAgent:
    def __init__(self):
        self.device_id = None
        self.username = None
        self.cache = []
        self.is_revoked = False
        self.running = False
        self.collector = LocationCollector()
        
        self.data_dir = self._get_data_dir()
        self.device_id_file = self.data_dir / "device_id.txt"
        self.cache_file = self.data_dir / "cache.json"
    
    def _get_data_dir(self):
        if platform == 'android':
            from android.storage import app_storage_path
            data_dir = Path(app_storage_path())
        else:
            data_dir = Path.cwd()
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def get_or_create_device_id(self):
        if self.device_id_file.exists():
            return self.device_id_file.read_text().strip()
        device_id = f"dev{uuid.uuid4().hex[:8]}"
        self.device_id_file.write_text(device_id)
        return device_id
    
    def load_cache(self):
        if self.cache_file.exists():
            try:
                self.cache = json.loads(self.cache_file.read_text())
            except:
                self.cache = []
    
    def save_cache(self):
        self.cache_file.write_text(json.dumps(self.cache))
    
    def register_device(self):
        if not requests:
            return False
        try:
            response = requests.post(
                f"{API_BASE_URL}/devices/register",
                json={"device_id": self.device_id, "username": self.username, "consent": True},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def send_locations(self, locations):
        if not requests:
            return False
        try:
            response = requests.post(
                f"{API_BASE_URL}/locations/submit",
                json={"device_id": self.device_id, "locations": locations},
                timeout=10
            )
            if response.status_code == 403:
                self.is_revoked = True
            return response.status_code == 200
        except:
            return False
    
    def collect_and_cache(self):
        location = self.collector.collect()
        self.cache.append(location)
        if len(self.cache) > MAX_CACHE_SIZE:
            self.cache = self.cache[-MAX_CACHE_SIZE:]
        self.save_cache()
        return location
    
    def sync_cache(self):
        if not self.cache or self.is_revoked:
            return False
        batch = self.cache[:BATCH_SIZE]
        if self.send_locations(batch):
            self.cache = self.cache[len(batch):]
            self.save_cache()
            return True
        return False
    
    def start(self, username):
        self.device_id = self.get_or_create_device_id()
        self.username = username
        self.load_cache()
        if not self.register_device():
            return False
        self.running = True
        return True


class ConsentScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        self.add_widget(Label(text='[b]LOCATION TRACKING[/b]', markup=True, 
                             size_hint=(1, 0.1), font_size='24sp'))
        
        self.add_widget(Label(text='Your Name:', size_hint=(1, 0.08), font_size='16sp'))
        
        self.username_input = TextInput(hint_text='Enter your name', size_hint=(1, 0.1), 
                                       font_size='18sp', multiline=False)
        self.add_widget(self.username_input)
        
        scroll = ScrollView(size_hint=(1, 0.47))
        info = Label(text='''This app collects:
✓ GPS Location (every 2 minutes)
✓ Battery Level
✓ Network Status

Backend: datakah06.pythonanywhere.com

By agreeing, you consent to location tracking.''',
                    size_hint=(1, None), halign='left', font_size='14sp')
        info.bind(texture_size=lambda i, v: setattr(i, 'size', v))
        scroll.add_widget(info)
        self.add_widget(scroll)
        
        buttons = BoxLayout(size_hint=(1, 0.15), spacing=10)
        agree_btn = Button(text='I AGREE', font_size='18sp', 
                          background_color=(0.06, 0.73, 0.51, 1))
        agree_btn.bind(on_press=self.on_agree)
        decline_btn = Button(text='DECLINE', font_size='18sp',
                            background_color=(0.94, 0.27, 0.27, 1))
        decline_btn.bind(on_press=lambda x: self.app.stop())
        buttons.add_widget(agree_btn)
        buttons.add_widget(decline_btn)
        self.add_widget(buttons)
    
    def on_agree(self, instance):
        username = self.username_input.text.strip()
        if not username:
            Popup(title='Error', content=Label(text='Please enter your name'),
                 size_hint=(0.8, 0.3)).open()
            return
        self.app.on_consent_given(username)


class TrackingScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        self.add_widget(Label(text='[b]Tracking Active[/b]', markup=True,
                             size_hint=(1, 0.08), font_size='20sp',
                             color=(0.06, 0.73, 0.51, 1)))
        
        self.user_label = Label(text='User: Loading...', size_hint=(1, 0.08), font_size='16sp')
        self.add_widget(self.user_label)
        
        self.status_label = Label(text='Status: Initializing...', size_hint=(1, 0.08), font_size='14sp')
        self.add_widget(self.status_label)
        
        self.location_label = Label(text='Location: Waiting...', size_hint=(1, 0.08), font_size='14sp')
        self.add_widget(self.location_label)
        
        self.cache_label = Label(text='Cached: 0', size_hint=(1, 0.08), font_size='14sp')
        self.add_widget(self.cache_label)
        
        scroll = ScrollView(size_hint=(1, 0.43))
        self.log_label = Label(text='', size_hint=(1, None), halign='left', font_size='11sp')
        self.log_label.bind(texture_size=lambda i, v: setattr(i, 'size', v))
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)
        
        stop_btn = Button(text='STOP TRACKING', size_hint=(1, 0.15), font_size='16sp',
                         background_color=(0.94, 0.27, 0.27, 1))
        stop_btn.bind(on_press=lambda x: self.app.stop())
        self.add_widget(stop_btn)
    
    def update_username(self, username):
        self.user_label.text = f'User: {username}'
    
    def update_status(self, text):
        self.status_label.text = f'Status: {text}'
    
    def update_location(self, lat, lng):
        self.location_label.text = f'Location: {lat:.6f}, {lng:.6f}'
    
    def update_cache(self, count):
        self.cache_label.text = f'Cached: {count}'
    
    def add_log(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_label.text += f'\n[{timestamp}] {message}'


class TrackerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.agent = DeviceAgent()
        self.tracking_screen = None
    
    def build(self):
        self.title = 'Device Tracker'
        return ConsentScreen(self)
    
    def on_start(self):
        if platform == 'android':
            request_permissions([
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION,
                Permission.INTERNET,
                Permission.ACCESS_NETWORK_STATE
            ])
    
    def on_consent_given(self, username):
        self.tracking_screen = TrackingScreen(self)
        self.root.clear_widgets()
        self.root.add_widget(self.tracking_screen)
        
        if self.agent.start(username):
            self.tracking_screen.update_username(username)
            self.tracking_screen.add_log('✓ Device registered')
            Clock.schedule_interval(self.tracking_loop, LOCATION_INTERVAL)
        else:
            self.tracking_screen.update_status('Failed')
            self.tracking_screen.add_log('✗ Registration failed')
    
    def tracking_loop(self, dt):
        if not self.agent.running or self.agent.is_revoked:
            return False
        
        try:
            location = self.agent.collect_and_cache()
            self.tracking_screen.update_location(location['lat'], location['lng'])
            self.tracking_screen.update_cache(len(self.agent.cache))
            self.tracking_screen.add_log(f'📍 Collected | Battery: {location["battery"]}%')
            
            if self.agent.sync_cache():
                self.tracking_screen.add_log('✓ Synced to backend')
            
            status = 'REVOKED' if self.agent.is_revoked else 'ACTIVE'
            self.tracking_screen.update_status(status)
        except Exception as e:
            self.tracking_screen.add_log(f'✗ {str(e)}')
        
        return True
    
    def on_stop(self):
        self.agent.running = False
        if self.agent.cache:
            self.agent.sync_cache()


if __name__ == '__main__':
    TrackerApp().run()
```

## 📂 Struktur Folder:
```
your-repo/
├── .github/
│   └── workflows/
│       └── main.yml
└── android/
    ├── buildozer.spec
    └── main.py
