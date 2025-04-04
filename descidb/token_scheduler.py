"""
Token scheduling module for DeSciDB.

This module provides functionality to schedule token rewards for users based on
their contributions to the DeSciDB ecosystem.
"""

from descidb.token_rewarder import TokenRewarder
from pathlib import Path


def run_reward_users():
    """
    Run the token reward process for users across different database configurations.

    This function initializes the TokenRewarder with different database configurations
    and processes rewards for users in each database.
    """
    databases = [
        {
            "converter": "openai",
            "chunker": "sentence",
            "embedder": "openai"
        },
        {
            "converter": "openai",
            "chunker": "paragraph",
            "embedder": "openai"
        }
    ]

    components = {
        "converter": list(set([db_config["converter"] for db_config in databases])),
        "chunker": list(set([db_config["chunker"] for db_config in databases])),
        "embedder": list(set([db_config["embedder"] for db_config in databases]))
    }

    # Get project root directory
    project_root = Path(__file__).parent.parent
    contract_abi_path = project_root / "contracts" / "CoopHiveV1.json"

    rewarder = TokenRewarder(
        network='test_base',
        contract_address='0x14436f6895B8EC34e0E4994Df29D1856b665B490',
        contract_abi_path=str(contract_abi_path),
        db_components=components,
        host="localhost",
        port=5432,
        user="vardhanshorewala",
        password="password"
    )

    for component in components:
        component += '_token'
        rewarder.get_user_rewards(component)


if __name__ == "__main__":
    run_reward_users()
