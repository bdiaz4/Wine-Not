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
import os
import time
import csv
import threading
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
            timestr = time.strftime("%Y%m%d_%H%M%S")
            wine_images_dir = os.path.join(os.path.dirname(__file__), 'wineImages')
            os.makedirs(wine_images_dir, exist_ok=True)
            filepath = os.path.join(wine_images_dir, f"wine_{timestr}.png")  # Changed to png since export_to_png
            self.camera.export_to_png(filepath)
            print(f"Captured: {filepath}")
            # Return to add wine screen
            app = App.get_running_app()
            app.root.current = "add_wine"
        else:
            print("No camera available for capture")

class BaseScreen(Screen):
    def go_home(self, instance):
        self.manager.current = "home"

    def create_header(self):
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.2), spacing=5)

        title_button = Button(
            text="Wine Not?",
            font_size=28,
            size_hint=(1, 0.65)
        )
        title_button.bind(on_press=self.go_home)

        subtitle = Label(
            text="Tap title to return home",
            font_size=14,
            size_hint=(1, 0.35)
        )

        header.add_widget(title_button)
        header.add_widget(subtitle)
        return header


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=15
        )

        title = Label(
            text="Wine Not?",
            font_size=30,
            size_hint=(1, 0.2)
        )
        layout.add_widget(title)

        subtitle = Label(
            text="Your personal wine assistant",
            font_size=16,
            size_hint=(1, 0.1)
        )
        layout.add_widget(subtitle)

        profile_button = Button(
            text="My Profile",
            font_size=20,
            size_hint=(1, 0.17)
        )
        profile_button.bind(on_press=self.go_profile)
        layout.add_widget(profile_button)

        add_wine_button = Button(
            text="Add Wine",
            font_size=20,
            size_hint=(1, 0.17)
        )
        add_wine_button.bind(on_press=self.go_add_wine)
        layout.add_widget(add_wine_button)

        recommend_button = Button(
            text="Get Recommendation",
            font_size=20,
            size_hint=(1, 0.17)
        )
        recommend_button.bind(on_press=self.go_recommendation)
        layout.add_widget(recommend_button)

        settings_button = Button(
            text="Settings",
            font_size=20,
            size_hint=(1, 0.17)
        )
        settings_button.bind(on_press=self.go_settings)
        layout.add_widget(settings_button)

        self.add_widget(layout)

    def go_profile(self, instance):
        self.manager.current = "profile"

    def go_add_wine(self, instance):
        self.manager.current = "add_wine"

    def go_recommendation(self, instance):
        self.manager.current = "recommendation"

    def go_settings(self, instance):
        self.manager.current = "settings"


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
                        orientation='horizontal',
                        size_hint=(1, 1),
                        spacing=5,
                        padding=(15, 5, 5, 5)
                    )
                    
                    wine_name = Label(
                        text=row.get('Wine Name', 'Unknown'),
                        font_size=14,
                        size_hint_y=None,
                        height=65,
                        text_size=(240, None),
                        markup=True,
                        halign='left',
                        valign='top'
                    )
                    info_layout.add_widget(wine_name)
                    
                    count = Label(
                        text=f"Count: {row.get('Count', 'N/A')}",
                        font_size=12,
                        size_hint_y=None,
                        height=25
                    )
                    info_layout.add_widget(count)
                    
                    date_added = Label(
                        text=f"Date Added: {row.get('Date Added', 'N/A')}",
                        font_size=12,
                        size_hint_y=None,
                        height=25
                    )
                    info_layout.add_widget(date_added)
                    
                    favorite = row.get('Favorite', 'False') == 'True'
                    favorite_button = ToggleButton(
                        text="Favorite" if favorite else "Save to Favorites",
                        font_size=20,
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
                        orientation='horizontal',
                        size_hint=(1, 1),
                        spacing=5,
                        padding=(15, 5, 5, 5)
                    )
                    
                    wine_name = Label(
                        text=row.get('Wine Name', 'Unknown'),
                        font_size=14,
                        size_hint_y=None,
                        height=65,
                        text_size=(240, None),
                        markup=True,
                        halign='left',
                        valign='top'
                    )
                    info_layout.add_widget(wine_name)
                    
                    count = Label(
                        text=f"Count: {row.get('Count', 'N/A')}",
                        font_size=12,
                        size_hint_y=None,
                        height=25
                    )
                    info_layout.add_widget(count)
                    
                    date_added = Label(
                        text=f"Date Added: {row.get('Date Added', 'N/A')}",
                        font_size=12,
                        size_hint_y=None,
                        height=25
                    )
                    info_layout.add_widget(date_added)
                    
                    favorite = True  # since it's favorites screen
                    favorite_button = ToggleButton(
                        text="Favorite" if favorite else "Save to Favorites",
                        font_size=20,
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
            text="Edit Profile",
            font_size=18,
            size_hint=(1, 0.14)
        )
        edit_button.bind(on_press=self.edit_profile)
        layout.add_widget(edit_button)

        self.result_label = Label(
            text="Profile options will appear here",
            font_size=16,
            size_hint=(1, 0.2)
        )
        layout.add_widget(self.result_label)

        self.add_widget(layout)

    def show_saved_wines(self, instance):
        self.manager.current = "saved_wines"

    def show_favorites(self, instance):
        self.manager.current = "favorites"

    def show_recent(self, instance):
        self.result_label.text = "Showing recently saved wines..."

    def edit_profile(self, instance):
        self.result_label.text = "Opening edit profile..."


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

    def upload_picture(self, instance):
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

        grid = GridLayout(cols=3, spacing=10, size_hint=(1, 0.6))

        self.selected_label = Label(text="Select an image", font_size=16, size_hint=(1, 0.1))

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
                    grid.add_widget(button)

        layout.add_widget(grid)
        layout.add_widget(self.selected_label)

        self.add_widget(layout)

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


class RecommendationScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(
            orientation='vertical',
            padding=20,
            spacing=12
        )

        layout.add_widget(self.create_header())

        section_label = Label(
            text="Get Recommendation",
            font_size=22,
            size_hint=(1, 0.14)
        )
        layout.add_widget(section_label)

        upload_menu_button = Button(
            text="Upload Menu",
            font_size=18,
            size_hint=(1, 0.18)
        )
        upload_menu_button.bind(on_press=self.upload_menu)
        layout.add_widget(upload_menu_button)

        chat_button = Button(
            text="Chat Assistant",
            font_size=18,
            size_hint=(1, 0.18)
        )
        chat_button.bind(on_press=self.chat_assistant)
        layout.add_widget(chat_button)

        self.result_label = Label(
            text="Choose how to get recommendations",
            font_size=16,
            size_hint=(1, 0.25)
        )
        layout.add_widget(self.result_label)

        self.add_widget(layout)

    def upload_menu(self, instance):
        self.result_label.text = "Opening menu upload..."

    def chat_assistant(self, instance):
        self.result_label.text = "Opening chat assistant..."


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

        notifications_button = Button(
            text="Notifications",
            font_size=18,
            size_hint=(1, 0.18)
        )
        notifications_button.bind(on_press=self.notifications)
        layout.add_widget(notifications_button)

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

    def notifications(self, instance):
        self.result_label.text = "Notifications settings coming soon..."

    def theme(self, instance):
        self.result_label.text = "Theme settings coming soon..."


class WineApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(SavedWinesScreen(name="saved_wines"))
        sm.add_widget(FavoritesScreen(name="favorites"))
        sm.add_widget(AddWineScreen(name="add_wine"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(RecommendationScreen(name="recommendation"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if __name__ == "__main__":
    WineApp().run()
