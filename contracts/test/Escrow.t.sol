// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test, console2} from "forge-std/Test.sol";
import {Escrow} from "../src/Escrow.sol";

/// @title Escrow Contract Tests
/// @notice Tests for the bounty escrow contract
contract EscrowTest is Test {
    Escrow public escrow;
    address public owner;
    address public developer;
    address public agent;
    address public attacker;

    // Test constants
    uint256 public constant MIN_BOUNTY = 0.001 ether;
    uint256 public constant FEE_PERCENT = 5;
    uint256 public constant EXPIRATION = 1 hours;

    function setUp() public {
        owner = makeAddr("owner");
        developer = makeAddr("developer");
        agent = makeAddr("agent");
        attacker = makeAddr("attacker");

        vm.prank(owner);
        escrow = new Escrow();
    }

    function test_initial_state() public {
        assertEq(escrow.owner(), owner);
        assertEq(escrow.bountyCount(), 0);
        assertEq(escrow.MIN_BOUNTY(), MIN_BOUNTY);
        assertEq(escrow.FEE_PERCENT(), FEE_PERCENT);
    }

    function test_createBounty_success() public {
        uint256 bountyAmount = 0.01 ether;
        string memory ipfsHash = "QmTest123456789";

        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: bountyAmount}(ipfsHash, EXPIRATION);

        assertEq(escrow.bountyCount(), 1);

        // Verify bounty state
        assertEq(escrow.bountyCount(), 1);
        (uint256 id, address payable dev, uint256 amount, bool claimed, bool disputed, string memory hash, bytes memory agentSig, uint256 createdAt, uint256 expiresAt) = escrow.bounties(1);

        assertEq(id, 1);
        assertEq(dev, developer);
        assertEq(amount, bountyAmount - (bountyAmount * FEE_PERCENT) / 100);
        assertFalse(claimed);
        assertFalse(disputed);
        assertEq(hash, ipfsHash);
        assertEq(createdAt, block.timestamp);
        assertEq(expiresAt, block.timestamp + EXPIRATION);
    }

    function test_createBounty_belowMinimum() public {
        uint256 bountyAmount = 0.0005 ether; // Below minimum

        vm.deal(developer, 1 ether);
        vm.prank(developer);

        vm.expectRevert("Below minimum bounty");
        escrow.createBounty{value: bountyAmount}("QmTest", EXPIRATION);
    }

    function test_createBounty_invalidIpfsHash() public {
        vm.deal(developer, 1 ether);
        vm.prank(developer);

        vm.expectRevert("Invalid IPFS hash");
        escrow.createBounty{value: MIN_BOUNTY}("", EXPIRATION);
    }

    function test_createBounty_shortExpiration() public {
        vm.deal(developer, 1 ether);
        vm.prank(developer);

        vm.expectRevert("Minimum 1 hour expiry");
        escrow.createBounty{value: MIN_BOUNTY}("QmTest", 1800); // 30 minutes
    }

    function test_submitReport_success() public {
        // Create bounty first
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Sign a report
        bytes memory signature = _signReport(1, developer, "QmTest");

        vm.prank(agent);
        escrow.submitReport(1, signature);

        // Verify report was submitted
        (, , , , , , bytes memory agentSig, , ) = escrow.bounties(1);
        assertTrue(agentSig.length > 0);
    }

    function test_submitReport_bountyExpired() public {
        // Create bounty with very short expiration
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", 1 seconds);

        // Wait for expiration
        vm.warp(block.timestamp + 2 seconds);

        bytes memory signature = _signReport(1, developer, "QmTest");

        vm.prank(agent);
        vm.expectRevert("Bounty expired");
        escrow.submitReport(1, signature);
    }

    function test_submitReport_doubleSubmission() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Submit report twice
        bytes memory signature = _signReport(1, developer, "QmTest");

        vm.prank(agent);
        escrow.submitReport(1, signature);

        vm.prank(agent);
        vm.expectRevert("Report already submitted");
        escrow.submitReport(1, signature);
    }

    function test_claimBounty_success() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Submit report
        bytes memory signature = _signReport(1, developer, "QmTest");
        vm.prank(agent);
        escrow.submitReport(1, signature);

        // Record developer balance before
        uint256 balanceBefore = developer.balance;

        // Claim bounty
        vm.prank(developer);
        escrow.claimBounty(1);

        // Verify
        (, , , bool claimed, , , , , ) = escrow.bounties(1);
        assertTrue(claimed);
        assertEq(developer.balance, balanceBefore + 0.0095 ether); // 0.01 - 5% fee
    }

    function test_claimBounty_notDeveloper() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.deal(attacker, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Try to claim as attacker
        vm.prank(attacker);
        vm.expectRevert("Not bounty creator");
        escrow.claimBounty(1);
    }

    function test_claimBounty_alreadyClaimed() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Submit report
        bytes memory signature = _signReport(1, developer, "QmTest");
        vm.prank(agent);
        escrow.submitReport(1, signature);

        // Claim once
        vm.prank(developer);
        escrow.claimBounty(1);

        // Try to claim again
        vm.prank(developer);
        vm.expectRevert("Already claimed");
        escrow.claimBounty(1);
    }

    function test_disputeBounty_success() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Dispute
        vm.prank(developer);
        escrow.disputeBounty(1);

        // Verify
        (, , , , bool disputed, , , , ) = escrow.bounties(1);
        assertTrue(disputed);
    }

    function test_disputeBounty_notDeveloper() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.deal(attacker, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Try to dispute as attacker
        vm.prank(attacker);
        vm.expectRevert("Only developer can dispute");
        escrow.disputeBounty(1);
    }

    function test_disputeBounty_doubleDispute() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Dispute once
        vm.prank(developer);
        escrow.disputeBounty(1);

        // Try to dispute again
        vm.prank(developer);
        vm.expectRevert("Already disputed");
        escrow.disputeBounty(1);
    }

    function test_resolveDispute_rewardDeveloper() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Dispute
        vm.prank(developer);
        escrow.disputeBounty(1);

        // Resolve and reward developer
        vm.prank(owner);
        escrow.resolveDispute(1, true);

        // Verify
        (, , , bool claimed, bool disputed, , , , ) = escrow.bounties(1);
        assertTrue(claimed);
        assertFalse(disputed);
    }

    function test_resolveDispute_refund() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Dispute
        vm.prank(developer);
        escrow.disputeBounty(1);

        // Record owner balance before
        uint256 balanceBefore = owner.balance;

        // Resolve and refund to owner
        vm.prank(owner);
        escrow.resolveDispute(1, false);

        // Verify
        (, , , bool claimed, bool disputed, , , , ) = escrow.bounties(1);
        assertTrue(claimed);
        assertFalse(disputed);
        assertEq(owner.balance, balanceBefore + 0.0095 ether);
    }

    function test_resolveDispute_notOwner() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Dispute
        vm.prank(developer);
        escrow.disputeBounty(1);

        // Try to resolve as non-owner
        vm.prank(developer);
        vm.expectRevert();
        escrow.resolveDispute(1, true);
    }

    function test_collectFees() public {
        // Create bounty
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", EXPIRATION);

        // Dispute and resolve with refund
        vm.prank(developer);
        escrow.disputeBounty(1);

        vm.prank(owner);
        escrow.resolveDispute(1, false);

        // Record owner balance before
        uint256 balanceBefore = owner.balance;

        // Collect fees
        vm.prank(owner);
        escrow.collectFees();

        assertEq(owner.balance, balanceBefore + 0.0005 ether); // 5% fee
    }

    function test_getDeveloperBounties() public {
        // Create multiple bounties
        vm.deal(developer, 5 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest1", EXPIRATION);

        vm.prank(developer);
        escrow.createBounty{value: 0.02 ether}("QmTest2", EXPIRATION);

        // Get bounties
        Escrow.Bounty[] memory bounties = escrow.getDeveloperBounties(developer);

        assertEq(bounties.length, 2);
        assertEq(bounties[0].id, 1);
        assertEq(bounties[1].id, 2);
    }

    function test_getExpiredBounties() public {
        // Create bounty with short expiration
        vm.deal(developer, 1 ether);
        vm.prank(developer);
        escrow.createBounty{value: 0.01 ether}("QmTest", 1 seconds);

        // Wait for expiration
        vm.warp(block.timestamp + 2 seconds);

        // Get expired bounties
        Escrow.Bounty[] memory expired = escrow.getExpiredBounties();

        assertEq(expired.length, 1);
        assertEq(expired[0].id, 1);
    }

    // Helper function to sign a report
    function _signReport(uint256 bountyId, address dev, string memory ipfsHash) 
        internal view returns (bytes memory signature) 
    {
        bytes32 message = keccak256(
            abi.encodePacked(bountyId, dev, dev, ipfsHash)
        );

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(1, message); // Using private key 1 for testing
        signature = abi.encodePacked(r, s, v);
    }
}
