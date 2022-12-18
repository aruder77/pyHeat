from homie.property import HomieProperty
from homie.node import HomieNode
from homie.constants import INTEGER
from machine import Timer
from flow_temperature_regulator_node import FlowTemperatureRegulatorNode
from target_flow_temperature_calculator_node import TargetFlowTemperatureCalculatorNode
from valve_controller_node import ValveControllerNode
from temperature_reader_node import TemperatureReaderNode
from heat_pump_controller_node import HeatPumpControllerNode

class HeatingControllerNode(HomieNode):

    flowTemperatureRegulator: FlowTemperatureRegulatorNode
    targetFlowTemperatureCalculator: TargetFlowTemperatureCalculatorNode
    valveController: ValveControllerNode
    temperatureReader: TemperatureReaderNode
    heatPumpController: HeatPumpControllerNode


    def __init__(self, temperatureReader, flowTemperatureRegulator, targetFlowTemperatureCalculator, valveController, heatPumpController):
        super().__init__(id="Floors", name="Floors", type="Controller")

        self.temperatureReader = temperatureReader
        self.flowTemperatureRegulator = flowTemperatureRegulator
        self.targetFlowTemperatureCalculator = targetFlowTemperatureCalculator
        self.valveController = valveController
        self.heatPumpController = heatPumpController

        self.temperatureSensorsInitialized = False

        self.numberOfOpenValves = 0
        self.numberOfOpenValvesProperty = HomieProperty(
            id="numberOfOpenValves",
            name="numberOfOpenValves",
            datatype=INTEGER,
            settable=True,
            default=0,
            on_message=self.numberOfOpenValvesMessage
        )
        self.add_property(self.numberOfOpenValvesProperty)

        self.heatPumpController.off()

        self.every10SecondsTimer = Timer(-1)
        self.every10SecondsTimer.init(period=10000, mode=Timer.PERIODIC, callback=lambda t:self.every10Seconds())

        self.temperatureInitializationTimer = Timer(-1)
        self.temperatureInitializationTimer.init(period=600000, mode=Timer.ONE_SHOT, callback=lambda t:self.finishTemperatureSensorInitialization())

    def finishTemperatureSensorInitialization(self):
        self.temperatureSensorsInitialized = True


    def every10Seconds(self):
        flowTemperature = self.temperatureReader.getFlowTemperature()
        outsideTemperature = self.temperatureReader.getOutsideTemperature()
        self.temperatureReader.getReturnTemperature()

        targetFlowTemperature = self.targetFlowTemperatureCalculator.calculateTargetFlowTemperature(outsideTemperature)
        if (self.numberOfOpenValves == 0):
            print("all floor valves closed, valveTarget=0")
            valveTarget = 0.0
        else:
            valveTarget = self.flowTemperatureRegulator.calculateValveTarget(flowTemperature, targetFlowTemperature)
        valveCurrent = self.valveController.valveCurrent
        if (self.temperatureSensorsInitialized == True):
            self.valveController.setTarget(valveTarget)

        print("Flow Temp aktuell: %.1f, Ziel: %.1f Ventil aktuell: %d, Ziel: %d" % (flowTemperature, targetFlowTemperature, valveCurrent, valveTarget)) 

    def numberOfOpenValvesMessage(self, topic, payload, retained):
        numberOfOpenValves = int(payload)
        print("new value for number of open valves received: %d" % numberOfOpenValves)
        self.numberOfOpenValves = numberOfOpenValves
        self.numberOfOpenValvesProperty.value = numberOfOpenValves
        if (numberOfOpenValves == 0):
            self.heatPumpController.off()
        else:
            self.heatPumpController.on()


    

    
