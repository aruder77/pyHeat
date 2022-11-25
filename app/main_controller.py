from esp_micro.esp_micro_controller import EspMicroController
from pyheat_device import PyHeatDevice


class MainController(EspMicroController):
    def __init__(self):
        super().__init__()

    def createHomieDevice(self, settings):
        return PyHeatDevice(settings)

    def getDeviceName(self):
        return 'pyHeat'

    def getDeviceID(self):
        return 'pyHeat'
