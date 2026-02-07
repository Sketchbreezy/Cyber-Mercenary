// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title IEscrow - Escrow contract interface
interface IEscrow {
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

    function createBounty(
        string memory ipfsHash,
        uint256 expiresIn
    ) external payable;

    function submitReport(uint256 bountyId, bytes memory signature) external;

    function claimBounty(uint256 bountyId) external;

    function disputeBounty(uint256 bountyId) external;

    function getDeveloperBounties(
        address developer
    ) external view returns (Bounty[] memory);

    function bountyCount() external view returns (uint256);

    function bounties(uint256 id) external view returns (Bounty memory);
}
