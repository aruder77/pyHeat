from homie.device import HomieDevice, await_ready_state
from utime import time
from flow_temperature_regulator_node import FlowTemperatureRegulatorNode
from heating_controller_node import HeatingControllerNode
from target_flow_temperature_calculator_node import TargetFlowTemperatureCalculatorNode
from valve_controller_node import ValveControllerNode
from temperature_reader_node import TemperatureReaderNode
from heat_pump_controller_node import HeatPumpControllerNode


class PyHeatDevice(HomieDevice):

    def __init__(self, settings):
        super().__init__(settings)

        flowTemperatureRegulator = FlowTemperatureRegulatorNode()
        targetFlowTemperatureCalculator = TargetFlowTemperatureCalculatorNode()
        valveController = ValveControllerNode()
        temperatureReader = TemperatureReaderNode()
        heatPumpController = HeatPumpControllerNode()

        self.add_node(flowTemperatureRegulator)
        self.add_node(targetFlowTemperatureCalculator)
        self.add_node(valveController)
        self.add_node(temperatureReader)
        self.add_node(heatPumpController)

        heatingController = HeatingControllerNode(temperatureReader, flowTemperatureRegulator, targetFlowTemperatureCalculator, valveController, heatPumpController)
        self.add_node(heatingController)


