from machine import Timer, Pin
from homie.property import HomieProperty
from homie.node import HomieNode
from homie.constants import INTEGER, STRING
from homie.device import await_ready_state
from uasyncio import sleep_ms, create_task

class ValveControllerNode(HomieNode):

    WORKER_DELAY = const(10)
    VALVE_ONE_PERCENT_OPEN_CYCLES: int = 55

    CLOSE, HOLD, OPEN = (-1, 0, 1)

    def __init__(self):
        super().__init__(id="flowTempValve", name="Flow Temperature Valve", type="Controller")

        self.closePin = Pin(1, Pin.OUT)
        self.openPin = Pin(0, Pin.OUT)

        self.valveTarget = 0
        self.internalValveTarget = 0
        self.previousValveTarget = 0
        self.valveCurrent = 0
        self.valveState = self.HOLD

        self.motorAdjustCounter = 0

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

        self.resetValveProperty = HomieProperty(
            id="resetValve",
            name="resetValve",
            default="",
        )
        self.add_property(self.resetValveProperty)

        self.pauseValveUpdate = False

        create_task(self.closeValve())

        self.every10SecondsTimer = Timer(-1)
        self.every10SecondsTimer.init(period=10, mode=Timer.PERIODIC, callback=lambda t:self.every10Milliseconds())

        self.resetValveTimer = Timer(-1)
        self.resetValveTimer.init(period=86400000, mode=Timer.PERIODIC, callback=lambda t:self.resetValve()) # 24h
        


    async def closeValve(self):
        self.pauseValveUpdate = True
        print("closing all valves...")
        self.resetValveProperty.value = "resetting valve..."        

        self.openPin.off()
        self.closePin.on()

        await sleep_ms(self.VALVE_ONE_PERCENT_OPEN_CYCLES * 10 * 100);

        self.closePin.off()
        print("...finished closing all valves")
        self.pauseValveUpdate = False



    def setTarget(self, target: int):
        if (target != self.previousValveTarget and target >= 0 and target <= 100):
            self.valveTarget = target
            self.valveTargetProperty.value = target


    def adjustTargetValvePosition(self):
        # check, if new target was set in the meantime...
        if (self.valveTarget != self.previousValveTarget):
            print("Ventil Ziel: %d" % self.valveTarget)
            self.previousValveTarget = self.valveTarget

            # if completely open or closed, make sure it is really completely open/closed.
            if (self.valveTarget == 100 and self.valveCurrent < 100):
                self.internalValveTarget = 103
            elif (self.valveTarget == 0 and self.valveCurrent > 0):
                self.internalValveTarget = -3
            else:
                self.internalValveTarget = self.valveTarget


            self.motorAdjustCounter = int(int(max(-103, min(103, self.internalValveTarget - self.valveCurrent))) * self.VALVE_ONE_PERCENT_OPEN_CYCLES)
            print("MotorAdjustCounter: %d" % self.motorAdjustCounter)


    def every10Milliseconds(self):
        if (not self.pauseValveUpdate):
            # adjust 2-point regulation
            if (self.motorAdjustCounter > 0):
                if (self.valveState != self.OPEN):
                    print("opening valve...")
                    self.valveState = self.OPEN
                    self.openPin.on()
                    self.closePin.off()

                if ((self.motorAdjustCounter % self.VALVE_ONE_PERCENT_OPEN_CYCLES) == 0):
                    if (self.valveCurrent < 100):
                        self.valveCurrent += 1
                        self.valveCurrentProperty.value = self.valveCurrent
                    self.motorAdjustCounter -= 1
                    self.adjustTargetValvePosition()
                else:
                    self.motorAdjustCounter -= 1

            elif (self.motorAdjustCounter < 0):
                if (self.valveState != self.CLOSE):
                    print("closing valve...")
                    self.valveState = self.CLOSE
                    self.openPin.off()
                    self.closePin.on()

                if ((self.motorAdjustCounter % self.VALVE_ONE_PERCENT_OPEN_CYCLES) == 0):
                    if (self.valveCurrent > 0):
                        self.valveCurrent -= 1
                        self.valveCurrentProperty.value = self.valveCurrent
                    self.motorAdjustCounter += 1
                    self.adjustTargetValvePosition()
                else:
                    self.motorAdjustCounter += 1

            else:
                if (self.valveState != self.HOLD):
                    print("keeping valve state...")
                    self.valveState = self.HOLD

                    # keep current valve position
                    self.openPin.off()
                    self.closePin.off()

                self.adjustTargetValvePosition()

