#!/usr/bin/env python

"""
    This code is the Perfsonar MaDDash Wrapper
    Author: Italo Valcy <italovalcy@gmail.com>
    Updated by: Renata Frez <renatafrez@gmail.com>
"""

import argparse
import requests
import urllib3
import json
import sys
import time
urllib3.disable_warnings()

def list_grids(server_name):
    grids = []
    req = requests.Session()
    res = req.get('http://' + server_name + '/maddash/grids', verify=False)
    res.encoding = 'utf-8'
    data = res.json()
    if 'grids' not in data:
        return
    for grid in data['grids']:
        grids.append({"{#NAME}": grid['name'], "{#URI}": grid['uri']})
    return grids

def list_cells(server_name, grid_uri, mapping, option):
    # status code (https://docs.perfsonar.net/maddash_api_grids.html#status-codes)
    cells = []
    status_code = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'PENDING', 'DOWN']
    req = requests.Session()
    try:
        res = req.get('http://' + server_name + grid_uri, verify=False)
        res.encoding = 'utf-8'
        data = res.json()
        assert 'grid' in data
        assert 'name' in data
    except:
        sys.stderr.write("\033[91mERROR: fail to get/parser response for uri=%s\033[0m" % (grid_uri))
        return cells
    # Loop through grids, rows, columns and specific tests
    # https://docs.perfsonar.net/maddash_api_grids.html
    # grid[n]       2-dimenional array  A row in the grid
    # grid[n][m]    2-dimenional array  A cell in the grid. If null then no checks are configured for this cell.
    # grid[n][m][l] array or objects    A check in the grid
    for grid in data['grid']:
        if not isinstance(grid, list):
            continue
        for row in grid:
            if not isinstance(row, list):
                continue
            for col in grid:
                if not isinstance(col, list):
                    continue
                for cel in col:
                    if not isinstance(cel, dict) or 'uri' not in cel:
                        continue
                    uri_l = str(cel['uri']).split('/')
                    #print "http://%s/maddash/grids/%s/%s/%s/%s" % (server_name, uri_l[-4], uri_l[-3], uri_l[-2], uri_l[-1])

                    if option == "throughput" and uri_l[-1] == "Throughput":
                        cells = get_values(server_name, uri_l, cel, mapping)
                    elif option == "loss" and uri_l[-1] == "Loss":
                        cells = get_values(server_name, uri_l, cel, mapping)
                    elif option == "latency" and uri_l[-1] == "Packet+Loss":
                        cells = get_values (server_name, uri_l, cel, mapping)
                    elif option == "all":
                        cells = get_values (server_name, uri_l, cel, mapping)
                    
    if cells:
        return cells
                        
def get_values(server_name, uri_l, cel, mapping):
    req = requests.Session()
    cells = []
    try:
        full_uri = "http://%s/maddash/grids/%s/%s/%s/%s" % (server_name, uri_l[-4], uri_l[-3], uri_l[-2], uri_l[-1])
        res = req.get(full_uri, verify=False)
        res.encoding = 'utf-8'
        data = res.json()
        assert 'gridName' in data
    except:
        sys.stderr.write("\033[91mERROR: fail to get/parser response for uri=%s\033[0m" % (full_uri))
    for history in data['history']:
        if not isinstance(history, dict):
            continue
        if "Average" in history['returnParams']:
            last_value = history['returnParams']['Average']
        else:
            last_value = None
        break
    SRC_DST = data['rowName'] + '->' + data['colName']
    if uri_l[-1] != "Packet+Loss":
        cells.append({'{#NAME}': data['gridName'],
                        '{#SRC_DST}' : SRC_DST,
                        '{#STATUS}': data['statusShortName'],
                        '{#URI}' : str(cel['uri']),
                        '{#TYPE}' : uri_l[-1],
                        '{#VALUE}': last_value})
    else:
        req = requests.Session()
        uri_esmond = None
        for i in mapping:
            if i['{#SRC_DST}'] == SRC_DST:
                uri_esmond = i['{#URI}']
                break
        if uri_esmond:
            url_full = 'http://' + server_name + '/esmond/perfsonar/archive/' + uri_esmond + "/histogram-owdelay/statistics/0?time-range=300&limit=1"
            res = req.get(url_full, verify=False)
            res.encoding = 'utf-8'
            esmond_data = res.json()
            #if not isinstance(esmond_data, list):
            #    continue
            if esmond_data:
                for val in esmond_data:
                    value = str(val['val']['mean']).decode('utf8')
                    break
            else:
                value = None
            cells.append({'{#NAME}': data['gridName'],
                            '{#SRC_DST}' : SRC_DST,
                            '{#STATUS}': data['statusShortName'],
                            '{#URI}' : str(uri_esmond),
                            '{#TYPE}' : "Latency",
                            '{#VALUE}': value})   
    return cells 

def get_check_status(server_name, check_uri):
    # status code (https://docs.perfsonar.net/maddash_api_grids.html#status-codes)
    status_code = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'PENDING', 'DOWN']
    req = requests.Session()
    max_retry = 4
    while max_retry > 0:
        try:
            res = req.get('http://' + server_name + check_uri, verify=False)
            res.encoding = 'utf-8'
            data = res.json()
            status = status_code[data['status']]
            break
        except:
            max_retry -= 1
        time.sleep(1)
    if max_retry == 0:
        sys.stderr.write("\033[91mERROR: fail to get/parser response for uri=%s\033[0m" % (check_uri))
        return 'UNKNOWN'
    return status

