from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.spacing = 10
        self.padding = 20

        title = Label(text="Wine Not?")
        self.add_widget(title)

        self.notes_input = TextInput(
            hint_text="Add a wine note here",
            multiline=False
        )
        self.add_widget(self.notes_input)

        self.wine_type_spinner = Spinner(
            text="Select Wine Type",
            values=("Red", "White")
        )
        self.add_widget(self.wine_type_spinner)

        upload_button = Button(text="Upload Wine Label")
        upload_button.bind(on_press=self.upload_wine)
        self.add_widget(upload_button)

        profile_button = Button(text="View Profile")
        profile_button.bind(on_press=self.view_profile)
        self.add_widget(profile_button)

        recommend_button = Button(text="Get Recommendations")
        recommend_button.bind(on_press=self.get_recommendations)
        self.add_widget(recommend_button)

        save_button = Button(text="Save Wine")
        save_button.bind(on_press=self.save_wine)
        self.add_widget(save_button)

        self.result_label = Label(text="Welcome to Wine Not")
        self.add_widget(self.result_label)

    def upload_wine(self, instance):
        self.result_label.text = "Upload button clicked"

    def view_profile(self, instance):
        self.result_label.text = "Profile button clicked"

    def get_recommendations(self, instance):
        wine_type = self.wine_type_spinner.text
        self.result_label.text = f"Recommendation requested for: {wine_type}"

    def save_wine(self, instance):
        note = self.notes_input.text
        wine_type = self.wine_type_spinner.text
        self.result_label.text = f"Saved wine note: {note} | Type: {wine_type}"


class WineApp(App):
    def build(self):
        return MainScreen()


if __name__ == "__main__":
    WineApp().run()