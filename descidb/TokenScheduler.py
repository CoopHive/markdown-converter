from TokenRewarder import TokenRewarder

def run_reward_users():
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

    rewarder = TokenRewarder(
        network='test_base',
        contract_address='0x14436f6895B8EC34e0E4994Df29D1856b665B490',
        contract_abi_path='../contracts/CoopHiveV1.json',
        db_components=components,
        host="localhost",
        port=5432,
        user="vardhanshorewala",
        password="password"
    )

    rewarder.reward_users()


if __name__ == "__main__":
    run_reward_users()
