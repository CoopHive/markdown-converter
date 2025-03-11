# MyToken ERC20 Contract

This repository contains a standard ERC20 token implementation built with Solidity and using OpenZeppelin contracts.

## Features

- Standard ERC20 functionality (transfer, approve, transferFrom)
- Custom token name, symbol, and decimals
- Mintable - new tokens can be created by the contract owner
- Burnable - token holders can burn their tokens
- Batch distribution - distribute tokens to multiple addresses in one transaction
- Base testnet deployment support
- Fully compliant with the ERC20 standard
- Well-documented with NatSpec comments

## Requirements

- Solidity ^0.8.20
- OpenZeppelin Contracts

## Installation

### Using Hardhat

1. Initialize a new Hardhat project if you haven't already:

   ```bash
   npm install --save-dev hardhat
   npx hardhat init
   ```

2. Install OpenZeppelin contracts:

   ```bash
   npm install @openzeppelin/contracts
   ```

3. Place the `MyToken.sol` file in your contracts directory.

### Using Truffle

1. Initialize a new Truffle project if you haven't already:

   ```bash
   npm install -g truffle
   truffle init
   ```

2. Install OpenZeppelin contracts:

   ```bash
   npm install @openzeppelin/contracts
   ```

3. Place the `MyToken.sol` file in your contracts directory.

### Using Remix

1. Open [Remix IDE](https://remix.ethereum.org)
2. Create a new file with the content of `MyToken.sol`
3. Make sure to have OpenZeppelin contracts installed via Remix plugin manager or by importing from GitHub URLs

## Contract Usage

The contract constructor takes the following parameters:

- `name_`: The name of your token (e.g., "My Token")
- `symbol_`: The symbol/ticker of your token (e.g., "MTK")
- `decimals_`: The number of decimal places (typically 18 for most tokens)
- `initialSupply`: The initial amount of tokens to mint (in whole tokens)
- `initialOwner`: The address that will own the contract and have minting privileges

### Functions

#### Standard ERC20 Functions

- `transfer(to, amount)`: Transfer tokens to another address
- `approve(spender, amount)`: Approve another address to spend tokens
- `transferFrom(from, to, amount)`: Transfer tokens from one address to another
- `balanceOf(account)`: Get the token balance of an account
- `allowance(owner, spender)`: Get the remaining allowance for a spender

#### Custom Functions

- `mint(to, amount)`: Mint new tokens to an address (owner only)
- `burn(amount)`: Burn tokens from your own balance
- `burnFrom(account, amount)`: Burn tokens from another account (requires approval)
- `batchDistribute(recipients, amounts)`: Distribute tokens to multiple addresses in one transaction (owner only)

### Deployment Example

Using Hardhat:

```javascript
const MyToken = await ethers.getContractFactory("MyToken");
const myToken = await MyToken.deploy(
  "My Token", // name
  "MTK", // symbol
  18, // decimals
  1000000, // initial supply (1 million tokens)
  "0xYourAddress" // initial owner
);
await myToken.deployed();
```

### Deploying to Base Testnet

1. Set up your `.env` file with your private key and API keys:

   ```
   PRIVATE_KEY=your_private_key_here
   BASESCAN_API_KEY=your_basescan_api_key_here
   ```

2. Run deployment command:

   ```bash
   npm run deploy:base-sepolia
   ```

3. Verify contract (optional):
   ```bash
   npm run verify:base-sepolia YOUR_CONTRACT_ADDRESS "My Token" "MTK" 18 1000000 "0xYourAddress"
   ```

### Batch Token Distribution Example

To distribute tokens to multiple addresses in one transaction:

```javascript
// Define recipients and amounts
const recipients = [
  "0x1111111111111111111111111111111111111111",
  "0x2222222222222222222222222222222222222222",
  "0x3333333333333333333333333333333333333333",
];

const amounts = [
  ethers.utils.parseUnits("1000", 18), // 1,000 tokens to first address
  ethers.utils.parseUnits("2000", 18), // 2,000 tokens to second address
  ethers.utils.parseUnits("3000", 18), // 3,000 tokens to third address
];

// Execute batch distribution (must be called by contract owner)
await myToken.batchDistribute(recipients, amounts);
```

## License

This project is licensed under the MIT License.
