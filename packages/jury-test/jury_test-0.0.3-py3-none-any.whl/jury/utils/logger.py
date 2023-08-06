import traceback
from rich.markup import escape
from rich.console import Console

logo_str = '''
 _____     _      ____       _____         _
|_   _|_ _(_)_ __|  _ \ _   |_   _|__  ___| |_
  | |/ _` | | '__| |_) | | | || |/ _ \/ __| __|
  | | (_| | | |  |  __/| |_| || |  __/\__ \ |_
  |_|\__,_|_|_|  |_|    \__, ||_|\___||___/\__|
                        |___/
'''

util_log_console = Console(highlight=False)


def log(string, end='\n'):
    log_gray(string, end)


def log_gray(string, end='\n'):
    util_log_console.print(escape(str(string)), end=end, style="grey58")


def log_white(string, end='\n'):
    util_log_console.print(escape(str(string)), end=end, style="white")


def log_green(string, end='\n'):
    util_log_console.print(escape(str(string)), end=end, style="green")


def log_yellow(string, end='\n'):
    util_log_console.print(escape(str(string)), end=end, style="yellow")


def log_blue(string, end='\n'):
    util_log_console.print(escape(str(string)), end=end, style="blue")


def log_red(string, end='\n'):
    util_log_console.print(escape(str(string)), end=end, style="red")


def log_exception( output, exe_info):
    error_type, error_message, error_traceback = exe_info
    print(output, end="")
    traceback.print_tb(error_traceback)
    log_red(f"{error_type.__name__} {error_message}")


if __name__ == '__main__':
    log_white("white")
    log_white("[white2]")
    log_yellow("yellow")
    log_green("green")
    log_blue("blue")
    log_red("red")
