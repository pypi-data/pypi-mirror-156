import argparse
import importlib
import os
import shutil
import sys

from .utils.hidden_prints import HiddenPrints
from .utils.logger import log_exception, log_green, log_gray, log_red
from jury.timer import Timer

case_dir = "tmp"
launcher_list = []


class Jury:
    def __init__(self, cases: list[str], tmp_dir="tmp"):
        self.args = self.__parse_args()
        self.__hidden_output = not self.args.verbose
        self.__cases = cases
        self.__tmp_dir = tmp_dir
        self.__check_cases()
        if os.path.exists(self.__tmp_dir):
            shutil.rmtree(self.__tmp_dir)

    def run(self):
        global case_dir
        total = len(self.__cases)
        if self.args.single:
            total = 1
        inx = 1
        for case in self.__cases:
            if self.args.single and case != self.args.single:
                continue
            timer = Timer()
            params = importlib.import_module(case.replace("/", "."))
            case_dir = f"{self.__tmp_dir}/{case.replace('/', '.')}"
            with HiddenPrints(activated=self.__hidden_output) as hp:
                # noinspection PyBroadException
                try:
                    params.main()
                except Exception:
                    HiddenPrints.recover_stdout()
                    for item in launcher_list:
                        item.stop()

                    log_gray("[", end='')
                    log_red("✗", end="")
                    log_gray(f"] {case} ({timer.elapsed_time()} seconds)")
                    log_exception(hp.get_output(), sys.exc_info())
                    exit(1)

                for item in launcher_list:
                    item.stop()

            log_gray(f"[", end='')
            log_green("✓", end="")
            log_gray(f" {inx}/{total}] {case} ({timer.elapsed_time()} seconds)")
            inx += 1

    def __check_cases(self):
        for case in self.__cases:
            params = importlib.import_module(case.replace("/", "."))

            if "main" not in params.__dir__():
                raise Exception(f"case {case} not has main() method.")

    @staticmethod
    def __parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('--single', type=str, help='test case name, such as: cases/example')
        parser.add_argument('--verbose', action='store_true', default=False,
                            help='show all the log')
        args = parser.parse_args()
        return args


def get_case_dir():
    return case_dir


def add_launcher(item):
    global launcher_list
    launcher_list.append(item)
