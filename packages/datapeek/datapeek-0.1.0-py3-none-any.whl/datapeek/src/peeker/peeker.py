import sys
import json

class Peek:
    message_color = {
        "ERROR": ';'.join([str(7), str(31), str(47)]),
        "WARN": ';'.join([str(7), str(33), str(40)]),
        "INFO": ';'.join([str(7), str(32), str(40)]),
        "GENERAL": ';'.join([str(7), str(34), str(47)])
    }
    message_types = [
        "ERROR",
        "WARN",
        "INFO",
        "GENERAL"
    ]
    data_types = [
        list,
        str,
        tuple,
        bool,
        memoryview,
        bytearray,
        bytes,
        frozenset,
        dict,
        range,
        complex,
        float,
        int
    ]

    def print_data(self, data):
        try:
            data_type = type(data)
            if data_type in self.data_types:
                if isinstance(data, memoryview):
                    return str(list(data))
                elif isinstance(data, bytearray):
                    return str(data.hex)
                elif isinstance(data, bytes):
                    x = bytes.fromhex(data)
                    return str(sys.stdout.buffer.write(x))
                elif isinstance(data, dict):
                    return json.dumps(data, indent=4, sort_keys=True)
                elif isinstance(data, range):
                    return str(list(data))
                else:
                    return str(data)
            else:
                return str(data)
        except TypeError as e:            
            print(f"\x1b[{self.message_color[3]}m INFO!: \x1b[0m: {data}\n {e}")

    def log_message(self, message_type, message, data=""):
        if data:
            DATA = "DATA:"
        else:
            DATA = ""
        try:
            message = str(message)
            if message_type in self.message_types:
                print(f"\x1b[{self.message_color[message_type]}m {message_type} \x1b[0m: {message}\n{DATA}\n{self.print_data(data)}")
            else:
                print(f"\x1b[{self.message_color[message_type[self.message_types[3]]]}m {message_type} \x1b[0m: {message}\n{DATA}\n{self.print_data(data)}")
        except TypeError as e:
            print(f"\x1b[{self.message_color[message_type[self.message_types[3]]]}m {message_type} \x1b[0m: {message}\n[{e}]")