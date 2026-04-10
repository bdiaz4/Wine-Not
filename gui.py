from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


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
        self.result_label.text = "Showing saved wines..."

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
        self.result_label.text = "Opening wine label upload..."

    def add_manually(self, instance):
        self.result_label.text = "Opening manual wine entry..."


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
        sm.add_widget(AddWineScreen(name="add_wine"))
        sm.add_widget(RecommendationScreen(name="recommendation"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if __name__ == "__main__":
    WineApp().run()