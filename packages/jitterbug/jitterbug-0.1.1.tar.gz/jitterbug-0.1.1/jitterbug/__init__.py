import pkg_resources
__version__ = pkg_resources.get_distribution('jitterbug').version

from jitterbug.commandline import main, run
from jitterbug.utils import notmutate
