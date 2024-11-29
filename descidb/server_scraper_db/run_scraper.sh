#!/bin/bash

update_config() {
  cat <<EOF > config.json
{
    "api_key": "$1",
    "category": "$2",
    "date_from": "$3",
    "date_until": "$4",
    "num_pdfs": $5,
    "download": $6
}
EOF
}

# Read parameters
API_KEY=$1
CATEGORY=$2
DATE_FROM=$3
DATE_UNTIL=$4
NUM_PDFS=$5
DOWNLOAD=$6

# Update the config file with the provided parameters
update_config "$API_KEY" "$CATEGORY" "$DATE_FROM" "$DATE_UNTIL" "$NUM_PDFS" "$DOWNLOAD"

# Activate the virtual environment if needed
# Uncomment and modify the line below according to your virtual environment setup

# source env/bin/activate

python3 scraper.py

# Deactivate the virtual environment if needed
# Uncomment the line below if you activated a virtual environment above

# deactivate