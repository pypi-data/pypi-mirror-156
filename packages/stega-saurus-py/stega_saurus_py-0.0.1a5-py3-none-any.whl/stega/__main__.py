from stega import __app_name__
from stega.cli import command


def main():
    command.app(prog_name=__app_name__)


if __name__ == '__main__':
    main()
