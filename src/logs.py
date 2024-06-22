import logging
from config import DEBUG


def init_logs():
    FORMAT = "%(levelname)s [%(filename)s->%(funcName)s():%(lineno)s] %(message)s"
    LEVEL = logging.INFO
    HANDLERS=[logging.StreamHandler()]
    if DEBUG:
        HANDLERS.append(logging.FileHandler("log.log", mode='w'))
        
    logging.basicConfig(level=LEVEL,
                        format=FORMAT, 
                        handlers=HANDLERS,
    )
    