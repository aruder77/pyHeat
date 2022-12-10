from homie.property import HomieProperty
from homie.node import HomieNode
from homie.constants import FLOAT

class TargetFlowTemperatureCalculatorNode(HomieNode):

    slope = -0.3
    origin = 35.0
    maxFlowTemp = 40.0

    def __init__(self):
        super().__init__(id="TargetTempCalc", name="Target Temperature Calculator", type="Controller")

        self.slopeProperty = HomieProperty(
            id="slope",
            name="slope",
            settable=True,
            datatype=FLOAT,
            default=-0.3,
            on_message=self.slope_msg,
        )
        self.add_property(self.slopeProperty)

        self.originProperty = HomieProperty(
            id="origin",
            name="origin",
            settable=True,
            datatype=FLOAT,
            unit="°C",
            default=35.0,
            on_message=self.origin_msg,
        )
        self.add_property(self.originProperty)

        self.maxFlowTempProperty = HomieProperty(
            id="maxFlowTemp",
            name="maxFlowTemp",
            settable=True,
            datatype=FLOAT,
            unit="°C",
            default=40.0,
            on_message=self.slope_msg,
        )
        self.add_property(self.maxFlowTempProperty)

        self.targetTemperatureProperty = HomieProperty(
            id="targetFlowTemperature",
            name="targetFlowTemperature",
            datatype=FLOAT,
            unit="°C", 
            format="10.0",            
        )
        self.add_property(self.targetTemperatureProperty)        

    def slope_msg(self, topic, payload, retained):
        slope = float(payload)
        self.setSlope(slope)

    def origin_msg(self, topic, payload, retained):
        origin = float(payload)
        self.setOrigin(origin)

    def maxFlowTemp_msg(self, topic, payload, retained):
        maxFlowTemp = int(payload)
        if maxFlowTemp >= 20 and maxFlowTemp <= 50:
            self.setMaxFlowTemp(maxFlowTemp)           

    def setSlope(self, slope: float):
        if slope > -1 and slope < 1:
            self.slope = slope
            self.slopeProperty.value = slope

    def setOrigin(self, origin: float):
        if origin >= 0 and origin <= 50:
            self.origin = origin
            self.originProperty.value = origin

    def setMaxFlowTemp(self, maxFlowTemp: float):
        if maxFlowTemp >= 20 and maxFlowTemp <= 50:
            self.maxFlowTemp = maxFlowTemp
            self.maxFlowTempProperty.value = maxFlowTemp

    def calculateTargetFlowTemperature(self, outsideTemperature: float):
        targetFlowTemperature = min(self.origin + outsideTemperature * self.slope, self.maxFlowTemp)
        # self.targetTemperatureProperty.value = targetFlowTemperature
        self.targetTemperatureProperty.value = 37.0
        return targetFlowTemperature



