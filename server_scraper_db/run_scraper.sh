#!/bin/bash

update_config() {
  cat <<EOF > config.json
{
    "api_key": "$1",
    "private_key": "$2",
    "category": "$3",
    "date_from": "$4",
    "date_until": "$5",
    "num_pdfs": $6,
    "download": $7
}
EOF
}

# Read parameters
API_KEY=$1
PRIVATE_KEY=$2
CATEGORY=$3
DATE_FROM=$4
DATE_UNTIL=$5
NUM_PDFS=$6
DOWNLOAD=$7

# Update the config file with the provided parameters
update_config "$API_KEY" "$PRIVATE_KEY" "$CATEGORY" "$DATE_FROM" "$DATE_UNTIL" "$NUM_PDFS" "$DOWNLOAD"

# Activate the virtual environment if needed
# Uncomment and modify the line below according to your virtual environment setup

source env/bin/activate

python3 scraper.py

deactivate
