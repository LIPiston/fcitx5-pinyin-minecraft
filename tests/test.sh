#!/bin/bash
# Build from a checked-in title list so the fetch step is skipped.
cp tests/blob/titles.txt mc-titles-cn.txt
make minecraft-cn.dict
