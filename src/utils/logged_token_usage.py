import functools
import logging


def log_token_usage(extra_text: str):
    """
    Only for OpenAIClient
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                result = await func(self, *args, **kwargs)
            except Exception as e:
                logging.error(f"{extra_text}: error")
                logging.exception(e)
            
            input_tokens =  self._OpenAIClient__delta_input_tokens
            output_tokens = self._OpenAIClient__delta_output_tokens
            
            self._OpenAIClient__input_tokens  += input_tokens
            self._OpenAIClient__output_tokens += output_tokens
            self._OpenAIClient__delta_session_input_tokens  += input_tokens
            self._OpenAIClient__delta_session_output_tokens += output_tokens
            self._OpenAIClient__delta_input_tokens = 0 
            self._OpenAIClient__delta_output_tokens = 0

            if extra_text:
                logging.info(extra_text)
                
            logging.info(f"Input tokens: {input_tokens} (total {self._OpenAIClient__input_tokens})")
            logging.info(f"Output tokens: {output_tokens} (total {self._OpenAIClient__output_tokens})")
            
            return result
        return wrapper
    return decorator
