import framework.NewLogger as NewLogger
import pathlib
# global config
NewLogger.global_log_level = 'DEBUG'
parent_path = str(pathlib.Path(__file__).parent.absolute())
