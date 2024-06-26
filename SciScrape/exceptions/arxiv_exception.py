#!/usr/bin/python3

import traceback

class ArxivException(Exception):
    
    def __init__(cls, message):
        cls.message = message
        super().__init__(message)
        traceback.print_exc()
