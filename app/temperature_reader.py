import array
from machine import ADC, Pin
from avg_pico import avg
from machine import Timer

class TemperatureReader:

    AF_TEMP_PIN = const(26)
    RUEF_TEMP_PIN = const(27)
    VF_TEMP_PIN = const(28)

    REF_VOLTAGE = const(3300)

    NO_OF_SAMPLES_TO_AVG = const(16)

    def __init__(self):
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

        self.readTemperaturesTimer = Timer(-1)
        self.readTemperaturesTimer.init(period=100, mode=Timer.PERIODIC, callback=self.readTemperatures())


    def readTemperatures(self):
        self.afVoltage = avg(self.afFilterData, self.adcAf.read_u16(), 4) / 4096 * self.REF_VOLTAGE 
        self.ruefVoltage = avg(self.ruefFilterData, self.adcRuef.read_u16(), 4) / 4096 * self.REF_VOLTAGE
        self.vfVoltage = avg(self.vfFilterData, self.adcVf.read_u16(), 4) / 4096 * self.REF_VOLTAGE


    def calculateResistence(self, voltage: float):
        return voltage * self.REF_RESISTOR / (self.REF_VOLTAGE - voltage)


    def calculateTemperature(self, resistence: int, offset: int, factor: float):
        return (resistence - offset) / factor


    def getOutsideTemperature(self):
        afResistence = self.calculateResistence(self.afVoltage)
        afTemperature = self.calculateTemperature(afResistence, self.OUTSIDE_TEMP_OFFSET, self.OUTSIDE_TEMP_FACTOR)
        print("outside: voltage:%d, resistence:%d, temperature:%.1f" % (self.afVoltage, afResistence, afTemperature))
        return afTemperature


    def getFlowTemperature(self):
        vfResistence = self.calculateResistence(self.vfVoltage)
        vfTemperature = self.calculateTemperature(self.vfResistence, self.OUTSIDE_TEMP_OFFSET, self.OUTSIDE_TEMP_FACTOR)
        print("outside: voltage:%d, resistence:%d, temperature:%.1f" % (self.vfVoltage, vfResistence, vfTemperature))
        return vfTemperature


    def getReturnTemperature(self):
        ruefResistence = self.calculateResistence(self.ruefVoltage)
        ruefTemperature = self.calculateTemperature(self.ruefResistence, self.OUTSIDE_TEMP_OFFSET, self.OUTSIDE_TEMP_FACTOR)
        print("outside: voltage:%d, resistence:%d, temperature:%.1f" % (self.ruefVoltage, ruefResistence, ruefTemperature))
        return ruefTemperature
