#!/bin/bash

first_uuid=$(find /dev/disk/by-uuid/ -type l -printf '%f\n' | head -n 1)
hash=$(echo -n "$first_uuid" | sha1sum)

uuid="${hash:0:8}"
echo "eqpayminer_$uuid"
