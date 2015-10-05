import os.path

class File:
    """A file wrapper which provides all the basic operations needed for a text editor.

    Provides saving, saving as, loading, reverting, getting file informations etc.
    """

    def __init__( self, file_name = None ):
        self.file_name = file_name if file_name is not None else 'Untitled'

    # Basic file actions

    def save( self ):
        pass

    def save_as( self ):
        pass

    def load( self, file_name ):
        pass

    def revert( self ):
        pass

    # File content operations

    def get_contents( self ):
        pass

    def set_contents( self ):
        pass

    # File informations

    def get_name( self ):
        return self.file_name

    def get_directory_path( self ):
        pass

    def get_absolute_path( self ):
        pass

    def get_base_name( self ):
        pass
