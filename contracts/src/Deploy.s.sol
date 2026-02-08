// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/// @title Escrow - Bounty payment contract
contract Escrow is Ownable, ReentrancyGuard, EIP712 {
    using ECDSA for bytes32;

    struct Bounty {
        uint256 id;
        address payable developer;
        uint256 amount;
        bool claimed;
        bool disputed;
        string ipfsHash;
        bytes agentSignature;
        uint256 createdAt;
        uint256 expiresAt;
    }

    mapping(uint256 => Bounty) public bounties;
    mapping(address => uint256[]) public developerBounties;
    uint256 public bountyCount;
    uint256 public constant MIN_BOUNTY = 0.001 ether;
    uint256 public constant FEE_PERCENT = 5;

    event BountyCreated(uint256 indexed id, address indexed developer, uint256 amount, string ipfsHash);
    event BountyClaimed(uint256 indexed id, address indexed claimer, uint256 amount);

    constructor() Ownable(msg.sender) EIP712("CyberMercenary", "1") {}

    function createBounty(string memory ipfsHash, uint256 expiresIn) external payable {
        require(msg.value >= MIN_BOUNTY, "Below minimum bounty");
        bountyCount++;
        uint256 netAmount = msg.value - (msg.value * FEE_PERCENT / 100);
        bounties[bountyCount] = Bounty(bountyCount, payable(msg.sender), netAmount, false, false, ipfsHash, "", block.timestamp, block.timestamp + expiresIn);
        emit BountyCreated(bountyCount, msg.sender, netAmount, ipfsHash);
    }

    function claimBounty(uint256 bountyId) external {
        Bounty storage b = bounties[bountyId];
        require(msg.sender == b.developer && !b.claimed, "Not authorized");
        b.claimed = true;
        payable(msg.sender).transfer(b.amount);
        emit BountyClaimed(bountyId, msg.sender, b.amount);
    }
}

/// @title DeployEscrow - Deployment script
contract DeployEscrow is Script {
    function run() external {
        vm.startBroadcast();
        Escrow escrow = new Escrow();
        console.log("Escrow deployed at:");
        console.logAddress(address(escrow));
        vm.stopBroadcast();
    }
}
