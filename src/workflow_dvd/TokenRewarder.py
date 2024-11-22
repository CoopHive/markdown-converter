import json
import itertools
from web3 import Web3
from dotenv import load_dotenv
import os
import time
from psycopg2 import sql, connect

load_dotenv()


class TokenRewarder:
    def __init__(self, network='test_base', contract_address='0x14436f6895B8EC34e0E4994Df29D1856b665B490',
                 contract_abi_path='../contracts/CoopHiveV1.json', db_components=None,
                 host="localhost", port=5432, user="", password=""):
        """Initializes the TokenRewarder class and sets up blockchain and database connections."""
        self._initialize_network(network)
        contract_abi = self.load_contract_abi(contract_abi_path)['abi']

        # Initialize Web3 and contract
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))
        self.contract_address = contract_address
        self.contract = self.web3.eth.contract(
            address=self.contract_address, abi=contract_abi)

        # Blockchain credentials from environment variables
        self.owner_address = os.getenv("OWNER_ADDRESS")
        self.private_key = os.getenv("PRIVATE_KEY")

        # Store PostgreSQL connection details
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        # Generate database names and initialize reward tables
        if db_components:
            self.db_names = self.generate_db_names(db_components)
            self._initialize_reward_tables()
        else:
            self.db_names = []

    def _initialize_network(self, network):
        """Sets the RPC URL and chain ID based on the specified network."""
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
                "Unsupported network. Choose 'optimism', 'test_base', or 'base'.")

    def _connect(self, dbname='postgres'):
        """Establishes a connection to the specified PostgreSQL database."""
        try:
            conn = connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=dbname
            )
            conn.autocommit = True
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None

    def load_contract_abi(self, abi_path):
        """Loads the contract ABI from the given path."""
        with open(abi_path, 'r') as abi_file:
            return json.load(abi_file)

    def generate_db_names(self, components):
        """Generates database names using Cartesian product of components."""
        return [
            f"{c}_{ch}_{e}_token"
            for c, ch, e in itertools.product(
                components['converter'], components['chunker'], components['embedder']
            )
        ]

    def _initialize_reward_tables(self):
        """Creates reward tables in all generated databases."""
        for db_name in self.db_names:
            self._create_database_and_table(db_name)

    def _create_database_and_table(self, db_name):
        """Creates the database and initializes the reward table."""
        conn = self._connect()
        if conn is None:
            print("Unable to connect to PostgreSQL server.")
            return

        cursor = conn.cursor()
        try:
            # Check if the database exists
            cursor.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [
                    db_name]
            )
            if not cursor.fetchone():
                # Create the new database
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_name)))
                print(f"Database '{db_name}' created successfully.")

            # Ensure schema and table are created in the new database
            self._create_schema_and_table(db_name)

        except Exception as e:
            print(f"Error creating database or table: {e}")
        finally:
            cursor.close()
            conn.close()

    def _create_schema_and_table(self, db_name):
        """Creates the schema and 'user_rewards' table in the given database, if they don't already exist."""
        conn = self._connect(db_name)
        if conn is None:
            print(f"Unable to connect to the database '{db_name}'.")
            return

        cursor = conn.cursor()
        try:
            # Create schema if it doesn't exist
            cursor.execute("CREATE SCHEMA IF NOT EXISTS default_schema")

            # Check if 'user_rewards' table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'default_schema' 
                    AND table_name = 'user_rewards'
                )
            """)
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                # Create the 'user_rewards' table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE default_schema.user_rewards (
                        public_key TEXT PRIMARY KEY,
                        job_count INT DEFAULT 0,
                        token_balance INT DEFAULT 0
                    )
                """)
                print(f"Initialized 'user_rewards' table in '{db_name}'.")
            else:
                print(
                    f"'user_rewards' table already exists in '{db_name}', skipping creation.")

        except Exception as e:
            print(f"Error creating schema or table: {e}")
        finally:
            cursor.close()
            conn.close()

    def add_reward_to_user(self, public_key, db_name):
        db_name = f"{db_name}_token"
        """Increments the job count for a user or adds them if they don't exist."""
        conn = self._connect(db_name)
        if conn is None:
            print(f"Unable to connect to the database '{db_name}'.")
            return

        cursor = conn.cursor()
        try:
            # Check if the user exists
            cursor.execute(
                "SELECT job_count FROM default_schema.user_rewards WHERE public_key = %s",
                (public_key,)
            )
            result = cursor.fetchone()

            if result is None:
                # Insert a new user if not found
                cursor.execute(
                    """
                    INSERT INTO default_schema.user_rewards (public_key, job_count, token_balance)
                    VALUES (%s, %s, %s)
                    """, (public_key, 1, 0)
                )
                print(f"User '{public_key}' added with job_count 1.")
            else:
                # Increment the user's job count
                new_job_count = result[0] + 1
                cursor.execute(
                    "UPDATE default_schema.user_rewards SET job_count = %s WHERE public_key = %s",
                    (new_job_count, public_key)
                )
                print(
                    f"User '{public_key}' job_count incremented to {new_job_count}.")

        except Exception as e:
            print(f"Error updating job count: {e}")
        finally:
            cursor.close()
            conn.close()

    def issue_token(self, recipient_address, job_count=1):
        """Issues tokens to the recipient address."""
        try:
            nonce = self.web3.eth.get_transaction_count(
                self.owner_address, 'pending')

            txn = self.contract.functions.transfer(
                recipient_address, job_count
            ).build_transaction({
                'chainId': self.chain_id,
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce,
            })

            signed_txn = self.web3.eth.account.sign_transaction(
                txn, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(
                signed_txn.raw_transaction)
            print(f"Transaction sent: {self.web3.to_hex(tx_hash)}")
            return True

        except Exception as e:
            print(f"Error sending transaction: {e}")
            return False

    def reward_users(self):
        """Rewards users and resets their job counts."""
        print("Rewarding users...")
        for db_name in self.db_names:
            conn = self._connect(db_name)
            if conn is None:
                print(f"Unable to connect to '{db_name}'.")
                continue

            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT public_key, job_count FROM default_schema.user_rewards WHERE job_count > 0"
                )
                users = cursor.fetchall()

                for public_key, job_count in users:
                    time.sleep(4)
                    if self.issue_token(public_key, job_count):
                        cursor.execute(
                            """
                            UPDATE default_schema.user_rewards 
                            SET job_count = 0, token_balance = token_balance + %s 
                            WHERE public_key = %s
                            """, (job_count, public_key)
                        )
                        print(
                            f"Rewarded {job_count} tokens to '{public_key}'.")

            except Exception as e:
                print(f"Error rewarding users: {e}")
            finally:
                cursor.close()
                conn.close()
