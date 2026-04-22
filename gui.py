from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.camera import Camera
from kivy.lang import Builder
import csv
import os
import time
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
        self.load_wines()

    def load_wines(self):
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
                            size_hint=(0.3, 1)
                        )
                        wine_card.add_widget(img)
                    
                    # Wine info
                    info_layout = BoxLayout(
                        orientation='horizontal',
                        size_hint=(0.7, 1),
                        spacing=5
                    )
                    
                    wine_name = Label(
                        text=row.get('Wine Name', 'Unknown'),
                        font_size=14,
                        size_hint_y=None,
                        height=65,
                        text_size=(self.width * 0.65, None),
                        markup=True
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
                    
                    most_recent = Label(
                        text=f"Most Recent: {row.get('Most Recent', 'N/A')}",
                        font_size=12,
                        size_hint_y=None,
                        height=25
                    )
                    info_layout.add_widget(most_recent)
                    
                    wine_card.add_widget(info_layout)
                    self.wine_container.add_widget(wine_card)
        except Exception as e:
            error_label = Label(text=f"Error loading wines: {str(e)}", font_size=16)
            self.wine_container.add_widget(error_label)


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
        self.result_label.text = "Showing favorite wines..."

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
        self.result_label.text = "Opening manual wine entry..."

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
        sm.add_widget(AddWineScreen(name="add_wine"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(RecommendationScreen(name="recommendation"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if __name__ == "__main__":
    WineApp().run()
