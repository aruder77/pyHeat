import sys
import time, machine, network, gc
import os

sys.path.append('/app')
sys.path.append('/app/lib')

from main_controller import MainController

def main():
    # start application controller
    controller = MainController()
    controller.run()


if __name__ == "__main__":
    main()
