import yaml

from gi.repository import Gtk, Gdk

from assemblers.frisc_assembler import *
from gui_components.editor_component import *
from utils.gui_helpers import *


class PEAS(Gtk.Application):

    # Initialization

    def __init__(self):
        Gtk.Application.__init__(self, application_id="io.github.zjurelinac.PEAS")
        self.connect("activate", self.on_application_activate)
        self.editor = EditorComponent()
        self.simulator = Gtk.Label('Simulator')
        self.loader = Gtk.Label('Loader')

    def init_user_interface(self):
        self.window = Gtk.ApplicationWindow(title="PEAS", type=Gtk.WindowType.TOPLEVEL)
        self.window.set_name('application-window')
        self.window.set_default_size(1080, 700)
        self.window.set_icon_from_file('resources/app.svg')
        self.views = Gtk.Stack()
        self.views.add_titled(self.editor, 'editor', 'Editor')
        self.views.add_titled(self.simulator, 'simulator', 'Simulator')
        self.views.add_titled(self.loader, 'loader', 'Loader')
        self.init_header_bar()
        self.window.set_titlebar(self.header_bar)
        self.window.add(self.views)
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path('./resources/style.css')
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.add_window(self.window)
        self.window.show_all()

    def init_header_bar(self):
        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_show_close_button(True)
        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.views)
        self.header_bar.set_custom_title(switcher)
        menuButton = Gtk.Button('\uE8B8')
        menuButton.set_name('icon_button')
        self.header_bar.pack_end(menuButton)

    # Actions

    def assemble_source(self):
        pass

    def start_simulator(self):
        pass

    # Events

    def on_application_activate(self, data):
        self.init_user_interface()

    def on_quit(self):
        pass


if __name__ == '__main__':
    application = PEAS()
    application.run()
