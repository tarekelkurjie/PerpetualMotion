# ////////////////////////////////////////////////////////////////
# //                     IMPORT STATEMENTS                      //
# ////////////////////////////////////////////////////////////////

import math
import sys
import time
import threading

from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.clock import Clock
from kivy.animation import Animation
from functools import partial
from kivy.config import Config
from kivy.core.window import Window
from pidev.kivy import DPEAButton
from pidev.kivy import PauseScreen
from time import sleep
from dpeaDPi.DPiComputer import *
from dpeaDPi.DPiStepper import *


# ////////////////////////////////////////////////////////////////
# //                      GLOBAL VARIABLES                      //
# //                         CONSTANTS                          //
# ////////////////////////////////////////////////////////////////
ON = False
OFF = True
HOME = True
TOP = False
OPEN = False
CLOSE = True
YELLOW = .180, 0.188, 0.980, 1
BLUE = 0.917, 0.796, 0.380, 1
DEBOUNCE = 0.1
INIT_RAMP_SPEED = 200
RAMP_LENGTH = 725


# ////////////////////////////////////////////////////////////////
# //            DECLARE APP CLASS AND SCREENMANAGER             //
# //                     LOAD KIVY FILE                         //
# ////////////////////////////////////////////////////////////////
class MyApp(App):
    def build(self):
        self.title = "Perpetual Motion"
        print("Intitialize!")
        return sm


Builder.load_file('main.kv')
Window.clearcolor = (.1, .1, .1, 1)  # (WHITE)

# ////////////////////////////////////////////////////////////////
# //                    SLUSH/HARDWARE SETUP                    //
# ////////////////////////////////////////////////////////////////
sm = ScreenManager()

ramp = DPiStepper()
ramp.setBoardNumber(0)

if ramp.initialize() is not True:
    print('Failed to initialize ramp stepper')
    exit(1)

ramp.enableMotors(True)

microstepping = 8
ramp.setMicrostepping(microstepping)

dpiComputer = DPiComputer()


# ////////////////////////////////////////////////////////////////
# //                       MAIN FUNCTIONS                       //
# //             SHOULD INTERACT DIRECTLY WITH HARDWARE         //
# ////////////////////////////////////////////////////////////////

# ////////////////////////////////////////////////////////////////
# //        DEFINE MAINSCREEN CLASS THAT KIVY RECOGNIZES        //
# //                                                            //
# //   KIVY UI CAN INTERACT DIRECTLY W/ THE FUNCTIONS DEFINED   //
# //     CORRESPONDS TO BUTTON/SLIDER/WIDGET "on_release"       //
# //                                                            //
# //   SHOULD REFERENCE MAIN FUNCTIONS WITHIN THESE FUNCTIONS   //
# //      SHOULD NOT INTERACT DIRECTLY WITH THE HARDWARE        //
# ////////////////////////////////////////////////////////////////

def openGate():
    dpiComputer.writeServo(0, 90)


def closeGate():
    dpiComputer.writeServo(0, 0)


def staircaseOn(speed):
    dpiComputer.writeServo(1, 90+speed)


def staircaseOff():
    dpiComputer.writeServo(1, 90)


def rampOn():
    ramp.moveToAbsolutePositionInSteps(0, -45000, True)


def rampHome(speed):
    ramp.moveToHomeInSteps(0, 1, speed*microstepping, 50000)


class MainScreen(Screen):
    version = 0
    staircaseSpeedText = '0'
    rampSpeed = INIT_RAMP_SPEED*10
    rampDisplaySpeed = INIT_RAMP_SPEED
    staircaseSpeed = 40

    gateIsOpen = False
    stairsAreOn = False

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        print("Create MainScreen Object")
        self.initialize()

    def toggleGate(self):
        if self.gateIsOpen is False:
            openGate()
            self.ids.gate.text = "Close Gate"
            self.gateIsOpen = True
        else:
            closeGate()
            self.ids.gate.text = "Open Gate"
            self.gateIsOpen = False

    def toggleStaircase(self):
        if self.stairsAreOn is False:
            staircaseOn(self.staircaseSpeed)
            self.ids.staircase.text = 'Staircase Off'
            self.stairsAreOn = True
        else:
            staircaseOff()
            self.ids.staircase.text = "Staircase On"
            self.stairsAreOn = False

    def toggleRamp(self):
        ramp.setSpeedInStepsPerSecond(0, self.rampSpeed*microstepping)
        rampHome(self.rampSpeed)
        print('Ramp home')
        rampOn()
        sleep(0.2)
        rampHome(self.rampSpeed)

    def auto(self):
        rampHome(self.rampSpeed)
        staircaseOn(self.staircaseSpeed)
        openGate()
        while dpiComputer.readDigitalIn(dpiComputer.IN_CONNECTOR__IN_0) == 1:
            sleep(0.5)
        else:
            rampOn()
            sleep(0.5)
            rampHome(self.rampSpeed)
            staircaseOff()
            closeGate()

    def setRampSpeed(self, speed):
        self.rampSpeed = speed*10
        self.ids.rampSpeedLabel.text = f"Ramp Speed: {speed}"

    def setStaircaseSpeed(self, speed):
        self.staircaseSpeed = speed

    def initialize(self):
        closeGate()
        staircaseOff()
        ramp.moveToHomeInSteps(0, 1, self.rampSpeed*microstepping, 50000)

    def resetColors(self):
        self.ids.gate.color = YELLOW
        self.ids.staircase.color = YELLOW
        self.ids.ramp.color = YELLOW
        self.ids.auto.color = BLUE

    def quit(self):
        print("Exit")
        MyApp().stop()


sm.add_widget(MainScreen(name='main'))

# ////////////////////////////////////////////////////////////////
# //                          RUN APP                           //
# ////////////////////////////////////////////////////////////////

MyApp().run()
