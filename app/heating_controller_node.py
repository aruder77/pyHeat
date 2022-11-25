from homie.property import HomieProperty
from homie.node import HomieNode
from flow_temperature_regulator_node import FlowTemperatureRegulatorNode
from target_flow_temperature_calculator_node import TargetFlowTemperatureCalculatorNode
from valve_controller_node import ValveControllerNode
from temperature_reader import TemperatureReader
from heat_pump_controller import HeatPumpController

class HeatingControllerNode(HomieNode):

    flowTemperatureRegulator: FlowTemperatureRegulatorNode
    targetFlowTemperatureCalculator: TargetFlowTemperatureCalculatorNode
    valveController: ValveControllerNode
    temperatureReader: TemperatureReader
    heatPumpController: HeatPumpController

    def __init__(self, flowTemperatureRegulator, targetFlowTemperatureCalculator, valveController):
        super.__init__(id="HeatingController", name="Heating Controller", type="Controller")

        self.flowTemperatureRegulator = flowTemperatureRegulator
        self.targetFlowTemperatureCalculator = targetFlowTemperatureCalculator
        self.valveController = valveController

        self.temperatureReader = TemperatureReader()
        self.heatPumpController = HeatPumpController()

        self.numberOfOpenValvesProperty = HomieProperty(
            id="numberOfOpenValves",
            name="numberOfOpenValves",
            datatype=INTEGER,
            default=0,
        )
        self.add_property(self.numberOfOpenValvesProperty)

        # always on for now
        self.heatPumpController.on()

        self.everySecondTimer = Timer(-1)
        self.everySecondTimer.init(period=10000, mode=Timer.PERIODIC, callback=self.every10Seconds())


    def every10Seconds(self):
        flowTemperature = self.temperatureReader.getFlowTemperature()
        outsideTemperature = self.temperatureReader.getOutsideTemperature()
        returnTemperature = self.temperatureReader.getReturnTemperature()

        targetFlowTemperature = self.targetFlowTemperatureCalculator.calculateTargetFlowTemperature(outsideTemperature)
        valveTarget = self.flowTemperatureRegulator.calculateValveTarget(flowTemperature, targetFlowTemperature)
        valveCurrent = self.valveController.valveCurrent
        self.valveController.setTarget(valveTarget)

        print("Ventil aktuell: %d, Ziel: %d" % (valveCurrent, valveTarget))





    

    
