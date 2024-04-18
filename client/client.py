import re
import os
import time
import linuxcnc
from flask import Blueprint, render_template
from flask import Blueprint

COMMAND = re.compile("(?P<line>\d+) N\.* (?P<type>[A-Z_]+)\((?P<coords>.*)\)")

# http://linuxcnc.org/docs/master/html/de/config/python-interface.html

s = linuxcnc.stat()

client_bp = Blueprint(
    "client_bp",
    __name__,  # 'Client Blueprint'
    template_folder="templates",  # Required for our purposes
    static_folder="static",  # Again, this is required
    static_url_path="/client/static",  # Flask will be confused if you don't do this
)


@client_bp.route("/")
def index():

    s.poll()
    filename = s.file
    if filename:
        content = open(filename, "r").read()
    else:
        content = ""

    svg_out = []
    p = os.popen(f"rs274 -g '{filename}'")
    output = p.readlines()
    r = p.close()
    last_pos = ()
    pos_min_x = 9999999999
    pos_min_y = 9999999999
    pos_max_x = 0
    pos_max_y = 0
    for line in output:
        result = COMMAND.match(line.strip())
        if result:
            if result["type"] in {"ARC_FEED", "STRAIGHT_FEED", "STRAIGHT_TRAVERSE"}:
                coords = result["coords"].split(",")
                new_x = float(coords[0].strip())
                new_y = float(coords[1].strip())
                new_z = float(coords[2].strip())
                pos_min_x = min(new_x, pos_min_x)
                pos_min_y = min(new_y, pos_min_y)
                pos_max_x = max(new_x, pos_max_x)
                pos_max_y = max(new_y, pos_max_y)

    print(pos_min_x, pos_min_y, pos_max_x, pos_max_y)

    width = pos_max_x - pos_min_x
    height = pos_max_y - pos_min_y

    border = max(height / 4, 2.0)

    width += (border * 2)
    height += (border * 2)


    for line in output:
        result = COMMAND.match(line.strip())
        if result:
            if result["type"] in {"ARC_FEED", "STRAIGHT_FEED", "STRAIGHT_TRAVERSE"}:
                coords = result["coords"].split(",")
                new_x = float(coords[0].strip()) - pos_min_x + border
                new_y = height - (float(coords[1].strip()) - pos_min_y) - border
                new_z = float(coords[2].strip())
                color = "white"
                if result["type"] == "STRAIGHT_TRAVERSE":
                    color = "green"
                if last_pos:
                    last_x, last_y, last_z = last_pos
                    svg_out.append(f'<line x1="{last_x}" y1="{last_y}" x2="{new_x}" y2="{new_y}" style="stroke:{color};stroke-width:0.1" />')
                last_pos = (new_x, new_y, new_z)

    lines = "".join(svg_out)
    svg_str = f'<svg height="100%" width="100%" viewBox="0 0 {width} {height}" style="background-color:black" xmlns="http://www.w3.org/2000/svg">{lines}<circle id="position" cx="0" cy="0" r="1" _border="{border}" _height="{height}" style="fill:red;stroke:red;stroke-width:0"/></svg>'

    return render_template("index.html", gcode=content.replace("\n", "<br/>"), svg_str=svg_str)


@client_bp.route("/get_file")
def get_file():
    s.poll()
    filename = s.file
    print("## filename ", filename)
    content = open(filename, "r").read()
    print("## ", content)
    return content.replace("\n", "<br/>")


@client_bp.route("/view")
def view():
    return render_template("view.html")

@client_bp.route("/mdi")
def do_mdi():

    s = linuxcnc.stat()
    c = linuxcnc.command()

    c.mode(linuxcnc.MODE_MDI)
    c.wait_complete() # warte bis mode Wechsel ausgeführt
    c.mdi("G0 X10 Y20 Z30")

    return "OK"


@client_bp.route("/start")
def do_start():

    s = linuxcnc.stat()
    c = linuxcnc.command()

    c.mode(linuxcnc.MODE_AUTO)

    c.auto(linuxcnc.AUTO_RUN, 0)
    #c.auto(linuxcnc.AUTO_STEP)
    #c.auto(linuxcnc.AUTO_PAUSE)
    #c.auto(linuxcnc.AUTO_RESUME)

    return "OK"


@client_bp.route("/spindle")
def do_spindle():

    s = linuxcnc.stat()
    c = linuxcnc.command()

    c.mode(linuxcnc.MODE_MANUAL)
    c.spindle(linuxcnc.SPINDLE_FORWARD, 1024)
    #c.spindle(linuxcnc.SPINDLE_OFF)

    return "OK"


@client_bp.route("/homeing")
def do_homeing():

    s = linuxcnc.stat()
    c = linuxcnc.command()

    print(dir(s))
    print(dir(c))

    c.mode(linuxcnc.MODE_MANUAL)

    c.spindle(linuxcnc.SPINDLE_FORWARD, 1024)
    #c.spindle(linuxcnc.SPINDLE_OFF)


    return "OK"


