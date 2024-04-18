import datetime
import sys
import time

import linuxcnc
from flask import Blueprint

AXIS_NAMES = ["X", "Y", "Z", "A", "B", "C", "U", "V", "W"]

s = linuxcnc.stat()
c = linuxcnc.command()


print(dir(s))
print(dir(c))


"""

c.home(0)
c.home(1)
c.home(2)

#c.mode(linuxcnc.MODE_AUTO)
c.program_open("/tmp/simple.ngc")
c.reset_interpreter()
c.auto(linuxcnc.AUTO_RUN, 0)

"""


api_bp = Blueprint("api_bp", __name__)


@api_bp.route("/JogStart/<axis>/<speed>")
def do_JogStart(axis, speed):
    if axis in AXIS_NAMES:
        axis = AXIS_NAMES.index(axis)
    c.mode(linuxcnc.MODE_MANUAL)
    c.jog(linuxcnc.JOG_CONTINUOUS,  True, int(axis), int(speed))
    return "OK"

@api_bp.route("/JogStop/<axis>")
def do_JogStop(axis):
    if axis in AXIS_NAMES:
        axis = AXIS_NAMES.index(axis)
    c.jog(linuxcnc.JOG_STOP,  True, int(axis))
    return "OK"

@api_bp.route("/auto/<mode>")
def do_auto(mode):
    s.poll()
    if s.task_mode != linuxcnc.MODE_AUTO:
        c.mode(linuxcnc.MODE_AUTO)
    print(mode)
    if mode == "RUN":
        c.auto(linuxcnc.AUTO_RUN, 1)
    elif mode == "STOP":
        c.auto(linuxcnc.AUTO_STEP)
    elif mode == "PAUSE":
        if s.interp_state != linuxcnc.INTERP_IDLE:
            c.auto(linuxcnc.AUTO_PAUSE)
    elif mode == "RESUME":
        c.auto(linuxcnc.AUTO_RESUME)
    elif mode == "STOP":
        c.auto(linuxcnc.AUTO_STOP)


    return "OK"

@api_bp.route("/setState/<state>")
def do_setstate(state):
    c.state(int(state))
    return "OK"

@api_bp.route("/feedrate/<rate>")
def do_feedrate(rate):
    c.feedrate(float(rate))
    return "OK"

@api_bp.route("/rapidrate/<rate>")
def do_rapidrate(rate):
    c.rapidrate(float(rate))
    return "OK"

@api_bp.route("/speedlerate/<spindle>/<rate>")
def do_spindleChange(spindle, rate):
    c.spindleoverride(float(rate), int(spindle))
    return "OK"

@api_bp.route("/homing/<axis>")
def homing(axis):
    if axis in AXIS_NAMES:
        axis = AXIS_NAMES.index(axis)
    c.mode(linuxcnc.MODE_MANUAL)
    c.teleop_enable(0)
    c.wait_complete()
    c.home(int(axis))
    return "OK"


@api_bp.route("/update")
def update():

    date = str(datetime.datetime.now())

    s.poll()

    data = {
        "file": s.file,
        "estop": s.estop,
        "enabled": s.enabled,
        "interp_state": s.interp_state,
        "task_state": s.task_state,
        "feedrate": s.feedrate,
        "rapidrate": s.rapidrate,
        "axisNames": AXIS_NAMES,
        "position": {},
        "spindle": {},
        "tool_in_spindle": s.tool_in_spindle,
        "current_vel": f"{s.current_vel * 60:08.2f}",
        "din": s.din,
        "dout": s.dout,
        "ain": s.ain,
        "aout": s.aout,
        "paused": s.paused,
    }
    for n, pos in enumerate(s.position[:3]):
        data["position"][AXIS_NAMES[n]] = {"homed_str": "homed" if s.homed[n] else "not-homed", "homed": s.homed[n], "pos": f"{pos:0.3f}"}

    for n, spindle in enumerate(s.spindle[:2]):
        data["spindle"][n] = spindle

    #print(data)
    return data
