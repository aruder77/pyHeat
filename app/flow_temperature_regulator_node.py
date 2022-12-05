from homie.property import HomieProperty
from homie.node import HomieNode
from homie.constants import FLOAT
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
        super().__init__(id="pid", name="Flow Temperature Regulator PID", type="Controller")

        self.pid = PID(self.kP, self.kI, self.kD, setpoint=self.targetFlowTemperature, scale='s')
        self.pid.output_limits = (0, 100)
        self.pid.sample_time = None

        self.kPProperty = HomieProperty(
            id="kP",
            name="kP",
            settable=True,
            datatype=FLOAT,
            default=self.kP,
            on_message=self.kPPropertyMessage,
        )
        self.add_property(self.kPProperty)

        self.tNProperty = HomieProperty(
            id="tN",
            name="tN",
            settable=True,
            datatype=FLOAT,
            default=self.tN,
            on_message=self.tNPropertyMessage,
        )
        self.add_property(self.tNProperty)

    def kPPropertyMessage(self, topic, payload, retained):
        kP = float(payload)
        if (kP >= 0.0 and kP < 100.0):
            self.kP = kP
            
    def tNPropertyMessage(self, topic, payload, retained):
        tN = float(payload)
        if (tN >= 0.0 and tN < 10000.0):
            self.tN = tN

    def calculateValveTarget(self, currentFlowTemperature, targetFlowTemperature):
        self.currentFlowTemperature = currentFlowTemperature
        self.targetFlowTemperature = targetFlowTemperature
        self.pid.setpoint = self.targetFlowTemperature
        self.valveTarget = self.pid(self.currentFlowTemperature)
        return int(self.valveTarget)

    def setTunings(self, kP, tN):
        self.kP = kP
        self.kPProperty.value = kP
        self.tN = tN
        self.tNProperty.value = tN
        self.kI = kP/tN
        self.pid.tunings = (self.kP, self.kI, self.kD)
        
