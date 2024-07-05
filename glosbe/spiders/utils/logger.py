import os
import logging

LOGS_DIR = 'logs'  # Nama folder untuk menyimpan log

def setup_logger():
    """Set up multiple loggers for different types of messages."""
    
    # Membuat folder logs jika belum ada
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    
    # Logger for error messages
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)
    error_handler = logging.FileHandler(os.path.join(LOGS_DIR, 'error.log'))
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(error_handler)

    # Logger for info messages
    info_logger = logging.getLogger('info_logger')
    info_logger.setLevel(logging.INFO)
    info_handler = logging.FileHandler(os.path.join(LOGS_DIR, 'info.log'))
    info_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    info_logger.addHandler(info_handler)

    # Logger for warning messages
    warning_logger = logging.getLogger('warning_logger')
    warning_logger.setLevel(logging.WARNING)
    warning_handler = logging.FileHandler(os.path.join(LOGS_DIR, 'warning.log'))
    warning_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    warning_logger.addHandler(warning_handler)

def log_info(message):
    """Log an informational message."""
    info_logger = logging.getLogger('info_logger')
    info_logger.info(message)

def log_error(message):
    """Log an error message."""
    error_logger = logging.getLogger('error_logger')
    error_logger.error(message)

def log_warning(message):
    """Log a warning message."""
    warning_logger = logging.getLogger('warning_logger')
    warning_logger.warning(message)
