#!/bin/bash

# Full path to the script directory
SCRIPT_DIR="/Users/vardhanshorewala/Desktop/coophive/markdown-converter/workflow_dvd"
cd "$SCRIPT_DIR"

echo "Cron job started at $(date)" >> "$SCRIPT_DIR/cron_debug.log"

/usr/local/bin/python3 "$SCRIPT_DIR/TokenScheduler.py" >> "$SCRIPT_DIR/reward_users.log" 2>> "$SCRIPT_DIR/cron_debug.log"

echo "Cron job completed at $(date)" >> "$SCRIPT_DIR/cron_debug.log"
