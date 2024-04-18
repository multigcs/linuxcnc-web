const apiEndpoint = '/api_v1/';


const vm = new Vue({
    el: '#vm',
    delimiters: ['[[', ']]'],
    data: {

        estop: 0,
        enabled: 0,
        paused: 0,

        line_num: 0,
        line_num_last: 0,

        interp_state: 0,
        task_state: 0,
        feedrate: 100.0,
        rapidrate: 100.0,

        axisNames: [],
        position: {},
        homed: {},

        spindle: 0,
        tool_in_spindle: 0,

        current_vel: 0,

        errors: {},
        mdi_commands: [],

        din: [],
        dout: [],
        ain: [],
        aout: [],
    },
    created: function(){
        this.fetch()
    },

    methods: {
        mdiCommand: async function () {
            command = document.getElementById("mdi_command").value;
            const gResponse = await fetch(apiEndpoint + 'mdi/' + command);
            //const gObject = await gResponse.json();
            console.log(gResponse);
        },
        doApiCall: async function (name) {
            const gResponse = await fetch(apiEndpoint + name);
            //const gObject = await gResponse.json();
            console.log(gResponse);
        },
        JogStart: async function (axis, speed) {
            const gResponse = await fetch(apiEndpoint + 'JogStart/' + axis + '/' + speed);
            //const gObject = await gResponse.json();
            console.log(gResponse);
        },
        JogStop: async function (axis) {
            const gResponse = await fetch(apiEndpoint + 'JogStop/' + axis);
            //const gObject = await gResponse.json();
            console.log(gResponse);
        },
        setState: async function (state) {
            const gResponse = await fetch(apiEndpoint + 'setState/' + state);
            //const gObject = await gResponse.json();
            console.log(gResponse);
        },
        feedrateChange: async function () {
            const gResponse = await fetch(apiEndpoint + 'feedrate/' + this.feedrate / 100.0);
            //const gObject = await gResponse.json();
            console.log(gResponse);
        },
        rapidrateChange: async function () {
            const gResponse = await fetch(apiEndpoint + 'rapidrate/' + this.rapidrate / 100.0);
            //const gObject = await gResponse.json();
            console.log(gResponse);
        },
        spindleChange: async function () {
            for (const spindle in this.spindle) {
                const gResponse = await fetch(apiEndpoint + 'speedlerate/' + spindle + '/' + this.spindle[spindle]['override'] / 100.0);
                console.log(gResponse);
            }
        },

        fetch: async function() {
            const gResponse = await fetch(apiEndpoint + 'update');
            const gObject = await gResponse.json();

            this.estop = gObject.estop;
            this.enabled = gObject.enabled;
            this.paused = gObject.paused;

            this.mdi_commands = gObject.mdi_commands;
            this.errors = gObject.errors;
            if (gObject.line_num != this.line_num) {
                if (this.line_num != 0) {
                    document.getElementById('ln' + this.line_num).style.color = "black";
                }
                this.line_num = gObject.line_num;
                if (this.line_num != 0) {
                    document.getElementById('ln' + this.line_num).style.color = "red";
                    if (this.line_num > 4) {
                        document.getElementById('ln' + (this.line_num - 4)).scrollIntoView();
                    } else {
                        document.getElementById('ln' + this.line_num).scrollIntoView();
                    }
                }
            }

            this.interp_state = gObject.interp_state;
            this.task_state = gObject.task_state;

            this.feedrate = gObject.feedrate * 100.0;
            this.rapidrate = gObject.rapidrate * 100.0;

            this.axisNames = gObject.axisNames;
            this.position = gObject.position;
            this.spindle = gObject.spindle;

            for (const spindle in this.spindle) {
                this.spindle[spindle]['override'] = this.spindle[spindle]['override'] * 100.0;
            }
            this.tool_in_spindle = gObject.tool_in_spindle;
            this.homed = gObject.homed;
            this.current_vel = gObject.current_vel;
            this.din = gObject.din;
            this.dout = gObject.dout;
            this.ain = gObject.ain;
            this.aout = gObject.aout;


            element = document.getElementById("position");
            height = parseFloat(element.getAttribute("_height"));
            border = parseFloat(element.getAttribute("_border"));

            element.setAttribute("cx", parseFloat(this.position.X.pos) + border)
            element.setAttribute("cy", height - parseFloat(this.position.Y.pos) - border)

        }
    },
    mounted: function () {
      window.setInterval(() => {
        this.fetch()
      }, 500)
    }


})
