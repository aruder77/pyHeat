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

    K2 = 0.001
    K1 = 1 - K2

    def __init__(self):
        super().__init__(id="Temperatures", name="Temperatures", type="Controller")

        self.delayAf = 0
        self.delayRuef = 0
        self.delayVf = 0

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

        self.setup()
    
    

    def setup(self):

        self.adcAf = ADC(Pin(AF_TEMP_PIN))
        self.adcRuef = ADC(Pin(RUEF_TEMP_PIN))
        self.adcVf = ADC(Pin(VF_TEMP_PIN))

        self.afFilterData = array.array('i', (0 for _ in range(self.NO_OF_SAMPLES_TO_AVG + 3))) # Average over 16 samples
        self.afFilterData[0] = len(self.afFilterData)

        self.ruefFilterData = array.array('i', (0 for _ in range(self.NO_OF_SAMPLES_TO_AVG + 3))) # Average over 16 samples
        self.ruefFilterData[0] = len(self.ruefFilterData)

        self.vfFilterData = array.array('i', (0 for _ in range(self.NO_OF_SAMPLES_TO_AVG + 3))) # Average over 16 samples
        self.vfFilterData[0] = len(self.vfFilterData)

        self.afVoltage = 0.0
        self.ruefVoltage = 0.0
        self.vfVoltage = 0.0

        self.readTemperaturesTimer = Timer(-1)
        self.readTemperaturesTimer.init(period=100, mode=Timer.PERIODIC, callback=lambda t:self.readTemperatures())


    def readTemperatures(self):
        self.delayAf = self.lowpassFilter(self.adcAf.read_u16() >> 4, self.delayAf)
        self.afVoltage = self.delayAf / 4096 * self.REF_VOLTAGE 
        self.delayRuef = self.lowpassFilter(self.adcRuef.read_u16() >> 4, self.delayRuef)
        self.ruefVoltage =  self.delayRuef / 4096 * self.REF_VOLTAGE
        self.delayVf = self.lowpassFilter(self.adcVf.read_u16() >> 4, self.delayVf)
        self.vfVoltage = self.delayVf / 4096 * self.REF_VOLTAGE


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
        print("flow: voltage:%.2f, resistence:%.2f, temperature:%.1f" % (self.vfVoltage, vfResistence, vfTemperature))
        self.flowTemperatureProperty.value = vfTemperature
        return vfTemperature


    def getReturnTemperature(self):
        ruefResistence = self.resistenceCorrection(self.calculateResistence(self.ruefVoltage))
        ruefTemperature = self.calculateTemperature(ruefResistence)
        print("reflux: voltage:%.2f, resistence:%.2f, temperature:%.1f" % (self.ruefVoltage, ruefResistence, ruefTemperature))
        self.returnTemperatureProperty.value = ruefTemperature
        return ruefTemperature


    def lowpassFilter(self, inp: int, delay: int):
        return (inp * self.K2) + (delay * self.K1)
