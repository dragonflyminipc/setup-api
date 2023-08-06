#!/bin/bash

result=$(nmcli --get-values GENERAL.DEVICE,GENERAL.TYPE device show | sed '/^ethernet$/!{h;d;};x' | head -n 1)

echo "$result"
