import logging.config
import os

def setup_logging():
    """
    Sets up the logging configuration from the logging.conf file.
    This function locates the configuration file relative to this file's location,
    assuming it is in the project root.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    log_conf_path = os.path.join(project_root, "logging.conf")

    if os.path.exists(log_conf_path):
        logging.config.fileConfig(log_conf_path, disable_existing_loggers=False)
    else:
        logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
