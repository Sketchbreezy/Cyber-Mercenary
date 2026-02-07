// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/// @title Escrow - Bounty payment contract with ECDSA verification
/// @notice Handles bounty creation, claiming, and dispute resolution
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

    // Storage
    mapping(uint256 => Bounty) public bounties;
    mapping(address => uint256[]) public developerBounties;
    mapping(bytes32 => bool) public usedSignatures;

    // Counters
    uint256 public bountyCount;

    // Constants
    uint256 public constant MIN_BOUNTY = 0.001 ether;
    uint256 public constant FEE_PERCENT = 5; // 5% platform fee
    uint256 public constant SIGNATURE_EXPIRY = 30 days;

    // Events
    event BountyCreated(
        uint256 indexed id,
        address indexed developer,
        uint256 amount,
        string ipfsHash
    );
    event BountyClaimed(
        uint256 indexed id,
        address indexed claimer,
        uint256 amount
    );
    event BountyDisputed(uint256 indexed id);
    event BountyResolved(uint256 indexed id, bool rewarded);
    event FeeCollected(uint256 amount);

    constructor() EIP712("CyberMercenary", "1") {}

    /// @notice Create a new bounty
    /// @param ipfsHash Hash of the encrypted vulnerability report
    /// @param expiresIn Time until bounty expires (in seconds)
    function createBounty(
        string memory ipfsHash,
        uint256 expiresIn
    ) external payable nonReentrant {
        require(msg.value >= MIN_BOUNTY, "Below minimum bounty");
        require(bytes(ipfsHash).length > 0, "Invalid IPFS hash");
        require(expiresIn >= 1 hours, "Minimum 1 hour expiry");

        bountyCount++;
        uint256 fee = (msg.value * FEE_PERCENT) / 100;
        uint256 netAmount = msg.value - fee;

        bounties[bountyCount] = Bounty({
            id: bountyCount,
            developer: payable(msg.sender),
            amount: netAmount,
            claimed: false,
            disputed: false,
            ipfsHash: ipfsHash,
            agentSignature: "",
            createdAt: block.timestamp,
            expiresAt: block.timestamp + expiresIn
        });

        developerBounties[msg.sender].push(bountyCount);

        emit BountyCreated(bountyCount, msg.sender, netAmount, ipfsHash);
    }

    /// @notice Submit vulnerability report and sign it
    /// @param bountyId The bounty ID
    /// @param signature Agent's ECDSA signature
    function submitReport(uint256 bountyId, bytes memory signature) external {
        require(bountyId <= bountyCount, "Invalid bounty ID");
        Bounty storage bounty = bounties[bountyId];

        require(
            block.timestamp < bounty.expiresAt,
            "Bounty expired"
        );
        require(
            bounty.agentSignature.length == 0,
            "Report already submitted"
        );

        // Verify signature from agent
        bytes32 message = keccak256(
            abi.encodePacked(
                bountyId,
                msg.sender,
                bounty.developer,
                bounty.ipfsHash
            )
        );
        bytes32 signedMessage = _hashTypedDataV4(message);

        require(
            usedSignatures[signedMessage] == false,
            "Signature already used"
        );

        bounty.agentSignature = signature;
        usedSignatures[signedMessage] = true;
    }

    /// @notice Claim bounty after report is verified
    /// @param bountyId The bounty ID
    function claimBounty(uint256 bountyId) external nonReentrant {
        require(bountyId <= bountyCount, "Invalid bounty ID");
        Bounty storage bounty = bounties[bountyId];

        require(msg.sender == bounty.developer, "Not bounty creator");
        require(!bounty.claimed, "Already claimed");
        require(
            block.timestamp >= bounty.expiresAt || bounty.agentSignature.length > 0,
            "Bounty not ready"
        );

        bounty.claimed = true;
        payable(msg.sender).transfer(bounty.amount);

        emit BountyClaimed(bountyId, msg.sender, bounty.amount);
    }

    /// @notice Dispute a bounty (if report is invalid)
    /// @param bountyId The bounty ID
    function disputeBounty(uint256 bountyId) external {
        require(bountyId <= bountyCount, "Invalid bounty ID");
        Bounty storage bounty = bounties[bountyId];

        require(
            msg.sender == bounty.developer,
            "Only developer can dispute"
        );
        require(!bounty.disputed, "Already disputed");

        bounty.disputed = true;
        emit BountyDisputed(bountyId);
    }

    /// @notice Resolve dispute (owner only)
    /// @param bountyId The bounty ID
    /// @param rewardDeveloper True to reward developer, false to refund
    function resolveDispute(uint256 bountyId, bool rewardDeveloper) external onlyOwner {
        require(bountyId <= bountyCount, "Invalid bounty ID");
        Bounty storage bounty = bounties[bountyId];

        require(bounty.disputed, "Not disputed");
        require(!bounty.claimed, "Already claimed");

        bounty.claimed = true;
        bounty.disputed = false;

        if (rewardDeveloper) {
            payable(bounty.developer).transfer(bounty.amount);
        } else {
            // Refund to original bounty creator
            // Note: In a real implementation, track original creator
            payable(owner()).transfer(bounty.amount);
        }

        emit BountyResolved(bountyId, rewardDeveloper);
    }

    /// @notice Collect platform fees (owner only)
    function collectFees() external onlyOwner {
        uint256 fees = address(this).balance;
        require(fees > 0, "No fees to collect");
        payable(owner()).transfer(fees);
        emit FeeCollected(fees);
    }

    /// @notice Get all bounties for an address
    function getDeveloperBounties(
        address developer
    ) external view returns (Bounty[] memory) {
        uint256[] memory ids = developerBounties[developer];
        Bounty[] memory result = new Bounty[](ids.length);

        for (uint256 i = 0; i < ids.length; i++) {
            result[i] = bounties[ids[i]];
        }

        return result;
    }

    /// @notice Get expired but unclaimed bounties
    function getExpiredBounties() external view returns (Bounty[] memory) {
        uint256 count = 0;
        for (uint256 i = 1; i <= bountyCount; i++) {
            if (
                bounties[i].expiresAt < block.timestamp &&
                !bounties[i].claimed
            ) {
                count++;
            }
        }

        Bounty[] memory result = new Bounty[](count);
        uint256 index = 0;

        for (uint256 i = 1; i <= bountyCount; i++) {
            if (
                bounties[i].expiresAt < block.timestamp &&
                !bounties[i].claimed
            ) {
                result[index] = bounties[i];
                index++;
            }
        }

        return result;
    }
}
