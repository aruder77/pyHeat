from machine import Pin

class HeatPumpController:

    pumpPin = Pin(15, Pin.OUT)


    def on(self):
        self.pumpPin.on()

    def off(self):
        self.pumpPin.off()
