from homie.property import HomieProperty
from homie.node import HomieNode
from homie.constants import INTEGER
from homie.device import await_ready_state
from machine import Pin
import uasyncio as asyncio
from uasyncio import sleep_ms

class ValveControllerNode(HomieNode):

    WORKER_DELAY = const(10)
    VALVE_ONE_PERCENT_OPEN_CYCLES = const(55)

    CLOSE, HOLD, OPEN = range(-1,1)

    closePin = Pin(0, Pin.OUT)
    openPin = Pin(0, Pin.OUT)

    valveTarget: int
    valveCurrent: int

    def __init(self):
        super().__init__(id="Valve", name="Valve", type="Controller")

        self.valveTargetProperty = HomieProperty(
            id="valveTarget",
            name="valveTarget",
            datatype=INTEGER,
            unit="%",
            default=0,
        )
        self.add_property(self.valveTargetProperty)

        self.valveCurrentProperty = HomieProperty(
            id="valveCurrent",
            name="valveCurrent",
            datatype=INTEGER,
            unit="%",
            default=0,
        )
        self.add_property(self.valveCurrentProperty)

        # setup valve control
        self.closeValve()


        # start loop 
        asyncio.createTask(self.workerLoop())

    def closeValve(self):
        self.openPin.off()
        self.closePin.on()

        sleep_ms(self.VALVE_ONE_PERCENT_OPEN_CYCLES * 10 * 100);

        self.closePin.off()


    def setTarget(self, target: int):
        if (target >= 0 and target <= 100):
            self.valveTarget = target
            self.valveTargetProperty.value = target


    @await_ready_state
    async def workerLoop(self):
        while True: 
            self.every100Milliseconds()

            await sleep_ms(self.WORKER_DELAY)       


    def adjustTargetValvePosition(self):
        # check, if new target was set in the meantime...
        if (self.tempValveTarget != self.valveTarget):
            self.valveTarget = self.tempValveTarget
            print("Ventil Ziel: %d" % self.valveTarget)

            # if completely open or closed, make sure it is really completely open/closed.
            if (self.valveTarget == 100 and self.valveCurrent < 100):
                self.valveTarget = 103
            elif (self.valveTarget == 0 and self.valveCurrent > 0):
                self.valveTarget = -3

            self.motorAdjustCounter = max(-103.0, min(103.0, float(self.valveTarget - self.valveCurrent))) * self.VALVE_ONE_PERCENT_OPEN_CYCLES
            print("MotorAdjustCounter: %d" % self.motorAdjustCounter)


    def every10Milliseconds(self):
        # adjust 2-point regulation
        if (self.motorAdjustCounter > 0):
            if (self.valveState != 1):
                print("opening valve...")
                self.valveState = 1
                self.openPin.on()
                self.closePin.off()
            if ((self.motorAdjustCounter % self.VALVE_ONE_PERCENT_OPEN_CYCLES) == 0 and self.valveCurrent < 100):
                self.valveCurrent += 1
                self.adjustTargetValvePosition()
            self.motorAdjustCounter -= 1
        elif (self.motorAdjustCounter < 0):
            if (self.valveState != 1):
                print("closing valve...")
                self.valveState = -1
                self.openPin.off()
                self.closePin.on()
            if ((self.motorAdjustCounter % self.VALVE_ONE_PERCENT_OPEN_CYCLES) == 0 and self.valveCurrent > 0):
                self.valveCurrent -= 1
                self.adjustTargetValvePosition()
            self.motorAdjustCounter += 1
        else:
            if (self.valveState != 0):
                print("keeping valve state...")
                self.valveState = 0

                # keep current valve position
                self.openPin.off()
                self.closePin.off()
            self.adjustTargetValvePosition();
