from homie.property import HomieProperty
from homie.node import HomieNode
from PID import PID



class FlowTemperatureRegulatorNode(HomieNode):

    kP = 2.0;
    tN = 120.0;
    kI = kP/tN;
    kD = 0.0;      

    currentFlowTemperature = 20.0;
    targetFlowTemperature = 40.0;
    
    valveTarget = 0.0;
    valveCurrent = 0.0;

    def __init__(self):
        super().__init__(id="FlowTemp", name="Flow Temperature Regulator", type="Controller")

        self.pid = PID(self.kP, self.kI, self.kD, setpoint=self.targetFlowTemperature, scale='s')
        self.pid.output_limits = (0, 100)
        self.pid.sample_time = 10

    def calculateValveTarget(self, currentFlowTemperature, targetFlowTemperature):
        self.currentFlowTemperature = currentFlowTemperature
        self.targetFlowTemperature = targetFlowTemperature
        self.pid.setpoint = self.targetFlowTemperature
        self.valveTarget = self.pid(self.currentFlowTemperature)

    def setTunings(self, kP, tN):
        self.kP = kP
        self.tN = tN
        self.kI = kP/tN
        self.pid.tunings = (self.kP, self.kI, self.kD)
        
