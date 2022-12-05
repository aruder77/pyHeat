from machine import Pin
from homie.node import HomieNode
from homie.property import HomieProperty
from homie.constants import ENUM

class HeatPumpControllerNode(HomieNode):

    pumpPin = Pin(2, Pin.OUT)

    def __init__(self):
        super().__init__(id="HeatPump", name="HeatPump", type="Controller")

        self.heatPumpProperty = HomieProperty(
            id="heatPump",
            name="heatPump",
            datatype=ENUM,
            format="on,off",
            settable=False,
            default="on",
        )
        self.add_property(self.heatPumpProperty)        


    def on(self):
        self.pumpPin.on()
        self.heatPumpProperty.value = "on"

    def off(self):
        self.pumpPin.off()
        self.heatPumpProperty.value = "off"
