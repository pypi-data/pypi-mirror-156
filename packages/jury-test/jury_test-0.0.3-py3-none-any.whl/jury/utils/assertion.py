import time
import types
from .logger import *


def ASSERT_EQ_TIMEOUT(v1, v2=None, timeout=10, interval=0.5):
    if v2 is None:
        time_start = time.time()
        if isinstance(v1, types.LambdaType):
            while True:
                value = v1()
                if value:
                    return
                if time.time() - time_start > timeout:
                    assert AssertionError("Assert timeout")
                time.sleep(interval)
        else:
            assert v1()
    else:
        time_start = time.time()
        while True:
            value1 = v1() if isinstance(v1, types.LambdaType) else v1
            value2 = v2() if isinstance(v2, types.LambdaType) else v2
            if value1 == value2:
                return
            else:
                if time.time() - time_start > timeout:
                    error = f"Assert timeout, [{value1}] != [{value2}]"
                    log_red(error)
                    raise AssertionError(error)
            time.sleep(interval)


def ASSERT_TRUE(v):
    if not v:
        log_red("\n----------------------------------------------")
        log_red(f"Assert Failed: expect True, but is {v}")
        log_red("----------------------------------------------\n")
        raise AssertionError(f"[{v}] != [True]")


def ASSERT_EQ(v0, v1):
    if v0 != v1:
        log_red("\n----------------------------------------------")
        log_red(f"Assert Failed: expect {v1}, but is {v0}")
        log_red("----------------------------------------------\n")
        raise AssertionError(f"[{v0}] != [{v1}]")
