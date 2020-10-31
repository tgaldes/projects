import logging

class Logger:
    def __init__(self):
        logging.basicConfig(filename='./example.log'
                            , level=logging.DEBUG
                            , datefmt='%Y%m%d %H:%M:%S'
                            , format='%(asctime)s [%(levelname)-8s] %(message)s')

    def li(self, s):
        logging.info(s)
        
