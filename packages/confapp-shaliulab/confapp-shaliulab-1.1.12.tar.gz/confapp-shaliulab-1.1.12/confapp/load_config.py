# TODO
import argparse
# For some fucking reason, confapp is not loading from the local_settings.py
def load_config():
    with open("local_settings.py", "r") as filehandle:
        data = filehandle.readlines()
        data = [e.strip("\n") for e in data]

    config = {}
    for line in data:
        try:
            key, value = line.split("=")
            value=value.lstrip('"').rstrip('"').lstrip("'").rstrip("'")
            if value =="False":
                value=False
            elif value=="True":
                value=True

            else:
                try:
                    value = float(value)
                except ValueError:
                    pass

            config[key] = value

        except:
            pass

    config = argparse.Namespace(**config)

    return config
