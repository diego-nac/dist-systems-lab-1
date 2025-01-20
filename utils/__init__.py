from .LoggerConfig import LoggerConfig
from .configs import *

logger = LoggerConfig(PROJECT_NAME).get_logger()