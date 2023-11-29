import datetime
import logging
import os
from logging.handlers import TimedRotatingFileHandler

current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_file = f"loader_{current_date}"
log_dir = "logs"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logger = logging.getLogger("loader")
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler(
    f"{log_dir}/{log_file}.log", when="midnight", interval=1, backupCount=5
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
