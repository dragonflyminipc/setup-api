#!/bin/bash

sudo /usr/bin/create_ap -m bridge $(source /usr/local/bin/get_wifi_interface.sh) $(source /usr/local/bin/get_ethernet_interface.sh) $(source /usr/local/bin/get_hotspot_uuid.sh) dragonfly --freq-band 2.4
