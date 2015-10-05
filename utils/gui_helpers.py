from gi.repository import Gtk, Gio

def create_button( name, icon_name, tooltip, action, has_icon = False, no_relief = False ):
    if has_icon:
        button = Gtk.Button.new_from_icon_name( icon_name, Gtk.IconSize.MENU )
    else:
        button = Gtk.Button( name.capitalize() )

    if tooltip is not None:
        button.set_tooltip_text( tooltip )

    if action is not None:
        button.connect( 'clicked', action )

    if no_relief:
        button.set_relief( Gtk.ReliefStyle.NONE )

    return button
