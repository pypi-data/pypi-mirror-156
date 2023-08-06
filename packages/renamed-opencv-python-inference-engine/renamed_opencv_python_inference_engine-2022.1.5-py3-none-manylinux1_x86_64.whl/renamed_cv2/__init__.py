import importlib
from .cv2 import *

# wildcard import above does not import "private" variables like __version__
# this makes them available
globals().update(importlib.import_module('renamed_cv2.cv2').__dict__)
