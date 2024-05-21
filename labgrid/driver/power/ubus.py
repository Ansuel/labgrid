""" UBUS jsonrpc interface for PoE management on OpenWrt devices. This comes in
    handy if devices are connected to a PoE switch running OpenWrt. Author: Paul
    Spooren <mail@aparcar.org>

    The URL given in hosts in exporter.yaml must accept unauthenticated UBUS
    calls for the two `poe` calls `info` and `manage`.

    An ACL example is given below:

    root@switch:~# cat /usr/share/rpcd/acl.d/unauthenticated.json 
    {
        "unauthenticated": {
            "description": "Access controls for unauthenticated requests",
            "read": {
                "ubus": {
                    "session": [
                        "access",
                        "login"
                    ],
                    "poe": [
                        "info",
                        "manage"
                    ]
                }
            }
        }
    }

    Further information is availbe at https://openwrt.org/docs/techref/ubus#acls

  NetworkPowerPort:
      model: ubus
      host: 'http://192.168.1.1/ubus'
      index: 1
"""

import requests


def jsonrpc_call(host, path, method, message):
    r = requests.post(
        host,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "call",
            "params": ["00000000000000000000000000000000", path, method, message],
        },
    )
    r.raise_for_status()
    return r.json()["result"][1]


def power_set(host, port, index, value):
    assert port is None

    jsonrpc_call(host, "poe", "manage", {"port": f"lan{index}", "enable": value == 1})


def power_get(host, port, index):
    assert port is None

    poe_info = jsonrpc_call(host, "poe", "info", {})

    assert (
        f"lan{index}" in poe_info["ports"]
    ), f"Port lan{index} not found in {poe_info['result'][1]['ports']}"

    return poe_info["ports"][f"lan{index}"] != "Disabled"
