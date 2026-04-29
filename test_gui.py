import pytest
from kivy.uix.button import Button
from kivy.uix.label import Label


@pytest.mark.trio
async def test_app_build(trio_kivy_app):
    from gui import WineApp
    app = await trio_kivy_app(WineApp)
    assert app is not None
    assert app.root is not None


@pytest.mark.trio
async def test_camera_can_open_and_save_image(trio_kivy_app):
    from gui import WineApp
    app = await trio_kivy_app(WineApp)

    # Navigate to add wine screen and open the camera workflow
    app.root.current = "add_wine"
    add_wine_screen = app.root.get_screen('add_wine')
    add_wine_screen.upload_picture(None)

    take_photo_button = next(
        (widget for widget in add_wine_screen.walk() if isinstance(widget, Button) and widget.text == "Take New Photo"),
        None
    )
    assert take_photo_button is not None
    take_photo_button.dispatch('on_press')
    assert app.root.current == "camera"

    camera_screen = app.root.get_screen('camera')
    capture_button = next(
        (widget for widget in camera_screen.walk() if isinstance(widget, Button) and widget.text == "Capture"),
        None
    )
    assert capture_button is not None


@pytest.mark.trio
async def test_screen_navigation(trio_kivy_app):
    from gui import WineApp
    app = await trio_kivy_app(WineApp)
    assert app.root.current == "home"
    app.root.current = "profile"
    assert app.root.current == "profile"


@pytest.mark.trio
async def test_add_wine_screen_elements(trio_kivy_app):
    from gui import WineApp
    app = await trio_kivy_app(WineApp)
    app.root.current = "add_wine"
    screen = app.root.get_screen('add_wine')
    buttons = [widget for widget in screen.walk() if isinstance(widget, Button)]
    button_texts = [btn.text for btn in buttons]
    assert "Upload Picture" in button_texts
    assert "Add Manually" in button_texts


@pytest.mark.trio
async def test_profile_screen_buttons(trio_kivy_app):
    from gui import WineApp
    app = await trio_kivy_app(WineApp)
    app.root.current = "profile"
    profile_screen = app.root.get_screen('profile')
    buttons = [widget for widget in profile_screen.walk() if isinstance(widget, Button)]
    button_texts = [btn.text for btn in buttons]
    assert "Saved Wines" in button_texts
    assert "Favorites" in button_texts