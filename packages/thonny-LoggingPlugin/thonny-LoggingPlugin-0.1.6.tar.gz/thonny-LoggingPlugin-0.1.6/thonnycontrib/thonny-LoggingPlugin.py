from thonnycontrib.thonny_LoggingPlugin.configuration.globals import *
from thonnycontrib.thonny_LoggingPlugin import mainApp

from thonnycontrib.thonny_LoggingPlugin.configuration import configuration
from thonny.config import *


def load_plugin():
    """
    Load the plugin and and a command to configure it in thonny
    """
    logger = mainApp.EventLogger()
    configuration.init_options()
    WB.add_configuration_page("LoggingPlugin", "LoggingPlugin", configuration.plugin_configuration_page, 30)
    