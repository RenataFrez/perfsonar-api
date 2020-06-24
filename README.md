perfSonar API
=============

This repository contains a python wrapper script to perfsonar MadDash API and some integration tools, such as a Zabbix Template for Perfsonar.

Personar MA wrapper
===================

Perfsonar Maddash (Monitoring and Debugging Dashboard) aims to collect and present two-dimensional monitoring data as a set of grids referred to as a dashboard. These measurement results can be accessed using a REST API, as documented at <https://docs.perfsonar.net/maddash_api_intro.html>.

You can use this script to query the status of a Dashboard on Perfsonar, to query specific tests, or even to check the status of a grid. Example:

.. code-block :: RST

    $ ./maddash-api_wrapper.py -s dashboard.ampath.net -L | python -m json.tool
    {
        "data": [
            {
                "{#NAME}": "AmLight Backbone: rtt - MIA - BCT - SPO (Monet - 100 Gbps) - Ping Loss",
                "{#URI}": "/maddash/grids/AmLight+Backbone%3A+rtt+-+MIA+-+BCT+-+SPO+%28Monet+-+100+Gbps%29+-+Ping+Loss"
            },
            {
                "{#NAME}": "RubinObs-LS: Huechuraba to La Serena - BW: Huechuraba - La Serena (10 Gbps) - Throughput",
                "{#URI}": "/maddash/grids/RubinObs-LS%3A+Huechuraba+to+La+Serena+-+BW%3A+Huechuraba+-+La+Serena+%2810+Gbps%29+-+Throughput"
            },
            {
                "{#NAME}": "RubinObs-LS: Huechuraba to La Serena - Latency: Huechuraba - La Serena - Loss",
                "{#URI}": "/maddash/grids/RubinObs-LS%3A+Huechuraba+to+La+Serena+-+Latency%3A+Huechuraba+-+La+Serena+-+Loss"
            },
            ...
            {
                "{#NAME}": "RubinObs-LS: Huechuraba to La Serena - RTT: Huechuraba - La Serena - Ping Loss",
                "{#URI}": "/maddash/grids/RubinObs-LS%3A+Huechuraba+to+La+Serena+-+RTT%3A+Huechuraba+-+La+Serena+-+Ping+Loss"
            }
        ]
    }
    $ ./maddash-api_wrapper.py -s dashboard.ampath.net -G "/maddash/grids/RubinObs-LS%3A+Huechuraba+to+La+Serena+-+RTT%3A+Huechuraba+-+La+Serena+-+Ping+Loss" | python -m json.tool
    [
        [
            {
                "{#MESSAGE}": "Average loss is 0.00%",
                "{#NAME}": "RubinObs-LS: Huechuraba to La Serena - RTT: Huechuraba - La Serena - Ping Loss",
                "{#SRC_DST}": "10.7.27.1->10.7.27.2",
                "{#STATUS}": "OK",
                "{#URI}": "/maddash/grids/RubinObs-LS:+Huechuraba+to+La+Serena+-+RTT:+Huechuraba+-+La+Serena+-+Ping+Loss/10.7.27.1/10.7.27.2/Loss"
            },
            {
                "{#MESSAGE}": "Average loss is 0.00%",
                "{#NAME}": "RubinObs-LS: Huechuraba to La Serena - RTT: Huechuraba - La Serena - Ping Loss",
                "{#SRC_DST}": "10.7.27.2->10.7.27.1",
                "{#STATUS}": "OK",
                "{#URI}": "/maddash/grids/RubinObs-LS:+Huechuraba+to+La+Serena+-+RTT:+Huechuraba+-+La+Serena+-+Ping+Loss/10.7.27.2/10.7.27.1/Loss"
            }
        ]
    ]
    $ ./maddash-api_wrapper.py -s dashboard.ampath.net -C "/maddash/grids/RubinObs-LS:+Huechuraba+to+La+Serena+-+RTT:+Huechuraba+-+La+Serena+-+Ping+Loss/10.7.27.1/10.7.27.2/Loss"
    OK

Zabbix integration
==================

Zabbix monitoring server allows you to create Templates and LLD (Low Level Discovery) to dynamiclly discovery and monitor your network. The template `zbx_tmpl_perfsonar_maddash_rest_api.xml` shows how to create LLD and monitor the measurement test results from Perfsonar Maddash.
