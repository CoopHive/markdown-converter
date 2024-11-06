import json
from web3 import Web3
from postgres import PostgresDBManager
from dotenv import load_dotenv
import os

load_dotenv()


class TokenRewarder:
    def __init__(self, network='test_base', contract_address='0x14436f6895B8EC34e0E4994Df29D1856b665B490', contract_abi_path='CoopHiveV1.json'):
        if network == 'optimism':
            self.rpc_url = 'https://mainnet.optimism.io'
            self.chain_id = 10
        elif network == 'test_base':
            self.rpc_url = 'https://sepolia.base.org'
            self.chain_id = 84532
        elif network == 'base':
            self.rpc_url = 'https://mainnet.base.org'
            self.chain_id = 1234
        else:
            raise ValueError(
                "Unsupported network. Choose 'optimism' or 'base'.")

        contract_abi = self.load_contract_abi(contract_abi_path)['abi']

        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.contract_address = contract_address
        self.contract = self.web3.eth.contract(
            address=self.contract_address, abi=contract_abi)

        self.owner_address = os.getenv("OWNER_ADDRESS")
        self.private_key = os.getenv("PRIVATE_KEY")

        self.postgres_db_manager = PostgresDBManager(
            host="localhost", port=5432, user="vardhanshorewala", password="password")

        self.db_names = [
            "dvd_paragraph_marker_nvidia", "dvd_paragraph_llm_nvidia", "dvd_sentence_marker_nvidia", "dvd_sentence_llm_nvidia",
            "dvd_paragraph_marker_openai", "dvd_paragraph_llm_openai", "dvd_sentence_marker_openai", "dvd_sentence_llm_openai"
        ]

    def load_contract_abi(self, abi_path):
        with open(abi_path, 'r') as abi_file:
            return json.load(abi_file)

    def issue_token(self, recipient_address, amount=1):
        nonce = self.web3.eth.get_transaction_count(self.owner_address)
        txn = self.contract.functions.transfer(recipient_address, amount).build_transaction({
            'chainId': self.chain_id,
            'gas': 100000,
            'gasPrice': self.web3.to_wei('60', 'gwei'),
            'nonce': nonce,
        })

        signed_txn = self.web3.eth.account.sign_transaction(
            txn, private_key=self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(
            signed_txn.raw_transaction)
        print(f"Transaction sent. Hash: {self.web3.to_hex(tx_hash)}")

    def reward_unrewarded_users(self):
        for db_name in self.db_names:
            users_to_reward = self.postgres_db_manager.query(
                db_name=db_name,
                query_string="SELECT author FROM default_schema.papers WHERE rewarded = FALSE"
            )

            if users_to_reward:
                for user in users_to_reward:
                    recipient_address = user[0]
                    self.issue_token(recipient_address)

                    self.postgres_db_manager.query(
                        db_name=db_name,
                        query_string="UPDATE default_schema.papers SET rewarded = TRUE WHERE author = %s",
                        params=(recipient_address,)
                    )
            else:
                print(f"No users to reward in database: {db_name}")


if __name__ == "__main__":
    rewarder = TokenRewarder()
    rewarder.reward_unrewarded_users()
