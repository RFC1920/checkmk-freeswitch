#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from .agent_based_api.v1 import *
import configparser
import os
script_dir = os.path.dirname('/opt/checkmk-freeswitch/checks/config.ini')

# Display output from freeswitch (Phone) agent

config = configparser.ConfigParser()
config.readfp(open(script_dir + '/config.ini'))
thresh = dict(config.items('thresholds'))
crit_in  = thresh['crit_in']
crit_out = thresh['crit_out']
warn_in  = thresh['warn_in']
warn_out = thresh['warn_out']

swstatus = ""
gateways = ""
calls_in = 0
calls_out = 0
failed_in = 0
failed_out = 0
registrations = 0

###################
# Check Functions #
###################
def parse_freeswitch(string_table):
    parsed = []
    debug = False
    global swstatus
    global gateways
    global calls_in
    global calls_out
    global failed_in
    global failed_out
    global registrations
    ingw = False
    inst = False

    for line in string_table:
        if debug:
            print("Testing: " + line[0])

        if ingw == True:
            inst = False
            gateways = gateways + "\n" + " ".join(line)

        elif inst == True:
            ingw = False
            swstatus = swstatus + "\n" + " ".join(line)

        if "show-status" in line[0]:
            inst = True
            if debug:
                print("Found start of switch status")

        elif "sofia-status-internal" in line[0]:
            ingw = True
            inst = False
            if debug:
                print("Found start of gateways")

        elif "gateway" in line[0]:
            ingw = False
            gateways = gateways + "\n" + " ".join(line)
            if debug:
                print(gateways)

        elif "Current Stack Size" in line:
            inst = False
            swstatus = swstatus + "\n" + " ".join(line)

        elif "FAILED-CALLS-IN" in line[0]:
            failed_in = line[1]
            if debug:
                print("Failed calls in: " + str(failed_in))
        elif "FAILED-CALLS-OUT" in line[0]:
            failed_out = line[1]
            if debug:
                print("Failed calls out: " + str(failed_out))
        elif "CALLS-IN" in line[0]:
            calls_in = line[1]
            if debug:
                print("Calls in: " + str(calls_in))
        elif "CALLS-OUT" in line[0]:
            calls_out = line[1]
            if debug:
                print("Calls out: " + str(calls_out))

        elif "REGISTRATIONS" in line[0]:
            registrations = line[1]
            if debug:
                print("Registrations: " + str(registrations))

    return gateways, swstatus, calls_in, failed_in, calls_out, failed_out, registrations

def inventory_freeswitch(info):
    yield Result(state=State.OK, summary = gateways + "\n" + swstatus)

def discover_freeswitch(section):
    yield Service()

def check_freeswitch(section):
    # Call count/fail here!
    text = ''
    failtext = ''
    status = State.OK

    global gateways
    global swstatus
    perfdata = [ gateways ]

    if calls_in == 0:
        text += "No calls in;"
        failed_in_pct = 0
    else:
        failed_in_pct = abs(int(failed_in) / int(calls_in))
        percentage = "{:.0%}".format(failed_in_pct)
        failtext += "High inbound call failure " + percentage + "; "

    if calls_out == 0:
        text += "No calls out;"
        failed_out_pct = 0
    else:
        failed_out_pct = abs(int(failed_out) / int(calls_out))
        percentage = "{:.0%}".format(failed_out_pct)
        failtext += "High outbound call failure " + percentage + "; "

    # CALLS IN
    if failed_in_pct * 100 > int(warn_in):
        status = State.WARN
        text = failtext
    elif failed_in_pct * 100 > int(crit_in):
        status = State.CRIT
        text = failtext
    else:
        percentage = "{:.0%}".format(failed_in_pct)
        text += "Inbound call failure " + percentage + "; "

    # CALLS OUT
    if failed_out_pct * 100 > int(warn_out):
        status = State.WARN
        text = failtext
    elif failed_out_pct * 100 > int(crit_out):
        status = State.CRIT
        text = failtext
    else:
        percentage = "{:.0%}".format(failed_out_pct)
        text += "Outbound call failure " + percentage + "; "

    text += str(registrations) + " Registrations"

    yield Result(state=status, summary=text)
    #yield Metric("calls_in", calls_in)
    #yield Metric("calls_out", calls_out)

register.check_plugin(
    name = "freeswitch",
    service_name = "Freeswitch",
    #inventory_function = inventory_freeswitch,
    discovery_function = discover_freeswitch,
    check_function = check_freeswitch
)

register.agent_section(
    name = "freeswitch",
    parse_function = parse_freeswitch,
)

