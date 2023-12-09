from homie.property import HomieProperty
from homie.node import HomieNode
from homie.constants import FLOAT, INTEGER
from PID import PID



class FlowTemperatureRegulatorNode(HomieNode):

    kP = 2.6;
    tN = 1000;
    kI = kP/tN if tN > 0 else 0.0;
    kD = 0.0;      
    sampleTime = 59000;

    currentFlowTemperature = 20.0;
    targetFlowTemperature = 40.0;
    
    valveTarget = 0.0;
    valveCurrent = 0.0;

    def __init__(self):
        super().__init__(id="pid", name="Flow Temperature Regulator PID", type="Controller")

        self.pid = PID(self.kP, self.kI, self.kD, setpoint=self.targetFlowTemperature, scale='ms')
        self.pid.output_limits = (0, 100)
        self.pid.sample_time = self.sampleTime

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

        self.kIProperty = HomieProperty(
            id="kI",
            name="kI",
            datatype=FLOAT,
            default=self.kI
        )
        self.add_property(self.kIProperty)

        self.kDProperty = HomieProperty(
            id="kD",
            name="kD",
            datatype=FLOAT,
            default=self.kD
        )
        self.add_property(self.kDProperty)

        self.sampleTimeProperty = HomieProperty(
            id="sampleTime",
            name="sampleTime",
            datatype=INTEGER,
            default=self.sampleTime,
            on_message=self.sampleTimePropertyMessage,
            settable=True
        )
        self.add_property(self.sampleTimeProperty)


    def kPPropertyMessage(self, topic, payload, retained):
        kP = float(payload)
        if (kP >= 0.0 and kP < 100.0):
            self.setTunings(kP, self.tN)
            
    def tNPropertyMessage(self, topic, payload, retained):
        tN = float(payload)
        if (tN >= 0.0 and tN < 10000.0):
            self.setTunings(self.kP, tN)

    def sampleTimePropertyMessage(self, topic, payload, retained):
        sampleTime = int(payload)
        if (sampleTime >= 0 and sampleTime < 100000):
            self.sampleTime = sampleTime
            self.pid.sample_time = sampleTime

    def calculateValveTarget(self, currentFlowTemperature, targetFlowTemperature):
        self.currentFlowTemperature = currentFlowTemperature
        self.targetFlowTemperature = targetFlowTemperature
        self.pid.setpoint = self.targetFlowTemperature
        self.valveTarget = self.pid(self.currentFlowTemperature)
        print("PID called (%.1f, %.1f) -> %.1f" % (self.currentFlowTemperature, self.targetFlowTemperature, self.valveTarget))
        return int(self.valveTarget)

    def setTunings(self, kP, tN):
        self.kP = kP
        self.kPProperty.value = kP
        self.tN = tN
        self.tNProperty.value = tN
        self.kI = kP/tN if tN > 0 else 0.0
        self.kDProperty.value = self.kD
        self.kIProperty.value = self.kI
        self.pid.tunings = (self.kP, self.kI, self.kD)
        
