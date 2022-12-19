import array
from machine import ADC, Pin, Timer
from homie.node import HomieNode
from homie.property import HomieProperty
from homie.constants import FLOAT

class TemperatureReaderNode(HomieNode):

    AF_TEMP_PIN = const(28)
    RUEF_TEMP_PIN = const(26)
    VF_TEMP_PIN = const(27)

    REF_VOLTAGE = const(3300)
    REF_RESISTOR = const(3875)
    
    RESISTENCE_CORRECTION_OFFSET = -20
    RESISTENCE_CORRECTION_FACTOR = 1.0

    NO_OF_SAMPLES_TO_AVG = const(128)

    TEMP_FACTOR = 0.257003341043434
    TEMP_OFFSET = -257.003341043434

    K2 = 0.0005
    K1 = 1 - K2

    def __init__(self):
        super().__init__(id="Temperatures", name="Temperatures", type="Controller")

        self.delayAf = None
        self.delayRuef = None
        self.delayVf = None
        self.delayRawVf = None

        self.flowTemperatureProperty = HomieProperty(
            id="flowTemperature",
            name="flowTemperature",
            datatype=FLOAT,
            unit="°C", 
            format="10.0",
            settable=False,
            default=0.0,
        )
        self.add_property(self.flowTemperatureProperty)

        self.rawFlowTemperatureProperty = HomieProperty(
            id="rawFlowTemperature",
            name="rawFlowTemperature",
            datatype=FLOAT,
            unit="°C", 
            format="10.0",
            settable=False,
            default=0.0,
        )
        self.add_property(self.rawFlowTemperatureProperty)        

        self.outsideTemperatureProperty = HomieProperty(
            id="outsideTemperature",
            name="outsideTemperature",
            datatype=FLOAT,
            unit="°C", 
            format="10.0",
            settable=False,
            default=0.0,
        )
        self.add_property(self.outsideTemperatureProperty)

        self.returnTemperatureProperty = HomieProperty(
            id="returnTemperature",
            name="returnTemperature",
            datatype=FLOAT,
            unit="°C", 
            format="10.0",
            settable=False,
            default=0.0,
        )
        self.add_property(self.returnTemperatureProperty)   

        self.lowpassFilterK2Property = HomieProperty(
            id="lowpassFilterK2",
            name="lowpassFilterK2",
            datatype=FLOAT,
            settable=True,
            default=0.0005,
            on_message=self.lowpassFilterK2PropertyMessage
        )
        self.add_property(self.lowpassFilterK2Property)   

        self.setup()
    
    

    def setup(self):

        self.adcAf = ADC(Pin(AF_TEMP_PIN))
        self.adcRuef = ADC(Pin(RUEF_TEMP_PIN))
        self.adcVf = ADC(Pin(VF_TEMP_PIN))

        self.afVoltage = 0.0
        self.ruefVoltage = 0.0
        self.vfVoltage = 0.0
        self.rawVfVoltage = 0.0

        self.readTemperaturesTimer = Timer(-1)
        self.readTemperaturesTimer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.readTemperatures())



    def lowpassFilterK2PropertyMessage(self, topic, payload, retained):
        k2 = float(payload)
        if (k2 >= 0.0 and k2 <= 1.0):
            self.K2 = k2
            self.K1 = 1 - self.K2


    def readTemperatures(self):
        self.delayAf = self.lowpassFilter(self.adcAf.read_u16() >> 4, self.delayAf, self.K2)
        self.afVoltage = self.delayAf / 4096 * self.REF_VOLTAGE 
        self.delayRuef = self.lowpassFilter(self.adcRuef.read_u16() >> 4, self.delayRuef, self.K2)
        self.ruefVoltage =  self.delayRuef / 4096 * self.REF_VOLTAGE
        vfReading = self.adcVf.read_u16() >> 4
        self.delayVf = self.lowpassFilter(vfReading, self.delayVf, self.K2)
        self.vfVoltage = self.delayVf / 4096 * self.REF_VOLTAGE
        self.delayRawVf = self.lowpassFilter(vfReading, self.delayRawVf, 0.01)
        self.rawVfVoltage = self.delayRawVf / 4096 * self.REF_VOLTAGE 


    def calculateResistence(self, voltage: float):
        return voltage * self.REF_RESISTOR / (self.REF_VOLTAGE - voltage)

    def resistenceCorrection(self, resistence: float):
        return resistence * self.RESISTENCE_CORRECTION_FACTOR + self.RESISTENCE_CORRECTION_OFFSET


    def calculateTemperature(self, resistence: int):
        return self.TEMP_OFFSET + self.TEMP_FACTOR * resistence;


    def getOutsideTemperature(self):
        afResistence = self.resistenceCorrection(self.calculateResistence(self.afVoltage))
        afTemperature = self.calculateTemperature(afResistence)
        print("outside: voltage:%.2f, resistence:%.2f, temperature:%.1f" % (self.afVoltage, afResistence, afTemperature))
        self.outsideTemperatureProperty.value = afTemperature
        return afTemperature


    def getFlowTemperature(self):
        vfResistence = self.resistenceCorrection(self.calculateResistence(self.vfVoltage))
        vfTemperature = self.calculateTemperature(vfResistence)
        rawVfResistence = self.resistenceCorrection(self.calculateResistence(self.rawVfVoltage))
        rawVfTemperature = self.calculateTemperature(rawVfResistence)
        print("flow: voltage:%.2f, resistence:%.2f, temperature:%.1f" % (self.vfVoltage, vfResistence, vfTemperature))
        self.flowTemperatureProperty.value = vfTemperature
        self.rawFlowTemperatureProperty.value = rawVfTemperature
        return vfTemperature


    def getReturnTemperature(self):
        ruefResistence = self.resistenceCorrection(self.calculateResistence(self.ruefVoltage))
        ruefTemperature = self.calculateTemperature(ruefResistence)
        print("reflux: voltage:%.2f, resistence:%.2f, temperature:%.1f" % (self.ruefVoltage, ruefResistence, ruefTemperature))
        self.returnTemperatureProperty.value = ruefTemperature
        return ruefTemperature


    def lowpassFilter(self, inp: int, delayParam, k2):
        delay = inp if delayParam is None else delayParam
        return (inp * k2) + (delay * (1 - k2))
