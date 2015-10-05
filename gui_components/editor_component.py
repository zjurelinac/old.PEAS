from gi.repository import Gtk, Gdk, GtkSource

from utils.file import *
from utils.gui_helpers import *

class EditorComponent( Gtk.Grid ):

    # Initialization

    def __init__( self ):
        Gtk.Grid.__init__( self )

        self.file = File()

        self.buffer = GtkSource.Buffer()
        self.view = GtkSource.View.new_with_buffer( self.buffer )

        self.init_user_interface()

    def init_user_interface( self ):
        self.set_name( 'editor-component' )
        self.init_header_bar()
        self.init_source_view()

    def init_header_bar( self ):
        self.header_bar = Gtk.HeaderBar()

        self.header_bar.set_name( 'view-bar' )
        self.header_bar.set_title( self.file.get_name() )
        self.header_bar.set_hexpand( True )
        self.header_bar.set_show_close_button( False )

        left_buttons_data = [
            ( 'open', None, 'Open file', None, False ),
            ( 'new', 'document-new', 'New file', None, False ),
            ( 'save', 'document-save-symbolic', 'Save file', None, False ),
            ( 'assemble', 'system-run-symbolic', 'Assemble', None, False )
        ]

        right_buttons_data = [
            ( 'save as', 'filesaveas', 'Save file as', None, True ),
            ( 'revert', 'gtk-refresh', 'Revert file', None, True ),
            ( None, None, None, None, None ),
            ( 'copy', 'edit-copy-symbolic', 'Copy', None, True ),
            ( 'cut', 'edit-cut-symbolic', 'Cut', None, True ),
            ( 'paste', 'edit-paste-symbolic', 'Paste', None, True ),
            ( None, None, None, None, None ),
            ( 'undo', 'edit-undo-symbolic', 'Undo', None, True ),
            ( 'redo', 'edit-redo-symbolic', 'Redo', None, True ),
        ]

        self.buttons = {}

        left_button_box = Gtk.Box()
        left_button_box.set_homogeneous( False )
        left_button_box.set_spacing( 4 )

        right_button_box = Gtk.Box()
        right_button_box.set_homogeneous( False )
        right_button_box.set_spacing( 0 )

        for name, icon, tooltip, action, relief in left_buttons_data:
            self.buttons[ name ] = create_button( name, icon, tooltip, action, icon is not None, relief )
            left_button_box.pack_start( self.buttons[ name ], False, False, 0 )

        for name, icon, tooltip, action, relief in right_buttons_data:
            if name is not None:
                self.buttons[ name ] = create_button( name, icon, tooltip, action, icon is not None, relief )
                right_button_box.pack_start( self.buttons[ name ], False, False, 0 )
            else:
                right_button_box.pack_start( Gtk.SeparatorToolItem(), False, False, 0 )

        self.header_bar.pack_start( left_button_box )
        self.header_bar.pack_end( right_button_box )

        self.attach( self.header_bar, 0, 0, 1, 1 )

    def init_source_view( self ):
        scrolled_window = Gtk.ScrolledWindow()

        scrolled_window.set_vexpand( True )
        scrolled_window.add( self.view )

        self.view.set_auto_indent( True )
        self.view.set_draw_spaces( GtkSource.DrawSpacesFlags.TAB | GtkSource.DrawSpacesFlags.SPACE | GtkSource.DrawSpacesFlags.LEADING | GtkSource.DrawSpacesFlags.TEXT )
        self.view.set_highlight_current_line( True )
        self.view.set_pixels_above_lines( 4 )
        self.view.set_pixels_below_lines( 4 )
        self.view.set_show_line_marks( True )
        self.view.set_show_line_numbers( True )
        self.view.set_show_right_margin( True )
        self.view.set_smart_home_end( True )
        self.view.set_tab_width( 4 )

        self.buffer.set_highlight_syntax( True )

        gutter = self.view.get_gutter( Gtk.TextWindowType.LEFT )
        gutter.set_padding( 0, 0 )
        line_renderer = gutter.get_renderer_at_pos( 10, 0 )
        line_renderer.set_alignment( 1, 0.5 )
        line_renderer.set_padding( 4, 4 )

        style_manager = GtkSource.StyleSchemeManager.get_default()
        style_manager.set_search_path( [ './resources/schemes' ] )

        language_manager = GtkSource.LanguageManager.get_default()
        language_manager.set_search_path( [ './resources/languages' ] + language_manager.get_search_path() )

        self.buffer.set_style_scheme( style_manager.get_scheme( 'peas' ) )
        self.buffer.set_language( language_manager.get_language( 'frisc' ) )

        self.attach( scrolled_window, 0, 1, 1, 1 )

    # Actions


    # Events
