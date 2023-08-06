from thonny import THONNY_USER_DIR, get_workbench

#Default config
DEFAULT_PATH = THONNY_USER_DIR+"/LoggingPlugin/"
DEFAULT_SERVER = 'http://127.0.0.1:8000'
DEFAULT_STORE = True
DEFAULT_LOG_IN_CONSOLE = True
VERSION = "0.1.6"

#Dict of options name and default value
OPTIONS = {
    "local_path" : DEFAULT_PATH,
    "server_address" : DEFAULT_SERVER,
    "store_logs" : DEFAULT_STORE,
    "log_in_console" : DEFAULT_LOG_IN_CONSOLE,
}

#Get the thonny workbench object
WB = get_workbench()