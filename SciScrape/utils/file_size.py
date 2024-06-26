#!/usr/bin/python3

import os, requests

class FileSize:

    @classmethod
    def format(cls, size, units=None):
        if units is None:
            units = [' bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
        
        return str(size) + units[0] if size < 1024 else cls.format(
            size >> 10, units[1:]
        )

    @classmethod
    def local_file(cls, file):
        file_size = os.stat(file)
        return cls.format(file_size.st_size)

    @classmethod
    def remote_file(cls, url):
        try:
            req_headers = requests.get(url)

            return cls.format(
                int(req_headers.headers["Content-Length"])
            )
        except:
            return None
