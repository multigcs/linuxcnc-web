import math
import re
import os
import glob
import time
import datetime
import linuxcnc

from flask import Blueprint, render_template, request, redirect


COMMAND = re.compile("(?P<line>\d+) N\.* (?P<type>[A-Z_]+)\((?P<coords>.*)\)")
ALLOWED_EXTENSIONS = {'ngc', 'ng'}
UPLOAD_FOLDER = f"{os.path.expanduser('~')}/nc_files/"

# http://linuxcnc.org/docs/master/html/de/config/python-interface.html

s = linuxcnc.stat()
c = linuxcnc.command()

client_bp = Blueprint(
    "client_bp",
    __name__,  # 'Client Blueprint'
    template_folder="templates",  # Required for our purposes
    static_folder="static",  # Again, this is required
    static_url_path="/client/static",  # Flask will be confused if you don't do this
)


@client_bp.route("/files")
def files():
    files = {}
    for filename in glob.glob(f"{UPLOAD_FOLDER}/*.ngc"):
        file_stats = os.stat(filename)
        
        mtime = datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')
        
        files[filename] = {"name": os.path.basename(filename), "size": file_stats.st_size, "mtime": mtime}
    return render_template("files.html", files=files)


@client_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        filefd = request.files['file']
        if filefd:
            target = f"{UPLOAD_FOLDER}/{filefd.filename}"
            print(target)
            open(target, "wb").write(filefd.read());
            return redirect("/files")
    return 'No file uploaded'



@client_bp.route("/")
def index():
    filename = request.args.get("filename")
    if filename:
        print(f"loading file: {filename}")

        s.poll()
        if s.task_mode != linuxcnc.MODE_AUTO:
            c.mode(linuxcnc.MODE_AUTO)
        c.program_open(filename)

        return redirect("/")


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
            if result["type"] in {"ARC_FEED"}:
                coords = result["coords"].split(",")
                new_x = float(coords[0].strip()) - pos_min_x + border
                new_y = height - (float(coords[1].strip()) - pos_min_y) - border
                new_z = float(coords[2].strip())
                if coords[4].strip()[0] == "-":
                    direction = "cw"
                else:
                    direction = "ccw"
                radius = round(math.dist((float(coords[0].strip()), float(coords[1].strip())), (float(coords[2].strip()), float(coords[3].strip()))), 4)
                if last_pos:
                    last_x, last_y, last_z = last_pos
                    if direction == "cw":
                        svg_out.append(f'<g stroke="red" fill="none" style="stroke:{color};stroke-width:0.1"><path d="M {last_x} {last_y} A {radius} {radius} 0 0 1 {new_x} {new_y}" /></g>')
                    else:
                        svg_out.append(f'<g stroke="red" fill="none" style="stroke:{color};stroke-width:0.1"><path d="M {new_x} {new_y} A {radius} {radius} 0 0 1 {last_x} {last_y}" /></g>')
                last_pos = (new_x, new_y, new_z)
            elif result["type"] in {"STRAIGHT_FEED", "STRAIGHT_TRAVERSE"}:
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

    content_ln = []
    for ln, line in enumerate(content.split("\n"), 1):
        content_ln.append(f"<div id='ln{ln}'>{ln:05}: {line}</div>")


    return render_template("index.html", gcode="".join(content_ln), svg_str=svg_str)


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


