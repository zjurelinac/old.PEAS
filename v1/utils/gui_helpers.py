from gi.repository import Gtk


def make_button(value, tooltip='', is_icon=False, action=None):
    button = Gtk.Button(value)
    button.set_tooltip_text(tooltip)
    if is_icon:
        button.set_name('icon_button')
    if action is not None:
        button.connect('clicked', action)
    return button
