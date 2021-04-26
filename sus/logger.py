import logging as log

class Logger(log.Logger):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    def info(self, msg):
        log.info(msg)
    def exception(self, msg):
        log.exception(msg)