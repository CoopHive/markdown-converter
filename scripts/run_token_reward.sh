#!/bin/bash
# run_token_rewarder.sh
# DESCRIPTION: Calculate contributor stats and batch‑distribute CoopHive ERC‑20 tokens

set -e

echo "Running DeSciDB token reward test..."
poetry run python -m descidb.rewards.token_reward_main -v