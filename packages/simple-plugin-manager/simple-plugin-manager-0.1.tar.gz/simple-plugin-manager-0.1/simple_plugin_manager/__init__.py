from .plugin_manager import PluginManager  # NOQA
from .loading import Loader, load  # NOQA

VERSION = (0, 1)
VERSION_STRING = '.'.join(str(i) for i in VERSION)
