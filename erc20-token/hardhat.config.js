/**
 * @type import('hardhat/config').HardhatUserConfig
 */
require('@nomiclabs/hardhat-waffle');
require('@nomiclabs/hardhat-ethers');
require('@nomiclabs/hardhat-etherscan');
require('dotenv').config();

// Optional: Load environment variables from .env file
// Example .env file:
// PRIVATE_KEY=your_private_key
// ETHERSCAN_API_KEY=your_etherscan_api_key
// INFURA_API_KEY=your_infura_api_key
// BASESCAN_API_KEY=your_basescan_api_key

const PRIVATE_KEY = process.env.PRIVATE_KEY || "0000000000000000000000000000000000000000000000000000000000000000";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";
const INFURA_API_KEY = process.env.INFURA_API_KEY || "";
const BASESCAN_API_KEY = process.env.BASESCAN_API_KEY || "";

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    hardhat: {
      chainId: 1337
    },
    localhost: {
      url: "http://127.0.0.1:8545",
    },
    // Base Testnet (Sepolia)
    "base-sepolia": {
      url: "https://sepolia.base.org",
      accounts: [PRIVATE_KEY],
      gasPrice: "auto",
      chainId: 84532,
    }
  },
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  }
}; 