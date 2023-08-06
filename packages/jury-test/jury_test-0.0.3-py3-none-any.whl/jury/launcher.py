import os.path
import signal
import subprocess
from pathlib import Path

from .utils.logger import log_white
from jury.timer import Timer
from .jury import add_launcher


class Launcher:
    def __init__(self, args, work_dir):
        self.__args = args
        if not os.path.exists(work_dir):
            Path(work_dir).mkdir(parents=True, exist_ok=True)
        self.__stdout_file = open(work_dir + "/launcher_stdout", 'a')
        self.__stderr_file = open(work_dir + "/launcher_stderr", 'a')
        self.__process = subprocess.Popen(self.__args, stdout=self.__stdout_file,
                                          stderr=self.__stderr_file, cwd=work_dir,
                                          encoding="utf-8")
        self.__started = True

        add_launcher(self)

    def __del__(self):
        self.stop()

    def get_pid(self):
        return self.__process.pid

    def stop(self, force=False):
        if self.__started:
            self.__started = False
            self.__stdout_file.close()
            self.__stderr_file.close()
            log_white(f"waiting for process {self.__process.pid} to exit...")
            self.__stdout_file.close()
            self.__stderr_file.close()
            t = Timer()
            self.__process.send_signal(signal.SIGKILL if force else signal.SIGINT)
            self.__process.wait()
            log_white(f"process {self.__process.pid} exited ({t.elapsed_time()}s)")
