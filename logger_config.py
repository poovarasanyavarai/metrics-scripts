"""
Logging configuration for the chatbot metrics application
"""
import logging
import os
from datetime import datetime


def setup_logger(name='chatbot_metrics', log_level=logging.INFO):
    """
    Setup logger with console and file handlers
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler - create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = f'logs/chatbot_metrics_{timestamp}.log'

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name=None):
    """Get logger instance"""
    return logging.getLogger(name or 'chatbot_metrics')