COLOR_RED = "\033[31m"
COLOR_RED_BOLD = "\033[1;31m"
COLOR_GREEN = "\033[32m"
COLOR_BLUE = "\033[34m"
COLOR_PURPLE = "\033[35m"
COLOR_CYAN = "\033[36m"
COLOR_YELLOW = "\033[33m"
COLOR_GREY = "\033[37m"
COLOR_BLACK = "\033[30m"
COLOR_NORMAL = "\033[0m"

def colorized(string, color):
    """ Returns ``string`` in ``color`` """
    return color + string + COLOR_NORMAL

def get_tty_size():
    import subprocess
    p = subprocess.Popen(('stty', 'size'), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, close_fds=True)
    size = p.stdout.readlines()[0].strip().split(' ')
    return map(int, reversed(size))
