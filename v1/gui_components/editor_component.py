from gi.repository import Gtk, GtkSource

from utils.file import *
from utils.gui_helpers import *


class EditorComponent(Gtk.Grid):

    # Initialization

    def __init__(self):
        Gtk.Grid.__init__(self)

        self.file = File()

        self.buffer = GtkSource.Buffer()
        self.view = GtkSource.View.new_with_buffer(self.buffer)

        self.set_name('editor-component')
        self.init_header_bar()
        self.init_source_view()
        self.connect('key-press-event', self.keypress)

    def init_header_bar(self):
        self.header_bar = Gtk.HeaderBar()

        self.header_bar.set_name('view-bar')
        self.header_bar.set_title(self.file.get_name())
        self.header_bar.set_hexpand(True)
        self.header_bar.set_show_close_button(False)

        self.buttons = {}
        button_box = {}

        button_box['left'] = Gtk.Box()
        button_box['left'].set_homogeneous(False)
        button_box['left'].set_spacing(4)

        button_box['right'] = Gtk.Box()
        button_box['right'].set_homogeneous(False)
        button_box['right'].set_spacing(0)

        for name, value, tooltip, is_icon, action, box in [('open', 'Open', 'Open file', False, None, 'left'),
                                                           ('new', '\uE145', 'New file', True, None, 'left'),
                                                           ('save', '\uE161', 'Save file', True, None, 'left'),
                                                           ('assemble', '\uE869', 'Assemble file', True, None, 'left'),
                                                           ('save_as', '\uE161', 'Save file as', True, None, 'right'),
                                                           ('revert', '\uE863', 'Revert', True, None, 'right'),
                                                           ('undo', '\uE166', 'Undo', True, None, 'right'),
                                                           ('redo', '\uE15A', 'Redo', True, None, 'right')]:
            self.buttons[name] = make_button(value, tooltip, is_icon, action)
            button_box[box].pack_start(self.buttons[name], False, False, 0)

        self.header_bar.pack_start(button_box['left'])
        self.header_bar.pack_end(button_box['right'])

        self.attach(self.header_bar, 0, 0, 1, 1)

    def init_source_view(self):
        scrolled_window = Gtk.ScrolledWindow()

        scrolled_window.set_vexpand(True)
        scrolled_window.add(self.view)

        self.view.set_auto_indent(True)
        self.view.set_draw_spaces(GtkSource.DrawSpacesFlags.TAB |
                                  GtkSource.DrawSpacesFlags.SPACE |
                                  GtkSource.DrawSpacesFlags.LEADING |
                                  GtkSource.DrawSpacesFlags.TEXT)
        self.view.set_highlight_current_line(True)
        self.view.set_pixels_above_lines(4)
        self.view.set_pixels_below_lines(4)
        self.view.set_show_line_marks(True)
        self.view.set_show_line_numbers(True)
        self.view.set_show_right_margin(True)
        self.view.set_smart_home_end(True)
        self.view.set_tab_width(4)

        self.buffer.set_highlight_syntax(True)

        gutter = self.view.get_gutter(Gtk.TextWindowType.LEFT)
        gutter.set_padding(0, 0)
        line_renderer = gutter.get_renderer_at_pos(10, 0)
        line_renderer.set_alignment(1, 0.5)
        line_renderer.set_padding(4, 4)

        style_manager = GtkSource.StyleSchemeManager.get_default()
        style_manager.set_search_path(['./resources/schemes'])

        language_manager = GtkSource.LanguageManager.get_default()
        language_manager.set_search_path(
            ['./resources/languages'] + language_manager.get_search_path())

        self.buffer.set_style_scheme(style_manager.get_scheme('peas'))
        self.buffer.set_language(language_manager.get_language('frisc'))

        self.attach(scrolled_window, 0, 1, 1, 1)

    # Actions

    def open_file(self):
        pass

    def save_file(self):
        pass

    # Events

    def keypress(self, e, f):
        print(f.is_modifier, f.group, f.keyval, f.state)
