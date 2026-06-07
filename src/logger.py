import logging
import os

logging.basicConfig(level=logging.INFO)

def setup_logger():
    """Sets up a central logger that outputs to both console and a log file."""
    
    # 1. Ensure the logs directory exists
    os.makedirs("logs", exist_ok=True)
    log_file_path = "logs/pipeline.log"
    
    # 2. Create the logger
    logger = logging.getLogger("CityPulseETL")
    logger.setLevel(logging.INFO) # Captures INFO, WARNING, ERROR, and CRITICAL
    
    # 3. Prevent duplicate logs if imported multiple times
    if not logger.handlers:
        # Create handlers (Console & File)
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(log_file_path, mode='a') # 'a' means append
        
        # 4. Define the exact format of the log message
        # e.g., "2026-06-07 19:55:41 - INFO - extract - Weather data fetched successfully."
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 5. Attach handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
    return logger