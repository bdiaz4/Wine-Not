from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.camera import Camera
from kivy.uix.spinner import Spinner
import os
import time
import csv
import threading
import pandas as pd
from datetime import datetime
Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        spacing: 10
        ToggleButton:
            text: 'Play'
            on_press: root.toggle_play()
            size_hint: 0.5, 1
        Button:
            text: 'Capture'
            on_press: root.capture()
            size_hint: 0.5, 1
''')

class CameraClick(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            self.camera = Camera(resolution=(640, 480), play=False)
            self.add_widget(self.camera)
        except Exception as e:
            self.camera = None
            no_camera_label = Label(text="No camera available", font_size=18)
            self.add_widget(no_camera_label)

    def toggle_play(self):
        if self.camera:
            self.camera.play = not self.camera.play

    def capture(self):
        if self.camera:
            def on_ok(instance):
                filename = textinput.text.strip()
                if not filename:
                    filename = time.strftime("%Y%m%d_%H%M%S")
                wine_images_dir = os.path.join(os.path.dirname(__file__), 'wineImages')
                os.makedirs(wine_images_dir, exist_ok=True)
                filepath = os.path.join(wine_images_dir, f"{filename}.png")
                self.camera.export_to_png(filepath)
                print(f"Captured: {filepath}")
                # Return to add wine screen
                app = App.get_running_app()
                app.root.current = "add_wine"
                popup.dismiss()

            textinput = TextInput(text=time.strftime("%Y%m%d_%H%M%S"), multiline=False)
            button = Button(text='OK', size_hint_y=None, height=50)
            button.bind(on_press=on_ok)
            content = BoxLayout(orientation='vertical')
            content.add_widget(textinput)
            content.add_widget(button)
            popup = Popup(title='Enter filename', content=content, size_hint=(0.8, 0.4))
            popup.open()
        else:
            print("No camera available for capture")

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app is not None:
            with self.canvas.before:
                from kivy.graphics import Color, Rectangle
                self.bg_color = Color(*app.theme['background'])
                self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def go_home(self, instance):
        self.manager.current = "home"

    def create_header(self):
        app = App.get_running_app()
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)

        self.title_button = Button(
            text="Wine Not?",
            font_size=28,
            size_hint=(1, 0.65),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        self.title_button.bind(on_press=self.go_home)
        header.add_widget(self.title_button)

        self.subtitle = Label(
            text="Tap title to return home",
            font_size=14,
            size_hint=(1, 0.35),
            color=app.theme['text']
        )
        header.add_widget(self.subtitle)
        return header

    def apply_theme(self):
        app = App.get_running_app()
        if hasattr(self, 'bg_color'):
            self.bg_color.rgba = app.theme['background']
        if hasattr(self, 'bg_rect'):
            self.bg_rect.size = self.size
            self.bg_rect.pos = self.pos

        for widget in self.walk():
            if hasattr(widget, 'color'):
                try:
                    widget.color = app.theme['text']
                except Exception:
                    pass
            if hasattr(widget, 'background_color'):
                try:
                    widget.background_color = app.theme['box']
                except Exception:
                    pass
            if hasattr(widget, 'background_normal') and isinstance(widget, Spinner):
                widget.background_normal = ''


class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()

        self.layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15
        )

        self.title = Label(
            text="Wine Not?",
            font_size=30,
            size_hint=(1, 0.2),
            color=app.theme['text']
        )
        self.layout.add_widget(self.title)

        self.subtitle = Label(
            text="Your personal wine assistant",
            font_size=16,
            size_hint=(1, 0.1),
            color=app.theme['text']
        )
        self.layout.add_widget(self.subtitle)

        self.profile_button = Button(
            text="My Profile",
            font_size=20,
            size_hint=(1, 0.17),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        self.profile_button.bind(on_press=self.go_profile)
        self.layout.add_widget(self.profile_button)

        self.add_wine_button = Button(
            text="Add Wine",
            font_size=20,
            size_hint=(1, 0.17),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        self.add_wine_button.bind(on_press=self.go_add_wine)
        self.layout.add_widget(self.add_wine_button)

        self.recommend_button = Button(
            text="Get Recommendation",
            font_size=20,
            size_hint=(1, 0.17),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        self.recommend_button.bind(on_press=self.upload_menu)
        self.layout.add_widget(self.recommend_button)

        self.settings_button = Button(
            text="Settings",
            font_size=20,
            size_hint=(1, 0.17),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        self.settings_button.bind(on_press=self.go_settings)
        self.layout.add_widget(self.settings_button)

        self.add_widget(self.layout)

        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            self.bg_color = Color(*app.theme['background'])
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

    def apply_theme(self):
        app = App.get_running_app()
        if hasattr(self, 'bg_color'):
            self.bg_color.rgba = app.theme['background']
        self.title.color = app.theme['text']
        self.subtitle.color = app.theme['text']
        for button in [self.profile_button, self.add_wine_button, self.recommend_button, self.settings_button]:
            button.color = app.theme['text']
            button.background_color = app.theme['box']

    def go_profile(self, instance):
        self.manager.current = "profile"

    def go_add_wine(self, instance):
        self.manager.current = "add_wine"

    def go_recommendation(self, instance):
        self.manager.current = "recommendation"

    def go_settings(self, instance):
        self.manager.current = "settings"

    def upload_menu(self, instance):
        self.manager.current = 'menu_text_input'

class SavedWinesScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Saved Wines",
            font_size=22,
            size_hint=(1, 0.08)
        )
        layout.add_widget(section_label)

        wine_scroll = ScrollView(
            size_hint=(1, 0.92)
        )
        self.wine_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.wine_container.bind(minimum_height=self.wine_container.setter('height'))
        wine_scroll.add_widget(self.wine_container)
        layout.add_widget(wine_scroll)

        self.add_widget(layout)

    def on_enter(self):
        self.load_wines()

    def get_wine_from_dataset(self, wine_name):
        """Lookup wine data from WineDataset.csv"""
        try:
            dataset_path = os.path.join(os.path.dirname(__file__), 'WineDataset.csv')
            df = pd.read_csv(dataset_path)
            
            # Search for wine in dataset
            for _, row in df.iterrows():
                if str(row['Title']).lower() == wine_name.lower():
                    return {
                        "Wine Name": row['Title'],
                        "Types": row.get('Type', 'N/A'),
                        "Country": row.get('Country', 'N/A'),
                        "Characteristics": row.get('Characteristics', 'N/A'),
                        "ABV": row.get('ABV', 'N/A'),
                        "Region": row.get('Region', 'N/A') if pd.notna(row.get('Region', None)) else "N/A",
                        "Style": row.get('Style', 'N/A') if pd.notna(row.get('Style', None)) else "N/A"
                    }
            
            # If exact match not found, try partial match
            from wineMatching import findBestMatch
            best_row, score = findBestMatch(wine_name, df, 'Title')
            if best_row is not None and score >= 0.35:
                return {
                    "Wine Name": best_row['Title'],
                    "Types": best_row.get('Type', 'N/A'),
                    "Country": best_row.get('Country', 'N/A'),
                    "Characteristics": best_row.get('Characteristics', 'N/A'),
                    "ABV": best_row.get('ABV', 'N/A'),
                    "Region": best_row.get('Region', 'N/A') if pd.notna(best_row.get('Region', None)) else "N/A",
                    "Style": best_row.get('Style', 'N/A') if pd.notna(best_row.get('Style', None)) else "N/A"
                }
        except Exception as e:
            print(f"Error looking up wine: {e}")
        
        return None

    def show_wine_details(self, wine_name):
        """Navigate to wine details screen for clicked wine"""
        wine_data = self.get_wine_from_dataset(wine_name)
        if wine_data:
            app = App.get_running_app()
            app.selected_wine = wine_data
            self.manager.current = "wine_details"
        else:
            popup = Popup(
                title='Wine Not Found',
                content=Label(text=f"Could not find details for '{wine_name}'"),
                size_hint=(0.7, 0.3)
            )
            popup.open()

    def load_wines(self):
        self.wine_container.clear_widgets()
        csv_path = os.path.join(os.path.dirname(__file__), 'wineCollection.csv')
        images_dir = os.path.join(os.path.dirname(__file__), 'wineImages')
        
        if not os.path.exists(csv_path):
            error_label = Label(text="Wine collection file not found", font_size=16)
            self.wine_container.add_widget(error_label)
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    wine_card = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=160,
                        spacing=10
                    )
                    
                    # Image
                    image_filename = row.get('Image', '')
                    image_path = os.path.join(images_dir, image_filename)
                    
                    if os.path.exists(image_path):
                        img = Image(
                            source=image_path,
                            size_hint=(None, 1),
                            width=120
                        )
                        wine_card.add_widget(img)
                    
                    # Wine info
                    info_layout = BoxLayout(
                        orientation='vertical',
                        size_hint=(1, 1),
                        spacing=5,
                        padding=(15, 5, 5, 5)
                    )
                    
                    # Wine name as clickable button
                    wine_name_btn = Button(
                        text=row.get('Wine Name', 'Unknown'),
                        font_size=14,
                        size_hint_y=None,
                        height=65,
                        background_color=(0.2, 0.5, 0.8, 1)
                    )
                    wine_name_btn.wine_name = row.get('Wine Name', 'Unknown')
                    wine_name_btn.bind(on_press=lambda btn: self.show_wine_details(btn.wine_name))
                    info_layout.add_widget(wine_name_btn)
                    
                    # Metadata layout
                    metadata_layout = BoxLayout(
                        orientation='horizontal',
                        size_hint=(1, None),
                        height=25,
                        spacing=5
                    )
                    
                    count = Label(
                        text=f"Count: {row.get('Count', 'N/A')}",
                        font_size=12,
                        size_hint_x=0.3
                    )
                    metadata_layout.add_widget(count)
                    
                    date_added = Label(
                        text=f"Date Added: {row.get('Date Added', 'N/A')}",
                        font_size=12,
                        size_hint_x=0.4
                    )
                    metadata_layout.add_widget(date_added)
                    
                    info_layout.add_widget(metadata_layout)
                    
                    # Favorite button
                    favorite = row.get('Favorite', 'False') == 'True'
                    favorite_button = ToggleButton(
                        text="Favorite" if favorite else "Save to Favorites",
                        font_size=10,
                        size_hint_y=None,
                        height=25,
                        state='down' if favorite else 'normal'
                    )
                    favorite_button.wine_name = row.get('Wine Name')
                    favorite_button.bind(on_press=self.toggle_favorite)
                    info_layout.add_widget(favorite_button)
                    
                    wine_card.add_widget(info_layout)
                    self.wine_container.add_widget(wine_card)
        except Exception as e:
            error_label = Label(text=f"Error loading wines: {str(e)}", font_size=16)
            self.wine_container.add_widget(error_label)

    def toggle_favorite(self, instance):
        from wineProcessing import toggleFavorite
        is_fav = toggleFavorite(instance.wine_name)
        instance.text = "Favorite" if is_fav else "Save to Favorites"
        instance.state = 'down' if is_fav else 'normal'


class FavoritesScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Favorite Wines",
            font_size=22,
            size_hint=(1, 0.08)
        )
        layout.add_widget(section_label)

        wine_scroll = ScrollView(
            size_hint=(1, 0.92)
        )
        self.wine_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.wine_container.bind(minimum_height=self.wine_container.setter('height'))
        wine_scroll.add_widget(self.wine_container)
        layout.add_widget(wine_scroll)

        self.add_widget(layout)

    def on_enter(self):
        self.load_wines()

    def get_wine_from_dataset(self, wine_name):
        """Lookup wine data from WineDataset.csv"""
        try:
            dataset_path = os.path.join(os.path.dirname(__file__), 'WineDataset.csv')
            df = pd.read_csv(dataset_path)
            
            # Search for wine in dataset
            for _, row in df.iterrows():
                if str(row['Title']).lower() == wine_name.lower():
                    return {
                        "Wine Name": row['Title'],
                        "Types": row.get('Type', 'N/A'),
                        "Country": row.get('Country', 'N/A'),
                        "Characteristics": row.get('Characteristics', 'N/A'),
                        "ABV": row.get('ABV', 'N/A'),
                        "Region": row.get('Region', 'N/A') if pd.notna(row.get('Region', None)) else "N/A",
                        "Style": row.get('Style', 'N/A') if pd.notna(row.get('Style', None)) else "N/A"
                    }
            
            # If exact match not found, try partial match
            from wineMatching import findBestMatch
            best_row, score = findBestMatch(wine_name, df, 'Title')
            if best_row is not None and score >= 0.35:
                return {
                    "Wine Name": best_row['Title'],
                    "Types": best_row.get('Type', 'N/A'),
                    "Country": best_row.get('Country', 'N/A'),
                    "Characteristics": best_row.get('Characteristics', 'N/A'),
                    "ABV": best_row.get('ABV', 'N/A'),
                    "Region": best_row.get('Region', 'N/A') if pd.notna(best_row.get('Region', None)) else "N/A",
                    "Style": best_row.get('Style', 'N/A') if pd.notna(best_row.get('Style', None)) else "N/A"
                }
        except Exception as e:
            print(f"Error looking up wine: {e}")
        
        return None

    def show_wine_details(self, wine_name):
        """Navigate to wine details screen for clicked wine"""
        wine_data = self.get_wine_from_dataset(wine_name)
        if wine_data:
            app = App.get_running_app()
            app.selected_wine = wine_data
            self.manager.current = "wine_details"
        else:
            popup = Popup(
                title='Wine Not Found',
                content=Label(text=f"Could not find details for '{wine_name}'"),
                size_hint=(0.7, 0.3)
            )
            popup.open()

    def load_wines(self):
        self.wine_container.clear_widgets()
        csv_path = os.path.join(os.path.dirname(__file__), 'wineCollection.csv')
        images_dir = os.path.join(os.path.dirname(__file__), 'wineImages')
        
        if not os.path.exists(csv_path):
            error_label = Label(text="Wine collection file not found", font_size=16)
            self.wine_container.add_widget(error_label)
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                favorites = [row for row in reader if row.get('Favorite', 'False') == 'True']
                for row in favorites:
                    wine_card = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=160,
                        spacing=10
                    )
                    
                    # Image
                    image_filename = row.get('Image', '')
                    image_path = os.path.join(images_dir, image_filename)
                    
                    if os.path.exists(image_path):
                        img = Image(
                            source=image_path,
                            size_hint=(None, 1),
                            width=120
                        )
                        wine_card.add_widget(img)
                    
                    # Wine info
                    info_layout = BoxLayout(
                        orientation='vertical',
                        size_hint=(1, 1),
                        spacing=5,
                        padding=(15, 5, 5, 5)
                    )
                    
                    # Wine name as clickable button
                    wine_name_btn = Button(
                        text=row.get('Wine Name', 'Unknown'),
                        font_size=14,
                        size_hint_y=None,
                        height=65,
                        background_color=(0.2, 0.5, 0.8, 1)
                    )
                    wine_name_btn.wine_name = row.get('Wine Name', 'Unknown')
                    wine_name_btn.bind(on_press=lambda btn: self.show_wine_details(btn.wine_name))
                    info_layout.add_widget(wine_name_btn)
                    
                    # Metadata layout
                    metadata_layout = BoxLayout(
                        orientation='horizontal',
                        size_hint=(1, None),
                        height=25,
                        spacing=5
                    )
                    
                    count = Label(
                        text=f"Count: {row.get('Count', 'N/A')}",
                        font_size=12,
                        size_hint_x=0.3
                    )
                    metadata_layout.add_widget(count)
                    
                    date_added = Label(
                        text=f"Date Added: {row.get('Date Added', 'N/A')}",
                        font_size=12,
                        size_hint_x=0.4
                    )
                    metadata_layout.add_widget(date_added)
                    
                    info_layout.add_widget(metadata_layout)
                    
                    favorite = True  # since it's favorites screen
                    favorite_button = ToggleButton(
                        text="Favorite" if favorite else "Save to Favorites",
                        font_size=10,
                        size_hint_y=None,
                        height=25,
                        state='down' if favorite else 'normal'
                    )
                    favorite_button.wine_name = row.get('Wine Name')
                    favorite_button.bind(on_press=self.toggle_favorite)
                    info_layout.add_widget(favorite_button)
                    
                    wine_card.add_widget(info_layout)
                    self.wine_container.add_widget(wine_card)
        except Exception as e:
            error_label = Label(text=f"Error loading wines: {str(e)}", font_size=16)
            self.wine_container.add_widget(error_label)

    def toggle_favorite(self, instance):
        from wineProcessing import toggleFavorite
        is_fav = toggleFavorite(instance.wine_name)
        instance.text = "Favorite" if is_fav else "Save to Favorites"
        instance.state = 'down' if is_fav else 'normal'
        # If no longer favorite, remove from this screen
        if not is_fav:
            # Find the parent card and remove it
            card = instance.parent.parent
            self.wine_container.remove_widget(card)


class ProfileScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="My Profile",
            font_size=22,
            size_hint=(1, 0.12)
        )
        layout.add_widget(section_label)

        saved_button = Button(
            text="Saved Wines",
            font_size=18,
            size_hint=(1, 0.14)
        )
        saved_button.bind(on_press=self.show_saved_wines)
        layout.add_widget(saved_button)

        favorites_button = Button(
            text="Favorites",
            font_size=18,
            size_hint=(1, 0.14)
        )
        favorites_button.bind(on_press=self.show_favorites)
        layout.add_widget(favorites_button)

        recent_button = Button(
            text="Recently Saved",
            font_size=18,
            size_hint=(1, 0.14)
        )
        recent_button.bind(on_press=self.show_recent)
        layout.add_widget(recent_button)

        edit_button = Button(
            text="Edit Wines",
            font_size=18,
            size_hint=(1, 0.14)
        )
        edit_button.bind(on_press=self.edit_profile)
        layout.add_widget(edit_button)

        preferences_button = Button(
            text="Edit Preferences",
            font_size=18,
            size_hint=(1, 0.14)
        )
        preferences_button.bind(on_press=self.my_preferences)
        layout.add_widget(preferences_button)

        user_profile_button = Button(
            text="User Preferences",
            font_size=18,
            size_hint=(1, 0.14)
        )
        user_profile_button.bind(on_press=self.user_profile)
        layout.add_widget(user_profile_button)

        self.result_label = Label(
            text="Profile options will appear here",
            font_size=16,
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.result_label)

        self.add_widget(layout)

    def show_saved_wines(self, instance):
        self.manager.current = "saved_wines"

    def show_favorites(self, instance):
        self.manager.current = "favorites"

    def show_recent(self, instance):
        self.manager.current = "recently_saved"

    def edit_profile(self, instance):
        self.manager.current = "edit_profile"

    def my_preferences(self, instance):
        self.manager.current = "my_preferences"

    def user_profile(self, instance):
        self.manager.current = "user_profile"


class AddWineScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Add Wine",
            font_size=22,
            size_hint=(1, 0.14)
        )
        layout.add_widget(section_label)

        upload_button = Button(
            text="Upload Picture",
            font_size=18,
            size_hint=(1, 0.18)
        )
        upload_button.bind(on_press=self.upload_picture)
        layout.add_widget(upload_button)

        manual_button = Button(
            text="Add Manually",
            font_size=18,
            size_hint=(1, 0.18)
        )
        manual_button.bind(on_press=self.add_manually)
        layout.add_widget(manual_button)

        self.result_label = Label(
            text="Choose how to add a wine",
            font_size=16,
            size_hint=(1, 0.25)
        )
        layout.add_widget(self.result_label)

        self.add_widget(layout)
        self.main_layout = layout
        self.in_upload_mode = False

    def on_enter(self):
        # Refresh the image grid if we were in upload mode and returned from camera
        if self.in_upload_mode:
            self.refresh_image_grid()

    def upload_picture(self, instance):
        self.in_upload_mode = True
        self.clear_widgets()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)

        layout.add_widget(self.create_header())

        section_label = Label(text="Wine Images", font_size=22, size_hint=(1, 0.14))

        layout.add_widget(section_label)

        camera_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        camera_button = Button(text="Take New Photo", font_size=16)
        camera_button.bind(on_press=self.take_photo)
        camera_box.add_widget(camera_button)
        layout.add_widget(camera_box)

        self.grid = GridLayout(cols=3, spacing=10, size_hint=(1, 0.6))

        self.selected_label = Label(text="Select an image", font_size=16, size_hint=(1, 0.1))

        self.populate_image_grid()
        
        layout.add_widget(self.grid)
        layout.add_widget(self.selected_label)

        self.add_widget(layout)

    def populate_image_grid(self):
        """Populate the image grid with images from wineImages folder"""
        self.grid.clear_widgets()
        
        image_folder = 'wineImages/'

        if os.path.exists(image_folder):
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    button = Button(
                        background_normal=os.path.join(image_folder, filename),
                        size_hint=(None, None),
                        size=(200, 200)
                    )
                    button.bind(on_press=lambda instance, fn=filename: self.select_image(fn))
                    self.grid.add_widget(button)

    def refresh_image_grid(self):
        """Refresh the image grid to show newly captured photos"""
        if self.in_upload_mode and hasattr(self, 'grid'):
            self.populate_image_grid()

    def add_manually(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Enter Wine Name:", font_size=16))
        wine_input = TextInput(multiline=False, size_hint_y=None, height=40)
        content.add_widget(wine_input)
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        def on_add(instance):
            wine_name = wine_input.text.strip()
            if wine_name:
                from wineProcessing import wineCollection
                wineCollection(wine_name)
                app = App.get_running_app()
                app.add_recent_wine(wine_name)
                self.result_label.text = f"Added '{wine_name}' manually"
                popup.dismiss()
            else:
                self.result_label.text = "Wine name cannot be empty"
        
        add_button = Button(text='Add Wine')
        add_button.bind(on_press=on_add)
        buttons.add_widget(add_button)
        
        cancel_button = Button(text='Cancel')
        cancel_button.bind(on_press=lambda x: popup.dismiss())
        buttons.add_widget(cancel_button)
        
        content.add_widget(buttons)
        
        popup = Popup(title='Add Wine Manually', content=content, size_hint=(0.8, 0.4))
        popup.open()

    def select_image(self, filename):
        Clock.schedule_once(lambda dt: self.do_process_image(filename), 0.1)

    def do_process_image(self, filename):
        self.loading_popup = Popup(title='Processing', content=Label(text='Processing image...\nPlease wait while we analyze the wine label.'), size_hint=(0.6, 0.4), auto_dismiss=False)
        self.loading_popup.open()
        
        image_path = os.path.join('wineImages', filename)
        
        def process_thread():
            from wineProcessing import process_wine_image
            result = process_wine_image(image_path)
            Clock.schedule_once(lambda dt: self.show_result(result, filename), 0)
        
        threading.Thread(target=process_thread).start()

    def show_result(self, result, filename):
        self.loading_popup.dismiss()
        
        from wineProcessing import wineCollection
        
        if result['matched']:
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            content.add_widget(Label(text=f"Extracted Text: {result['extracted_text']}", font_size=14))
            content.add_widget(Label(text=f"Best Match Text: {result['best_text']}", font_size=14))
            content.add_widget(Label(text=f"Matched Wine: {result['wine_name']}", font_size=16, bold=True))
            content.add_widget(Label(text=f"Confidence Score: {result['score']:.2f}", font_size=14))
            
            buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
            
            def on_confirm(instance):
                wineCollection(result['wine_name'], filename)
                app = App.get_running_app()
                app.add_recent_wine(result['wine_name'], filename)
                self.selected_label.text = f"Added {result['wine_name']} to collection"
                popup.dismiss()
            
            confirm_button = Button(text='Add to Collection', size_hint_x=0.5)
            confirm_button.bind(on_press=on_confirm)
            buttons.add_widget(confirm_button)
            
            cancel_button = Button(text='Cancel', size_hint_x=0.5)
            cancel_button.bind(on_press=lambda x: popup.dismiss())
            buttons.add_widget(cancel_button)
            
            content.add_widget(buttons)
            
            popup = Popup(title='Wine Processing Result', content=content, size_hint=(0.9, 0.7))
            popup.open()
        else:
            content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            if 'error' in result:
                content.add_widget(Label(text=result['error'], font_size=16))
            else:
                content.add_widget(Label(text="Could not identify wine from image", font_size=16))
                content.add_widget(Label(text=f"Extracted Text: {result.get('extracted_text', '')}", font_size=14))
                content.add_widget(Label(text=f"Best Attempt: {result.get('best_text', '')}", font_size=14))
                content.add_widget(Label(text=f"Score: {result.get('score', 0):.2f}", font_size=14))
            
            close_button = Button(text='Close', size_hint_y=None, height=50)
            close_button.bind(on_press=lambda x: popup.dismiss())
            content.add_widget(close_button)
            
            popup = Popup(title='Processing Failed', content=content, size_hint=(0.8, 0.6))
            popup.open()

    def take_photo(self, instance):
        self.manager.current = "camera"


class CameraScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(self.create_header())
        
        camera_click = CameraClick()
        layout.add_widget(camera_click)
        
        cancel_button = Button(text="Cancel", size_hint_y=None, height='48dp')
        cancel_button.bind(on_press=self.cancel_camera)
        layout.add_widget(cancel_button)
        
        self.add_widget(layout)
    
    def cancel_camera(self, instance):
        self.manager.current = "add_wine"


class RecentlySavedScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Recently Saved",
            font_size=22,
            size_hint=(1, 0.08)
        )
        layout.add_widget(section_label)

        wine_scroll = ScrollView(
            size_hint=(1, 0.92)
        )
        self.wine_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.wine_container.bind(minimum_height=self.wine_container.setter('height'))
        wine_scroll.add_widget(self.wine_container)
        layout.add_widget(wine_scroll)

        self.add_widget(layout)

    def on_enter(self):
        self.load_recent_wines()

    def load_recent_wines(self):
        self.wine_container.clear_widgets()
        app = App.get_running_app()
        
        if not app.recently_saved_wines:
            empty_label = Label(text="No wines saved in this session yet", font_size=16)
            self.wine_container.add_widget(empty_label)
            return
        
        # Sort by timestamp (most recent first)
        sorted_wines = sorted(app.recently_saved_wines, key=lambda x: x['timestamp'], reverse=True)
        
        current_time = time.time()
        
        for wine_data in sorted_wines:
            minutes_ago = int((current_time - wine_data['timestamp']) / 60)
            if minutes_ago == 0:
                time_str = "Just now"
            elif minutes_ago == 1:
                time_str = "1 minute ago"
            else:
                time_str = f"{minutes_ago} minutes ago"
            
            wine_card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=100,
                spacing=10
            )
            
            # Image
            image_filename = wine_data.get('image', '')
            if image_filename:
                images_dir = os.path.join(os.path.dirname(__file__), 'wineImages')
                image_path = os.path.join(images_dir, image_filename)
                
                if os.path.exists(image_path):
                    img = Image(
                        source=image_path,
                        size_hint=(None, 1),
                        width=80
                    )
                    wine_card.add_widget(img)
            
            # Wine info
            info_layout = BoxLayout(
                orientation='vertical',
                size_hint=(1, 1),
                spacing=5,
                padding=(10, 5, 5, 5)
            )
            
            wine_name = Label(
                text=wine_data.get('name', 'Unknown'),
                font_size=14,
                size_hint_y=None,
                height=35,
                text_size=(240, None),
                markup=True,
                halign='left',
                valign='top'
            )
            info_layout.add_widget(wine_name)
            
            time_label = Label(
                text=time_str,
                font_size=12,
                size_hint_y=None,
                height=25,
                color=(0.7, 0.7, 0.7, 1)
            )
            info_layout.add_widget(time_label)
            
            wine_card.add_widget(info_layout)
            self.wine_container.add_widget(wine_card)


class EditProfileScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Edit Wines",
            font_size=22,
            size_hint=(1, 0.08)
        )
        layout.add_widget(section_label)

        wine_scroll = ScrollView(
            size_hint=(1, 0.92)
        )
        self.wine_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10,
            padding=10
        )
        self.wine_container.bind(minimum_height=self.wine_container.setter('height'))
        wine_scroll.add_widget(self.wine_container)
        layout.add_widget(wine_scroll)

        self.add_widget(layout)

    def on_enter(self):
        self.load_wines()

    def load_wines(self):
        self.wine_container.clear_widgets()
        csv_path = os.path.join(os.path.dirname(__file__), 'wineCollection.csv')
        
        if not os.path.exists(csv_path):
            error_label = Label(text="Wine collection file not found", font_size=16)
            self.wine_container.add_widget(error_label)
            return
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    wine_card = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=80,
                        spacing=10
                    )
                    
                    # Wine info
                    info_layout = BoxLayout(
                        orientation='vertical',
                        size_hint=(0.6, 1),
                        spacing=5,
                        padding=(10, 5, 5, 5)
                    )
                    
                    wine_name = Label(
                        text=row.get('Wine Name', 'Unknown'),
                        font_size=13,
                        size_hint_y=None,
                        height=35,
                        text_size=(200, None),
                        markup=True,
                        halign='left',
                        valign='top'
                    )
                    info_layout.add_widget(wine_name)
                    
                    count = Label(
                        text=f"Count: {row.get('Count', '0')}",
                        font_size=11,
                        size_hint_y=None,
                        height=25
                    )
                    info_layout.add_widget(count)
                    
                    wine_card.add_widget(info_layout)
                    
                    # Buttons
                    buttons_layout = BoxLayout(
                        orientation='horizontal',
                        size_hint=(0.4, 1),
                        spacing=5
                    )
                    
                    edit_button = Button(
                        text='Edit',
                        font_size=11,
                        size_hint_x=0.5
                    )
                    edit_button.wine_name = row.get('Wine Name')
                    edit_button.wine_row = row
                    edit_button.bind(on_press=self.on_edit_wine)
                    buttons_layout.add_widget(edit_button)
                    
                    delete_button = Button(
                        text='Delete',
                        font_size=11,
                        size_hint_x=0.5,
                        background_color=(1, 0.5, 0.5, 1)
                    )
                    delete_button.wine_name = row.get('Wine Name')
                    delete_button.bind(on_press=self.on_delete_wine)
                    buttons_layout.add_widget(delete_button)
                    
                    wine_card.add_widget(buttons_layout)
                    self.wine_container.add_widget(wine_card)
        except Exception as e:
            error_label = Label(text=f"Error loading wines: {str(e)}", font_size=16)
            self.wine_container.add_widget(error_label)

    def on_edit_wine(self, instance):
        wine_name = instance.wine_name
        wine_row = instance.wine_row
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Rename section
        content.add_widget(Label(text="Rename Wine:", font_size=14, size_hint_y=None, height=30))
        rename_input = TextInput(text=wine_name, multiline=False, size_hint_y=None, height=40)
        content.add_widget(rename_input)
        
        # Amount section
        content.add_widget(Label(text="Amount:", font_size=14, size_hint_y=None, height=30))
        amount_input = TextInput(text=wine_row.get('Count', '0'), multiline=False, size_hint_y=None, height=40, input_filter='int')
        content.add_widget(amount_input)
        
        # Buttons
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        def on_save(instance):
            new_name = rename_input.text.strip()
            new_amount = amount_input.text.strip()
            
            if not new_name:
                new_name = wine_name
            if not new_amount:
                new_amount = wine_row.get('Count', '0')
            
            from wineProcessing import updateWine
            updateWine(wine_name, new_name, new_amount)
            self.load_wines()
            popup.dismiss()
        
        save_button = Button(text='Save')
        save_button.bind(on_press=on_save)
        buttons.add_widget(save_button)
        
        cancel_button = Button(text='Cancel')
        cancel_button.bind(on_press=lambda x: popup.dismiss())
        buttons.add_widget(cancel_button)
        
        content.add_widget(buttons)
        
        popup = Popup(title=f'Edit Wine: {wine_name}', content=content, size_hint=(0.85, 0.7))
        popup.open()

    def on_delete_wine(self, instance):
        wine_name = instance.wine_name
        
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text=f"Delete '{wine_name}'?", font_size=16))
        content.add_widget(Label(text="This action cannot be undone.", font_size=12))
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        def on_confirm(instance):
            from wineProcessing import deleteWine
            deleteWine(wine_name)
            self.load_wines()
            popup.dismiss()
        
        confirm_button = Button(text='Delete', background_color=(1, 0.5, 0.5, 1))
        confirm_button.bind(on_press=on_confirm)
        buttons.add_widget(confirm_button)
        
        cancel_button = Button(text='Cancel')
        cancel_button.bind(on_press=lambda x: popup.dismiss())
        buttons.add_widget(cancel_button)
        
        content.add_widget(buttons)
        
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.8, 0.5))
        popup.open()






class MenuTextInputScreen(BaseScreen):
    """Screen for entering wine names from a menu via text input"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Enter Wine Names from Menu",
            font_size=22,
            size_hint=(1, 0.12)
        )
        layout.add_widget(section_label)

        instructions = Label(
            text="Enter one wine name per line:",
            font_size=14,
            size_hint=(1, 0.08)
        )
        layout.add_widget(instructions)

        # Text input for wine names
        self.wine_input = TextInput(
            multiline=True,
            size_hint=(1, 0.55),
            hint_text="Wine Name 1\nWine Name 2\nWine Name 3"
        )
        layout.add_widget(self.wine_input)

        # Buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 0.1),
            spacing=10
        )

        process_button = Button(
            text="Process Menu",
            font_size=16,
            size_hint=(0.6, 1)
        )
        process_button.bind(on_press=self.process_wines)
        button_layout.add_widget(process_button)

        cancel_button = Button(
            text="Cancel",
            font_size=16,
            size_hint=(0.4, 1)
        )
        cancel_button.bind(on_press=self.cancel_menu)
        button_layout.add_widget(cancel_button)

        layout.add_widget(button_layout)

        self.add_widget(layout)

    def process_wines(self, instance):
        wine_text = self.wine_input.text.strip()
        if not wine_text:
            self.wine_input.hint_text = "Please enter at least one wine name"
            return
        
        # Process the text input
        from wineMatching import processMenuText
        try:
            results = processMenuText(wine_text)
            
            # Store results in app for MenuResultsScreen to access
            app = App.get_running_app()
            app.menu_results = results
            
            # Navigate to results screen
            self.manager.current = "menu_results"
        except Exception as e:
            self.wine_input.hint_text = f"Error: {str(e)}"

    def cancel_menu(self, instance):
        self.manager.current = "recommendation"


class PreferencesScreen(BaseScreen):
    """Screen for selecting wine preferences"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.category_spinners = {}
        self.options = self.load_preferences_data()
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        layout.add_widget(self.create_header())
        
        section_label = Label(text="Add Preferences", font_size=22, size_hint=(1, 0.08))
        layout.add_widget(section_label)
        
        scroll = ScrollView(size_hint=(1, 0.92))
        scroll_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))
        
        categories = ['Types', 'Country', 'Characteristics', 'ABV', 'Region', 'Style']
        
        for category in categories:
            cat_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
            
            spinner = Spinner(
                text=f"Select {category}",
                values=self.options.get(category, []),
                size_hint=(0.7, 1)
            )
            self.category_spinners[category] = spinner
            cat_layout.add_widget(spinner)
            
            plus_btn = Button(text="+", size_hint=(0.3, 1))
            plus_btn.category = category
            plus_btn.bind(on_press=self.add_preference)
            cat_layout.add_widget(plus_btn)
            
            scroll_layout.add_widget(cat_layout)
        
        scroll.add_widget(scroll_layout)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def load_preferences_data(self):
        """Parse Preferences.txt to get all preferences"""
        options = {
            'Types': [],
            'Country': [],
            'Characteristics': [],
            'ABV': [],
            'Region': [],
            'Style': []
        }
        
        try:
            with open('Preferences.txt', 'r',encoding='utf-8') as content:
                line= content.readline().strip()
                while line:
                    if not line:
                        continue
                    # Check if this is a category header
                    for cat in options.keys():
                        if line.startswith(f"{cat}["):
                            current_category = cat
                            # Extract values from bracket
                            values_str = line[len(cat)+1:line.rfind(']')]
                            if values_str:
                                # Parse the list
                                values = [v.strip().strip("'\"") for v in values_str.split(',')]
                                options[cat] = values
                            break
                    line= content.readline().strip()
            
            return options
        except Exception as e:
            print(f"Error loading preferences: {e}")
            return options
    
    def add_preference(self, instance):
        """Add selected preference to myProfile.csv"""
        category = instance.category
        spinner = self.category_spinners[category]
        selected_value = spinner.text
        
        if selected_value == f"Select {category}":
            popup = Popup(title='Error', content=Label(text=f'Please select a {category}'), size_hint=(0.6, 0.3))
            popup.open()
            return
        
        # Add to myProfile.csv
        profile_path = 'myProfile.csv'
        
        try:
            # Read existing data
            if os.path.exists(profile_path):
                df = pd.read_csv(profile_path)
            else:
                df = pd.DataFrame(columns=['Types', 'Country', 'Characteristics', 'ABV', 'Region', 'Style'])
            
            # Ensure empty strings instead of NaN
            df = df.fillna('')
            empty_row_index = None

            for idx, row in df.iterrows():
                if row[category] == '':
                    empty_row_index = idx
                    break

            if empty_row_index is not None:
                #fill existing row if exist
                df.at[empty_row_index, category] = selected_value
            else:
                #create new row
                new_row = {col: '' for col in df.columns}
                new_row[category] = selected_value
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

            df.to_csv(profile_path, index=False)
            
            # Reset spinner
            spinner.text = f"Select {category}"
            
            # Show confirmation
            popup = Popup(title='Added', content=Label(text=f'{selected_value} added to preferences'), size_hint=(0.6, 0.3))
            popup.open()
            
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Error saving preference: {str(e)}'), size_hint=(0.6, 0.3))
            popup.open()


class UserProfileScreen(BaseScreen):
    """Screen to display saved user preferences"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        layout.add_widget(self.create_header())
        
        section_label = Label(text="User Preferences", font_size=22, size_hint=(1, 0.08))
        layout.add_widget(section_label)
        
        scroll = ScrollView(size_hint=(1, 0.85))
        self.profile_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10, padding=10)
        self.profile_layout.bind(minimum_height=self.profile_layout.setter('height'))
        scroll.add_widget(self.profile_layout)
        layout.add_widget(scroll)
        
        clear_btn = Button(text="Clear All Preferences", size_hint=(1, 0.07), background_color=(1, 0.5, 0.5, 1))
        clear_btn.bind(on_press=self.clear_preferences)
        layout.add_widget(clear_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.load_profile_data()
    
    def load_profile_data(self):
        """Load and display preferences from myProfile.csv"""
        self.profile_layout.clear_widgets()
        
        profile_path = 'myProfile.csv'
        
        if not os.path.exists(profile_path):
            empty_label = Label(text="No preferences saved yet", font_size=16)
            self.profile_layout.add_widget(empty_label)
            return
        
        try:
            df = pd.read_csv(profile_path)
            
            if df.empty:
                empty_label = Label(text="No preferences saved yet", font_size=16)
                self.profile_layout.add_widget(empty_label)
                return
            
            # Display preferences grouped by category
            for col in df.columns:
                # Get all non-empty values for this category
                values = df[col].dropna()
                values = [str(v) for v in values if str(v).strip() != '']

                if values:
                    pref_layout = BoxLayout(
                        orientation='horizontal',
                        size_hint_y=None,
                        height=50,
                        spacing=10
                    )

                    # Join all values into one line
                    pref_text = f"{col}: " + ", ".join(values)

                    pref_label = Label(
                        text=pref_text,
                        font_size=12,
                        size_hint=(0.8, 1)
                    )
                    pref_layout.add_widget(pref_label)

                    # Optional: delete button per category (clears whole column)
                    delete_btn = Button(
                        text="X",
                        size_hint=(0.2, 1),
                        background_color=(1, 0.5, 0.5, 1)
                    )
                    delete_btn.category = col
                    delete_btn.bind(on_press=self.delete_preference)
                    pref_layout.add_widget(delete_btn)

                    self.profile_layout.add_widget(pref_layout)
        
        except Exception as e:
            error_label = Label(text=f"Error loading profile: {str(e)}", font_size=14)
            self.profile_layout.add_widget(error_label)
    
    def delete_preference(self, instance):
        """Delete a specific preference"""
        category = instance.category
        profile_path = 'myProfile.csv'
        
        try:
            df = pd.read_csv(profile_path)
            df[category] = ''  # clear column
            df.to_csv(profile_path, index=False)
            self.load_profile_data()
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Error deleting preference: {str(e)}'), size_hint=(0.6, 0.3))
            popup.open()
    
    def clear_preferences(self, instance):
        """Clear all preferences"""
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Clear all preferences?", font_size=16))
        content.add_widget(Label(text="This action cannot be undone.", font_size=12))
        
        buttons = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        def confirm_clear(inst):
            profile_path = 'myProfile.csv'
            try:
                df = pd.read_csv(profile_path)
                df = df.iloc[0:0]  # Clear all rows
                df.to_csv(profile_path, index=False)
                popup.dismiss()
                self.load_profile_data()
            except Exception as e:
                popup.dismiss()
                error_popup = Popup(title='Error', content=Label(text=f'Error clearing: {str(e)}'), size_hint=(0.6, 0.3))
                error_popup.open()
        
        confirm_btn = Button(text='Clear')
        confirm_btn.bind(on_press=confirm_clear)
        buttons.add_widget(confirm_btn)
        
        cancel_btn = Button(text='Cancel')
        buttons.add_widget(cancel_btn)
        
        content.add_widget(buttons)
        
        popup = Popup(title='Confirm Clear', content=content, size_hint=(0.8, 0.5))
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()


class MenuResultsScreen(BaseScreen):
    """Screen displaying identified wines from menu text input"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Menu Results",
            font_size=22,
            size_hint=(1, 0.12)
        )
        layout.add_widget(section_label)

        # Scrollable results area
        results_scroll = ScrollView(size_hint=(1, 0.75))
        self.results_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=8,
            padding=10
        )
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        results_scroll.add_widget(self.results_container)
        layout.add_widget(results_scroll)

        # Add to collection button
        add_button = Button(
            text="Add Selected to Collection",
            font_size=16,
            size_hint=(1, 0.08)
        )
        add_button.bind(on_press=self.add_to_collection)
        layout.add_widget(add_button)

        self.add_widget(layout)

    def load_user_preferences(self):
        """Load user preferences from myProfile.csv"""
        preferences = {}
        try:
            if os.path.exists('myProfile.csv'):
                df = pd.read_csv('myProfile.csv')
                for col in df.columns:
                    values = df[col].dropna()
                    values = [str(v).strip() for v in values if str(v).strip()]
                    preferences[col] = values
        except Exception as e:
            print(f"Error loading preferences: {e}")
        return preferences

    def wine_matches_preferences(self, wine_data, preferences):
        """Check if wine matches any user preferences"""
        if not preferences:
            return False
        
        # Fields to check from wine data
        wine_fields = {
            'Types': wine_data.get('Types', ''),
            'Country': wine_data.get('Country', ''),
            'Characteristics': wine_data.get('Characteristics', ''),
            'ABV': wine_data.get('ABV', ''),
            'Region': wine_data.get('Region', ''),
            'Style': wine_data.get('Style', '')
        }
        
        # Check if any wine field value matches any user preference
        for pref_category, pref_values in preferences.items():
            if pref_category in wine_fields:
                wine_value = str(wine_fields[pref_category]).lower().strip()
                for pref_value in pref_values:
                    if pref_value.lower() in wine_value or wine_value in pref_value.lower():
                        return True
        
        return False

    def on_enter(self):
        self.user_preferences = self.load_user_preferences()
        self.display_results()

    def display_results(self):
        self.results_container.clear_widgets()
        
        app = App.get_running_app()
        if not hasattr(app, 'menu_results') or not app.menu_results:
            error_label = Label(text="No results to display", font_size=14, size_hint_y=None, height=50)
            self.results_container.add_widget(error_label)
            return
        
        results = app.menu_results
        
        # Display matched wines
        if results['matched_wines']:
            matched_label = Label(
                text=f"Matched Wines ({results['total_matched']}/{results['total_input']})",
                font_size=16,
                size_hint_y=None,
                height=40,
                bold=True
            )
            self.results_container.add_widget(matched_label)
            
            for wine in results['matched_wines']:
                is_recommended = self.wine_matches_preferences(wine, self.user_preferences)
                wine_card = self.create_wine_card(wine, is_recommended)
                self.results_container.add_widget(wine_card)
        
        # Display unmatched wines
        if results['unmatched_wines']:
            unmatched_label = Label(
                text=f"Unmatched ({len(results['unmatched_wines'])})",
                font_size=14,
                size_hint_y=None,
                height=35,
                color=(1, 0.5, 0.5, 1)
            )
            self.results_container.add_widget(unmatched_label)
            
            for wine in results['unmatched_wines']:
                unmatched_card = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=60,
                    padding=10,
                    spacing=5
                )
                unmatched_card.canvas.before.clear()
                from kivy.graphics import Color, Rectangle
                with unmatched_card.canvas.before:
                    Color(0.3, 0.3, 0.3, 0.5)
                    Rectangle(size=unmatched_card.size, pos=unmatched_card.pos)
                
                title = Label(
                    text=f"'{wine['Original Input']}' (confidence: {wine['Confidence']:.2f})",
                    font_size=13,
                    size_hint_y=None,
                    height=30
                )
                unmatched_card.add_widget(title)
                
                note = Label(
                    text="Not found in database",
                    font_size=11,
                    size_hint_y=None,
                    height=25,
                    color=(1, 0.7, 0.7, 1)
                )
                unmatched_card.add_widget(note)
                
                self.results_container.add_widget(unmatched_card)

    def create_wine_card(self, wine_data, is_recommended=False):
        """Create a clickable card for a wine result"""
        card_height = 150 if is_recommended else 120
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=card_height,
            padding=10,
            spacing=5
        )
        
        # Store wine data on the card for later access
        card.wine_data = wine_data
        
        # Recommendation label if applicable
        if is_recommended:
            rec_label = Label(
                text="Recommended Based on your Preferences!",
                font_size=12,
                size_hint_y=None,
                height=25,
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            )
            card.add_widget(rec_label)
        
        # Wine name (clickable)
        name_btn = Button(
            text=wine_data['Wine Name'],
            font_size=14,
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.5, 0.8, 1)
        )
        name_btn.bind(on_press=self.show_wine_details)
        card.add_widget(name_btn)
        
        # Confidence score
        confidence_label = Label(
            text=f"Confidence: {wine_data['Confidence']:.2%}",
            font_size=11,
            size_hint_y=None,
            height=20,
            color=(0.7, 0.7, 0.7, 1)
        )
        card.add_widget(confidence_label)
        
        # Quick info
        info_text = f"{wine_data['Types']} • {wine_data['Country']} • {wine_data['ABV']}"
        info_label = Label(
            text=info_text,
            font_size=11,
            size_hint_y=None,
            height=30
        )
        card.add_widget(info_label)
        
        return card

    def show_wine_details(self, instance):
        """Navigate to wine details screen"""
        # Find parent card with wine_data
        parent = instance.parent
        while parent and not hasattr(parent, 'wine_data'):
            parent = parent.parent
        
        if parent and hasattr(parent, 'wine_data'):
            app = App.get_running_app()
            app.selected_wine = parent.wine_data
            self.manager.current = "wine_details"

    def add_to_collection(self, instance):
        """Add matched wines to collection"""
        app = App.get_running_app()
        if not hasattr(app, 'menu_results'):
            return
        
        from wineProcessing import wineCollection
        
        added_count = 0
        for wine in app.menu_results['matched_wines']:
            try:
                wineCollection(wine['Wine Name'])
                app.add_recent_wine(wine['Wine Name'])
                added_count += 1
            except Exception as e:
                print(f"Error adding {wine['Wine Name']}: {str(e)}")
        
        popup = Popup(
            title='Added to Collection',
            content=Label(text=f"Successfully added {added_count} wine(s) to your collection!"),
            size_hint=(0.7, 0.3)
        )
        popup.open()
        
        # Return to recommendation screen
        Clock.schedule_once(lambda dt: self.go_home(None), 2)


class WineDetailsScreen(BaseScreen):
    """Screen displaying detailed wine information"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        # Scrollable details area
        details_scroll = ScrollView(size_hint=(1, 0.85))
        self.details_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=15,
            padding=10
        )
        self.details_container.bind(minimum_height=self.details_container.setter('height'))
        details_scroll.add_widget(self.details_container)
        layout.add_widget(details_scroll)

        # Add to collection button
        add_button = Button(
            text="Add to Collection",
            font_size=16,
            size_hint=(1, 0.08)
        )
        add_button.bind(on_press=self.add_wine_to_collection)
        layout.add_widget(add_button)

        self.add_widget(layout)

    def on_enter(self):
        self.display_wine_details()

    def display_wine_details(self):
        self.details_container.clear_widgets()
        
        app = App.get_running_app()
        if not hasattr(app, 'selected_wine') or not app.selected_wine:
            error_label = Label(
                text="No wine selected",
                font_size=14,
                size_hint_y=None,
                height=50
            )
            self.details_container.add_widget(error_label)
            return
        
        wine = app.selected_wine
        
        # Wine name - title
        name_label = Label(
            text=wine['Wine Name'],
            font_size=18,
            bold=True,
            size_hint_y=None,
            height=50
        )
        self.details_container.add_widget(name_label)
        
        # Display the 6 required fields
        fields = [
            ("Type", wine.get('Types', 'N/A')),
            ("Country", wine.get('Country', 'N/A')),
            ("Characteristics", wine.get('Characteristics', 'N/A')),
            ("ABV", wine.get('ABV', 'N/A')),
            ("Region", wine.get('Region', 'N/A')),
            ("Style", wine.get('Style', 'N/A'))
        ]
        
        for field_name, field_value in fields:
            field_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=100,
                padding=30,
                spacing=5
            )
            if field_name=="Characteristics": #Allow room for up to 4 entries
                field_box = BoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    height=100,
                    padding=30,
                    spacing=30
                )
            label_header = Label(
                text=f"{field_name}:",
                font_size=13,
                bold=True,
                size_hint_y=None,
                height=25
            )
            field_box.add_widget(label_header)
            
            label_value = Label(
                text=str(field_value),
                font_size=12,
                size_hint_y=None,
                height=40,
                text_size=(field_box.width - 20, None)
            )
            field_box.add_widget(label_value)
            
            self.details_container.add_widget(field_box)

    def add_wine_to_collection(self, instance):
        """Add the displayed wine to collection"""
        app = App.get_running_app()
        if not hasattr(app, 'selected_wine'):
            return
        
        from wineProcessing import wineCollection
        wine_name = app.selected_wine['Wine Name']
        
        try:
            wineCollection(wine_name)
            app.add_recent_wine(wine_name)
            popup = Popup(
                title='Added to Collection',
                content=Label(text=f"'{wine_name}' added to your collection!"),
                size_hint=(0.7, 0.3)
            )
            popup.open()
            
            # Close after 2 seconds
            Clock.schedule_once(lambda dt: popup.dismiss(), 2)
        except Exception as e:
            popup = Popup(
                title='Error',
                content=Label(text=f"Error: {str(e)}"),
                size_hint=(0.7, 0.3)
            )
            popup.open()


class SettingsScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Settings",
            font_size=22,
            size_hint=(1, 0.14)
        )
        layout.add_widget(section_label)

        reset_data_button = Button(
            text="Reset Data",
            font_size=18,
            size_hint=(1, 0.18)
        )
        reset_data_button.bind(on_press=self.reset_data)
        layout.add_widget(reset_data_button)

        theme_button = Button(
            text="Theme",
            font_size=18,
            size_hint=(1, 0.18)
        )
        theme_button.bind(on_press=self.theme)
        layout.add_widget(theme_button)

        self.result_label = Label(
            text="Settings options will appear here",
            font_size=16,
            size_hint=(1, 0.25)
        )
        layout.add_widget(self.result_label)

        self.add_widget(layout)

    def reset_data(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        content.add_widget(Label(text="Reset ALL profile data?", font_size=16))
        content.add_widget(Label(text="This will delete preferences and saved data.\nThis cannot be undone.", font_size=12))

        buttons = BoxLayout(size_hint_y=None, height=50, spacing=10)

        def confirm_reset(inst):
            try:
                # --- CLEAR FILES ---
                # Clear preferences
                if os.path.exists('myProfile.csv'):
                    df = pd.read_csv('myProfile.csv')
                    df = df.iloc[0:0]
                    df.to_csv('myProfile.csv', index=False)

                # Clear wine collection
                if os.path.exists('wineCollection.csv'):
                    df = pd.read_csv('wineCollection.csv')
                    df = df.iloc[0:0]
                    df.to_csv('wineCollection.csv', index=False)

                popup.dismiss()
                self.result_label.text = "All data has been reset."

            except Exception as e:
                popup.dismiss()
                error_popup = Popup(
                    title='Error',
                    content=Label(text=str(e)),
                    size_hint=(0.6, 0.3)
                )
                error_popup.open()

        confirm_btn = Button(text="Yes, Reset", background_color=(1, 0.3, 0.3, 1))
        confirm_btn.bind(on_press=confirm_reset)

        cancel_btn = Button(text="Cancel")
        
        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_btn)

        content.add_widget(buttons)

        popup = Popup(title="Confirm Reset", content=content, size_hint=(0.8, 0.5))
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()
            

    def theme(self, instance):
        self.manager.current = "theme"


class ThemeScreen(BaseScreen):
    colors = {
        'White': (1, 1, 1, 1),
        'Black': (0, 0, 0, 1),
        'Gray': (0.5, 0.5, 0.5, 1),
        'Blue': (0, 0, 1, 1),
        'Green': (0, 1, 0, 1),
        'Red': (1, 0, 0, 1),
        'Yellow': (1, 1, 0, 1),
        'Purple': (0.5, 0, 0.5, 1)
    }
    reverse_colors = {v: k for k, v in colors.items()}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()

        self.layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        self.layout.add_widget(self.create_header())

        self.section_label = Label(
            text="Theme Settings",
            font_size=22,
            size_hint=(1, 0.1),
            color=app.theme['text']
        )
        self.layout.add_widget(self.section_label)

        bg_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        self.bg_label = Label(text="Background:", size_hint=(0.4, 1), color=app.theme['text'])
        self.bg_spinner = Spinner(
            text='White',
            values=('White', 'Black', 'Gray', 'Blue', 'Green', 'Red', 'Yellow', 'Purple'),
            size_hint=(0.6, 1),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        bg_layout.add_widget(self.bg_label)
        bg_layout.add_widget(self.bg_spinner)
        self.layout.add_widget(bg_layout)

        text_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        self.text_label = Label(text="Text:", size_hint=(0.4, 1), color=app.theme['text'])
        self.text_spinner = Spinner(
            text='Black',
            values=('White', 'Black', 'Gray', 'Blue', 'Green', 'Red', 'Yellow', 'Purple'),
            size_hint=(0.6, 1),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        text_layout.add_widget(self.text_label)
        text_layout.add_widget(self.text_spinner)
        self.layout.add_widget(text_layout)

        box_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15))
        self.box_label = Label(text="Boxes:", size_hint=(0.4, 1), color=app.theme['text'])
        self.box_spinner = Spinner(
            text='Gray',
            values=('White', 'Black', 'Gray', 'Blue', 'Green', 'Red', 'Yellow', 'Purple'),
            size_hint=(0.6, 1),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        box_layout.add_widget(self.box_label)
        box_layout.add_widget(self.box_spinner)
        self.layout.add_widget(box_layout)

        self.save_button = Button(
            text="Save Theme",
            font_size=18,
            size_hint=(1, 0.15),
            background_color=app.theme['box'],
            color=app.theme['text']
        )
        self.save_button.bind(on_press=self.save_theme)
        self.layout.add_widget(self.save_button)

        self.status_label = Label(
            text="",
            font_size=16,
            size_hint=(1, 0.1),
            color=app.theme['text']
        )
        self.layout.add_widget(self.status_label)

        self.add_widget(self.layout)

        self.load_theme()

    def load_theme(self):
        app = App.get_running_app()
        app_theme = app.theme
        self.bg_spinner.text = self.reverse_colors.get(app_theme['background'], 'White')
        self.text_spinner.text = self.reverse_colors.get(app_theme['text'], 'Black')
        self.box_spinner.text = self.reverse_colors.get(app_theme['box'], 'Gray')

    def save_theme(self, instance):
        theme = {
            'background': self.bg_spinner.text,
            'text': self.text_spinner.text,
            'box': self.box_spinner.text
        }
        theme_file = os.path.join(os.path.dirname(__file__), 'theme.json')
        import json
        with open(theme_file, 'w') as f:
            json.dump(theme, f)
        self.status_label.text = "Theme saved!"
        app = App.get_running_app()
        app.theme = {
            'background': self.colors[self.bg_spinner.text],
            'text': self.colors[self.text_spinner.text],
            'box': self.colors[self.box_spinner.text]
        }
        self.apply_theme_to_all_screens()

    def apply_theme(self):
        super().apply_theme()
        app = App.get_running_app()
        self.section_label.color = app.theme['text']
        for widget in [self.bg_label, self.text_label, self.box_label, self.status_label]:
            widget.color = app.theme['text']
        for spinner in [self.bg_spinner, self.text_spinner, self.box_spinner]:
            spinner.color = app.theme['text']
            spinner.background_color = app.theme['box']
        self.save_button.color = app.theme['text']
        self.save_button.background_color = app.theme['box']

    def apply_theme_to_all_screens(self):
        app = App.get_running_app()
        for screen in app.root.screens:
            if hasattr(screen, 'apply_theme'):
                screen.apply_theme()


class WineApp(App):
    colors = {
        'White': (1, 1, 1, 1),
        'Black': (0, 0, 0, 1),
        'Gray': (0.5, 0.5, 0.5, 1),
        'Blue': (0, 0, 1, 1),
        'Green': (0, 1, 0, 1),
        'Red': (1, 0, 0, 1),
        'Yellow': (1, 1, 0, 1),
        'Purple': (0.5, 0, 0.5, 1)
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recently_saved_wines = []
        self.menu_results = None
        self.selected_wine = None
        self.theme = self.load_theme()
    
    def load_theme(self):
        theme_file = os.path.join(os.path.dirname(__file__), 'theme.json')
        if os.path.exists(theme_file):
            import json
            with open(theme_file, 'r') as f:
                theme_names = json.load(f)
            return {
                'background': self.colors.get(theme_names.get('background', 'White'), (1,1,1,1)),
                'text': self.colors.get(theme_names.get('text', 'Black'), (0,0,0,1)),
                'box': self.colors.get(theme_names.get('box', 'Gray'), (0.5,0.5,0.5,1))
            }
        else:
            return {
                'background': (1,1,1,1),
                'text': (0,0,0,1),
                'box': (0.5,0.5,0.5,1)
            }

    def add_recent_wine(self, wine_name, image_filename=''):
        """Add a wine to the recently saved list"""
        self.recently_saved_wines.append({
            'name': wine_name,
            'image': image_filename,
            'timestamp': time.time()
        })
    
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(SavedWinesScreen(name="saved_wines"))
        sm.add_widget(FavoritesScreen(name="favorites"))
        sm.add_widget(RecentlySavedScreen(name="recently_saved"))
        sm.add_widget(EditProfileScreen(name="edit_profile"))

        sm.add_widget(PreferencesScreen(name="my_preferences"))
        sm.add_widget(UserProfileScreen(name="user_profile"))

        sm.add_widget(AddWineScreen(name="add_wine"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(MenuTextInputScreen(name="menu_text_input"))
        sm.add_widget(MenuResultsScreen(name="menu_results"))
        sm.add_widget(WineDetailsScreen(name="wine_details"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(ThemeScreen(name="theme"))

        for screen in sm.screens:
            if hasattr(screen, 'apply_theme'):
                screen.apply_theme()

        return sm


if __name__ == "__main__":
    WineApp().run()
