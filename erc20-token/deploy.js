// Script for deploying the MyToken contract using Hardhat
// Run with: npx hardhat run scripts/deploy.js --network <network_name>

async function main() {
  const [deployer] = await ethers.getSigners();
  
  console.log("Deploying contracts with the account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());
  
  // Deploy MyToken contract
  const MyToken = await ethers.getContractFactory("MyToken");
  
  // Configure your token parameters here
  const tokenName = "My Token";
  const tokenSymbol = "MTK";
  const tokenDecimals = 18;
  const initialSupply = 1000000; // 1 million tokens
  const ownerAddress = deployer.address;
  
  const token = await MyToken.deploy(
    tokenName,
    tokenSymbol,
    tokenDecimals,
    initialSupply,
    ownerAddress
  );
  
  await token.deployed();
  
  console.log("Token deployed to:", token.address);
  console.log("Token name:", await token.name());
  console.log("Token symbol:", await token.symbol());
  console.log("Token decimals:", await token.decimals());
  console.log("Token total supply:", (await token.totalSupply()).toString());
  console.log("Deployer balance:", (await token.balanceOf(deployer.address)).toString());
  
  // Example of using the batchDistribute function
  // Uncomment the following code to distribute tokens after deployment
  // Note: You'll need to adjust these addresses and amounts for your use case
  /*
  console.log("Distributing tokens to multiple addresses...");
  
  // Example addresses - replace with real addresses
  const recipients = [
    "0x1111111111111111111111111111111111111111",
    "0x2222222222222222222222222222222222222222",
    "0x3333333333333333333333333333333333333333"
  ];
  
  // Amounts in wei (considering decimals)
  const amounts = [
    ethers.utils.parseUnits("1000", tokenDecimals),  // 1,000 tokens to first address
    ethers.utils.parseUnits("2000", tokenDecimals),  // 2,000 tokens to second address
    ethers.utils.parseUnits("3000", tokenDecimals)   // 3,000 tokens to third address
  ];
  
  // Distribute tokens
  const tx = await token.batchDistribute(recipients, amounts);
  await tx.wait();
  
  console.log("Token distribution completed!");
  
  // Verify balances
  for (let i = 0; i < recipients.length; i++) {
    const balance = await token.balanceOf(recipients[i]);
    console.log(`Address ${recipients[i]} balance: ${ethers.utils.formatUnits(balance, tokenDecimals)}`);
  }
  */
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 