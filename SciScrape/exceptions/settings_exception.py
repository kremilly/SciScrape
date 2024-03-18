#!/usr/bin/python3

import traceback

class SettingsException(Exception):
    
    def __init__(self, message):
        self.message = message
        super().__init__(message)
        traceback.print_exc()
