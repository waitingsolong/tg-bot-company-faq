import logging

def logged_step(step_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logging.info(f"{step_name}: start")
            try:
                result = func(*args, **kwargs)
                if not result:
                    logging.info(f"{step_name}: null result")
                    
                return result
            except Exception as e:
                logging.error(f"{step_name}: error")
                logging.exception(e)
                return None
            finally: 
                logging.info(f"{step_name}: end")
        return wrapper
    return decorator