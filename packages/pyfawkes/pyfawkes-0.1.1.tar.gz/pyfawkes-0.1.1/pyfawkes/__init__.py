import pkg_resources
__version__ = pkg_resources.get_distribution('pyfawkes').version

from pyfawkes.commandline import main, run
from pyfawkes.utils import notmutate
