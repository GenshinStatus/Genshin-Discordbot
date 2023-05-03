import sys
import traceback


class LogException(Exception):
    def __init__(self, e):

        exc_type, exc_obj, exc_tb = sys.exc_info()
        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        # print(f"file:{str(fname)} in {str( exc_tb.tb_lineno )}")
        # print(e)
        print(traceback.print_tb(exc_tb))
