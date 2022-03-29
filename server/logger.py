import datetime

class Logger:
    file_name_suffix = ".log"

    def __init__(self, file_name_prefix: str):
        self._file_name = file_name_prefix + "-" + self._get_timestamp_file_name() + self.file_name_suffix

    def append(self, text: str):
        timestamp_str = self._get_timestamp_log()
        log_text = "[" + timestamp_str + "] " + text
        print(log_text)
        self.save(log_text + "\n")

    def _get_timestamp_log(self):
        return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _get_timestamp_file_name(self):
        return str(datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%S"))

    def save(self, text: str):
        try:
            with open(self._file_name, "a") as log_file:
                log_file.write(text)
        except:
            print("There was an error trying to create a log file.")