def get_check_values(server_name, check_uri):
    # status code (https://docs.perfsonar.net/maddash_api_grids.html#status-codes)
    if "maddash" in check_uri:
        req = requests.Session()
        max_retry = 4
        while max_retry > 0:
            try:
                res = req.get('http://' + server_name + check_uri, verify=False)
                res.encoding = 'utf-8'
                data = res.json()
                for history in data['history']:
                    if not isinstance(history, dict):
                        continue
                    if "Average" in history['returnParams']:
                        value = history['returnParams']['Average']
                    else:
                        value = None
                    break
                break
            except:
                max_retry -= 1
            time.sleep(1)
        if max_retry == 0:
            sys.stderr.write("\033[91mERROR: fail to get/parser response for uri=%s\033[0m" % (check_uri))
            return None
    elif "esmond" in check_uri:
        req = requests.Session()
        max_retry = 4
        while max_retry > 0:
            try:
                url_full = 'http://' + server_name + '/esmond/perfsonar/archive/' + check_uri + '/histogram-owdelay/statistics/0?time-range=300&limit=1'
                res = req.get(url_full, verify=False)
                res.encoding = 'utf-8'
                esmond_data = res.json()
                if esmond_data:
                    for val in esmond_data:
                        value = str(val['val']['mean']).decode('utf8')
                        break
                else:
                    value = None
                break
            except:
                max_retry -= 1
            time.sleep(1)
        if max_retry == 0:
            sys.stderr.write("\033[91mERROR: fail to get/parser response for uri=%s\033[0m" % (check_uri))
            return None
    return value

def list_grids_esmond(server_name):
    # Documentation: https://docs.perfsonar.net/esmond_api_rest.html
    mapping = []
    req = requests.Session()
    res = req.get('http://' + server_name + '/esmond/perfsonar/archive/', verify=False)
    res.encoding = 'utf-8'
    data = res.json()
    current_time = time.time()
    for grid in data:
        time_since_last_update = 0
        if grid['pscheduler-test-type'] == "latencybg":
            for events in grid['event-types']:
                for test in events:
                    int(events['time-updated'])
                    time_since_last_update = int(current_time) - int(events['time-updated'])
                    break
                break
            # Check the time since last update. If it's more than one day, ignore it. 
            if not time_since_last_update > 86400:
                mapping.append({'{#SRC_DST}' : grid['source'] + '->' + grid['destination'],
                        '{#URI}' : grid['uri']})

    return mapping

parser = argparse.ArgumentParser(prog='maddash-api-wrapper',
                                usage='%(prog)s [options] ACTION',
                                description='Wrapper for MaDDash API')
parser.add_argument("-s", "--server-name", required=True,
                        help="ServerName for the MaDDash host")
actions = parser.add_mutually_exclusive_group(required=True)
actions.add_argument("-L", "--list-grids", action="store_true",
                        help="ACTION: List all grids")
actions.add_argument("-A", "--values-all-grids",
                        help="ACTION: Print status and values of checks in all grids. Possible values: 'all', 'throughput', 'loss', 'latency'")
actions.add_argument("-G", "--grid-uri",
                        help="ACTION: Print status of checks in a grid")
actions.add_argument("-C", "--check-status-uri",
                        help="ACTION: Print status of a specific check")
actions.add_argument("-V", "--check-values-uri",
                        help="ACTION: Print values of a specific check")

args = parser.parse_args()

#if args.list_grids:
#    grids = list_grids_esmond(args.server_name)
#    print '{"data":',json.dumps(grids),'}'

if args.list_grids:
    grids = list_grids(args.server_name)
    print '{"data":',json.dumps(grids),'}'
    #for grid in grids:
    #    print grid['{#NAME}'].replace(" ", "_"), grid['{#URI}']
elif args.grid_uri:
    cells = list_cells(args.server_name, args.grid_uri)
    print '[',json.dumps(cells),']'
    #for cell in cells:
    #    print cell
elif args.values_all_grids:
    option = args.values_all_grids
    possible_options = ['all', 'throughput', 'loss', 'latency']
    if option in possible_options:
        grids = list_grids(args.server_name)
        mapping = list_grids_esmond(args.server_name)
        cells = []
        for grid in grids:
            name = grid['{#NAME}']
            uri = grid['{#URI}']
            #print name,"\n","="*len(name)
            tests_info = list_cells(args.server_name, uri, mapping, option)
            if tests_info:
                cells += tests_info
            #for cell in cells:
            #    print cell
        print '{"data":',json.dumps(cells),'}'
    else:
        raise ValueError("Option not valid. Please use 'all', 'throughput', 'loss', or 'latency'")
elif args.check_status_uri:
    status = get_check_status(args.server_name, args.check_status_uri)
    print status
elif args.check_values_uri:
    value = get_check_values(args.server_name, args.check_values_uri)
    print value
else:
    parser.print_help()