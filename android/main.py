"""
Android Device Tracking Agent - PRODUCTION VERSION
For deployment with hosted backend
"""

import os
import json
import time
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

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass
    import requests
    
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    LocationManager = autoclass('android.location.LocationManager')
    Context = autoclass('android.content.Context')
    BatteryManager = autoclass('android.os.BatteryManager')
    Intent = autoclass('android.content.Intent')
else:
    import requests

# ===================================
# CONFIGURATION - PRODUCTION
# ===================================
class Config:
    # PRODUCTION API URL - Change before deployment!
    API_BASE_URL = "https://datakah06.pythonanywhere.com"
    
    LOCATION_INTERVAL_SECONDS = 120
    BATCH_SIZE = 10
    MAX_CACHE_SIZE = 100


class LocationCollector:
    def __init__(self):
        self.location_manager = None
        self.context = None
        
        if platform == 'android':
            self.context = PythonActivity.mActivity
            self.location_manager = self.context.getSystemService(
                Context.LOCATION_SERVICE
            )
    
    def get_battery_level(self):
        try:
            if platform == 'android':
                intent_filter = autoclass('android.content.IntentFilter')(
                    Intent.ACTION_BATTERY_CHANGED
                )
                battery_status = self.context.registerReceiver(None, intent_filter)
                
                level = battery_status.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                scale = battery_status.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                
                battery_pct = (level / float(scale)) * 100
                return int(battery_pct)
            else:
                return 100
        except Exception as e:
            print(f"Battery error: {e}")
            return 100
    
    def get_network_status(self):
        try:
            response = requests.get("http://www.google.com", timeout=2)
            return "online"
        except:
            return "offline"
    
    def get_location(self):
        try:
            if platform == 'android':
                location = self.location_manager.getLastKnownLocation(
                    LocationManager.GPS_PROVIDER
                )
                
                if location:
                    return {
                        "lat": location.getLatitude(),
                        "lng": location.getLongitude()
                    }
                
                location = self.location_manager.getLastKnownLocation(
                    LocationManager.NETWORK_PROVIDER
                )
                
                if location:
                    return {
                        "lat": location.getLatitude(),
                        "lng": location.getLongitude()
                    }
            
            response = requests.get("http://ip-api.com/json/", timeout=5)
            data = response.json()
            
            if data.get("status") == "success":
                return {
                    "lat": data.get("lat", 0.0),
                    "lng": data.get("lon", 0.0)
                }
        except Exception as e:
            print(f"Location error: {e}")
        
        return {"lat": -6.175, "lng": 106.827}
    
    def collect(self):
        location = self.get_location()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "lat": location["lat"],
            "lng": location["lng"],
            "battery": self.get_battery_level(),
            "network": self.get_network_status()
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
        self.username_file = self.data_dir / "username.txt"
        self.cache_file = self.data_dir / "location_cache.json"
    
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
            with open(self.device_id_file, 'r') as f:
                return f.read().strip()
        
        device_id = f"dev{uuid.uuid4().hex[:8]}"
        with open(self.device_id_file, 'w') as f:
            f.write(device_id)
        
        return device_id
    
    def save_username(self, username):
        self.username = username
        with open(self.username_file, 'w') as f:
            f.write(username)
    
    def load_cache(self):
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
            except:
                self.cache = []
    
    def save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def register_device(self):
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/devices/register",
                json={
                    "device_id": self.device_id,
                    "username": self.username,
                    "consent": True
                },
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def send_locations(self, locations):
        try:
            response = requests.post(
                f"{Config.API_BASE_URL}/locations/submit",
                json={
                    "device_id": self.device_id,
                    "locations": locations
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            elif response.status_code == 403:
                self.is_revoked = True
                return False
            else:
                return False
        except Exception as e:
            print(f"Send error: {e}")
            return False
    
    def collect_and_cache(self):
        location = self.collector.collect()
        self.cache.append(location)
        
        if len(self.cache) > Config.MAX_CACHE_SIZE:
            self.cache = self.cache[-Config.MAX_CACHE_SIZE:]
        
        self.save_cache()
        return location
    
    def sync_cache(self):
        if not self.cache or self.is_revoked:
            return False
        
        batch = self.cache[:Config.BATCH_SIZE]
        
        if self.send_locations(batch):
            self.cache = self.cache[len(batch):]
            self.save_cache()
            return True
        
        return False
    
    def start(self, username):
        self.device_id = self.get_or_create_device_id()
        self.save_username(username)
        self.load_cache()
        
        if not self.register_device():
            return False
        
        self.running = True
        return True
    
    def stop(self):
        self.running = False
        if self.cache:
            self.sync_cache()


class ConsentScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        
        title = Label(
            text='[b]LOCATION TRACKING[/b]',
            markup=True,
            size_hint=(1, 0.1),
            font_size='24sp',
            color=(1, 1, 1, 1)
        )
        self.add_widget(title)
        
        username_label = Label(
            text='Your Name:',
            size_hint=(1, 0.08),
            font_size='16sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(username_label)
        
        self.username_input = TextInput(
            hint_text='Enter your name',
            size_hint=(1, 0.1),
            font_size='18sp',
            multiline=False,
            background_color=(0.2, 0.2, 0.3, 1),
            foreground_color=(1, 1, 1, 1),
            padding=[15, 15]
        )
        self.add_widget(self.username_input)
        
        scroll = ScrollView(size_hint=(1, 0.47))
        info_text = Label(
            text='''This app collects:

✓ GPS Location (every 2 minutes)
✓ Battery Level
✓ Network Status

Purpose:
• Device monitoring (7 days)
• Location tracking
• Security audit

Your Rights:
• Revoke access anytime
• Data deletion available
• All actions are logged

By agreeing, you consent to
location tracking.''',
            size_hint=(1, None),
            text_size=(None, None),
            halign='left',
            font_size='14sp',
            color=(0.9, 0.9, 0.9, 1)
        )
        info_text.bind(
            texture_size=lambda instance, value: setattr(
                instance, 'size', value
            )
        )
        scroll.add_widget(info_text)
        self.add_widget(scroll)
        
        button_layout = BoxLayout(
            size_hint=(1, 0.15),
            spacing=10
        )
        
        agree_btn = Button(
            text='I AGREE',
            font_size='18sp',
            background_color=(0.06, 0.73, 0.51, 1),
            bold=True
        )
        agree_btn.bind(on_press=self.on_agree)
        
        decline_btn = Button(
            text='DECLINE',
            font_size='18sp',
            background_color=(0.94, 0.27, 0.27, 1)
        )
        decline_btn.bind(on_press=self.on_decline)
        
        button_layout.add_widget(agree_btn)
        button_layout.add_widget(decline_btn)
        
        self.add_widget(button_layout)
    
    def on_agree(self, instance):
        username = self.username_input.text.strip()
        
        if not username:
            popup = Popup(
                title='Error',
                content=Label(text='Please enter your name'),
                size_hint=(0.8, 0.3)
            )
            popup.open()
            return
        
        self.app.on_consent_given(username)
    
    def on_decline(self, instance):
        self.app.stop()


class TrackingScreen(BoxLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        header = Label(
            text='[b]Tracking Active[/b]',
            markup=True,
            size_hint=(1, 0.08),
            font_size='20sp',
            color=(0.06, 0.73, 0.51, 1)
        )
        self.add_widget(header)
        
        self.user_label = Label(
            text='User: Loading...',
            size_hint=(1, 0.08),
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        self.add_widget(self.user_label)
        
        self.status_label = Label(
            text='Status: Initializing...',
            size_hint=(1, 0.08),
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.status_label)
        
        self.location_label = Label(
            text='Location: Waiting...',
            size_hint=(1, 0.08),
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.location_label)
        
        self.cache_label = Label(
            text='Cached: 0',
            size_hint=(1, 0.08),
            font_size='14sp',
            color=(0.8, 0.8, 0.8, 1)
        )
        self.add_widget(self.cache_label)
        
        scroll = ScrollView(size_hint=(1, 0.45))
        self.log_label = Label(
            text='',
            size_hint=(1, None),
            text_size=(None, None),
            halign='left',
            font_size='11sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.log_label.bind(
            texture_size=lambda instance, value: setattr(
                instance, 'size', value
            )
        )
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)
        
        stop_btn = Button(
            text='STOP TRACKING',
            size_hint=(1, 0.15),
            font_size='16sp',
            background_color=(0.94, 0.27, 0.27, 1)
        )
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
            
            Clock.schedule_interval(
                self.tracking_loop,
                Config.LOCATION_INTERVAL_SECONDS
            )
        else:
            self.tracking_screen.update_status('Failed')
            self.tracking_screen.add_log('✗ Registration failed')
    
    def tracking_loop(self, dt):
        if not self.agent.running or self.agent.is_revoked:
            return False
        
        try:
            location = self.agent.collect_and_cache()
            
            self.tracking_screen.update_location(
                location['lat'],
                location['lng']
            )
            self.tracking_screen.update_cache(len(self.agent.cache))
            self.tracking_screen.add_log(
                f'📍 Collected | Battery: {location["battery"]}%'
            )
            
            if self.agent.sync_cache():
                self.tracking_screen.add_log('✓ Synced')
            
            status = 'REVOKED' if self.agent.is_revoked else 'ACTIVE'
            self.tracking_screen.update_status(status)
            
        except Exception as e:
            self.tracking_screen.add_log(f'✗ {str(e)}')
        
        return True
    
    def on_stop(self):
        self.agent.stop()


if __name__ == '__main__':
    TrackerApp().run()
