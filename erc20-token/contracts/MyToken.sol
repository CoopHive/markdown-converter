// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title MyToken
 * @dev A standard ERC20 token with mint and burn functions.
 * The contract is Ownable, meaning only the owner can mint new tokens.
 */
contract MyToken is ERC20, Ownable {
    uint8 private _decimals;

    /**
     * @dev Constructor that initializes the token with a name, symbol,
     * decimals, and initial supply.
     * @param name_ Name of the token
     * @param symbol_ Symbol of the token
     * @param decimals_ Number of decimals for the token
     * @param initialSupply Initial supply of tokens to mint
     * @param initialOwner Address that will be the owner of the contract
     */
    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        uint256 initialSupply,
        address initialOwner
    ) ERC20(name_, symbol_) Ownable(initialOwner) {
        _decimals = decimals_;

        // Mint initial supply to the contract owner
        if (initialSupply > 0) {
            _mint(initialOwner, initialSupply * (10 ** decimals_));
        }
    }

    /**
     * @dev Returns the number of decimals used for token.
     */
    function decimals() public view virtual override returns (uint8) {
        return _decimals;
    }

    /**
     * @dev Mints new tokens. Can only be called by the contract owner.
     * @param to Address to mint tokens to
     * @param amount Amount of tokens to mint
     */
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }

    /**
     * @dev Burns tokens from the caller's balance.
     * @param amount Amount of tokens to burn
     */
    function burn(uint256 amount) public {
        _burn(_msgSender(), amount);
    }

    /**
     * @dev Burns tokens from a specified account if the caller is allowed.
     * @param account Address to burn tokens from
     * @param amount Amount of tokens to burn
     */
    function burnFrom(address account, uint256 amount) public {
        _spendAllowance(account, _msgSender(), amount);
        _burn(account, amount);
    }

    /**
     * @dev Distributes tokens to multiple addresses at once according to the provided mapping.
     * Can only be called by the contract owner.
     * @param recipients Array of recipient addresses
     * @param amounts Array of token amounts to distribute (must have the same length as recipients)
     */
    function batchDistribute(
        address[] calldata recipients,
        uint256[] calldata amounts
    ) public onlyOwner {
        require(
            recipients.length == amounts.length,
            "Recipients and amounts arrays must have the same length"
        );
        require(recipients.length > 0, "Recipients array cannot be empty");

        for (uint256 i = 0; i < recipients.length; i++) {
            require(
                recipients[i] != address(0),
                "Cannot distribute to the zero address"
            );
            _mint(recipients[i], amounts[i]);
        }
    }
}
