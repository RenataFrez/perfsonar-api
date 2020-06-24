#!/usr/bin/env python

"""
    This code is the Perfsonar MaDDash Wrapper
    Author: Italo Valcy <italovalcy@gmail.com>
"""

import argparse
import requests
import urllib3
import json
import sys
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

def list_cells(server_name, grid_uri):
    # status code (https://docs.perfsonar.net/maddash_api_grids.html#status-codes)
    status_code = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'PENDING', 'DOWN']
    cells = []
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
    # grid[n]	    2-dimenional array	A row in the grid
    # grid[n][m]    2-dimenional array	A cell in the grid. If null then no checks are configured for this cell.
    # grid[n][m][l] array or objects	A check in the grid
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
                    try:
                        status = status_code[cel['status']]
                    except:
                        status = 'UNKNOWN'
                    message = str(cel['message']).lstrip().rstrip()
                    cells.append({'{#NAME}': data['name'],
                                '{#SRC_DST}' : uri_l[-3] + '->' + uri_l[-2],
                                '{#URI}' : str(cel['uri']),
                                '{#STATUS}': status,
                                '{#MESSAGE}': message})
    return cells


def get_check_status(server_name, check_uri):
    # status code (https://docs.perfsonar.net/maddash_api_grids.html#status-codes)
    status_code = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'PENDING', 'DOWN']
    req = requests.Session()
    try:
        res = req.get('http://' + server_name + check_uri, verify=False)
        res.encoding = 'utf-8'
        data = res.json()
        status = status_code[data['status']]
    except:
        sys.stderr.write("\033[91mERROR: fail to get/parser response for uri=%s\033[0m" % (check_uri))
        return 'UNKNOWN'
    return status

parser = argparse.ArgumentParser(prog='maddash-api-wrapper',
                                usage='%(prog)s [options] ACTION',
                                description='Wrapper for MaDDash API')
parser.add_argument("-s", "--server-name", required=True,
                        help="ServerName for the MaDDash host")
actions = parser.add_mutually_exclusive_group(required=True)
actions.add_argument("-L", "--list-grids", action="store_true",
                        help="ACTION: List all grids")
actions.add_argument("-A", "--status-all-grids", action="store_true",
                        help="ACTION: Print status of checks in all grids")
actions.add_argument("-G", "--grid-uri",
                        help="ACTION: Print status of checks in a grid")
actions.add_argument("-C", "--check-uri",
                        help="ACTION: Print status of a specific check")

args = parser.parse_args()
if args.list_grids:
    grids = list_grids(args.server_name)
    print '{"data":',json.dumps(grids),'}'
elif args.grid_uri:
    cells = list_cells(args.server_name, args.grid_uri)
    print '[',json.dumps(cells),']'
elif args.status_all_grids:
    grids = list_grids(args.server_name)
    cells = []
    for grid in grids:
        name = grid['{#NAME}']
        uri = grid['{#URI}']
        cells += list_cells(args.server_name, uri)
    print '{"data":',json.dumps(cells),'}'
elif args.check_uri:
    status = get_check_status(args.server_name, args.check_uri)
    print status
else:
    parser.print_help()
