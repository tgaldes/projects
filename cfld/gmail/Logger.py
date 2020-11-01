import logging

# TODO: redirect to console as well
class Logger:
    def __init__(self):
        logging.basicConfig(filename='./example.log'
                            , level=logging.INFO
                            , datefmt='%Y%m%d %H:%M:%S'
                            , format='%(asctime)s [%(levelname)-8s] %(message)s')

    def li(self, s):
        logging.info(s)

    def lw(self, s):
        logging.warn(s)
        
