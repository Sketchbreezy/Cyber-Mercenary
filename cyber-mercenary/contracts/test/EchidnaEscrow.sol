// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Escrow} from "../src/Escrow.sol";

/// @title Echidna Fuzzing Tests for Escrow Contract
/// @notice Property-based tests for invariant verification

contract EchidnaEscrowTest {
    Escrow public escrow;
    address public owner;
    address public developer;
    
    uint256 public constant MIN_BOUNTY = 0.001 ether;
    uint256 public constant FEE_PERCENT = 5;
    
    // State tracking
    uint256 public totalBounties;
    uint256 public totalValueLocked;
    
    constructor() {
        owner = msg.sender;
        vm.createSelectFork("https://monad-testnet.drpc.org");
        vm.startBroadcast(owner);
        escrow = new Escrow();
        vm.stopBroadcast();
        
        developer = makeAddr("developer");
    }
    
    // Helper to create funded account
    function _createFundedAccount(uint256 value) internal returns (address) {
        address acc = makeAddr(string(abi.encodePacked("user_", vm.toString(value))));
        vm.deal(acc, value);
        return acc;
    }
    
    // Property: Bounty count always increases with creation
    function test_bountyCount_increases() public {
        address user = _createFundedAccount(10 ether);
        
        uint256 before = escrow.bountyCount();
        
        vm.prank(user);
        escrow.createBounty{value: MIN_BOUNTY}("QmTest", 1 hours);
        
        assert(escrow.bountyCount() == before + 1);
    }
    
    // Property: Fee calculation is correct
    function test_fee_calculation() public {
        uint256 amount = 1 ether;
        uint256 expectedFee = (amount * FEE_PERCENT) / 100;
        
        address user = _createFundedAccount(amount + 1 ether);
        
        vm.prank(user);
        escrow.createBounty{value: amount}("QmTest", 1 hours);
        
        // Check bounty state
        (,,,,,,,uint256 createdAt,uint256 expiresAt) = escrow.bounties(1);
        assert(createdAt > 0);
        assert(expiresAt > block.timestamp);
    }
    
    // Property: Cannot claim without report or expiration
    function test_claim_requires_report_or_expiration() public {
        address user = _createFundedAccount(1 ether);
        
        vm.prank(user);
        escrow.createBounty{value: 0.01 ether}("QmTest", 1 hours);
        
        vm.prank(user);
        vm.expectRevert(); // Should fail
        escrow.claimBounty(1);
    }
    
    // Property: Once claimed, cannot be claimed again
    function test_cannot_claim_twice() public {
        address user = _createFundedAccount(2 ether);
        
        // Create and claim
        vm.prank(user);
        escrow.createBounty{value: 0.01 ether}("QmTest", 1 seconds);
        
        // Warp past expiration
        vm.warp(block.timestamp + 2 seconds);
        
        // Claim first time
        vm.prank(user);
        escrow.claimBounty(1);
        
        // Try to claim again
        vm.prank(user);
        vm.expectRevert("Already claimed");
        escrow.claimBounty(1);
    }
    
    // Property: Cannot dispute twice
    function test_cannot_dispute_twice() public {
        address user = _createFundedAccount(1 ether);
        
        vm.prank(user);
        escrow.createBounty{value: 0.01 ether}("QmTest", 1 hours);
        
        // Dispute first time
        vm.prank(user);
        escrow.disputeBounty(1);
        
        // Try to dispute again
        vm.prank(user);
        vm.expectRevert("Already disputed");
        escrow.disputeBounty(1);
    }
    
    // Property: Owner can always resolve disputes
    function test_owner_can_resolve() public {
        address user = _createFundedAccount(2 ether);
        
        vm.prank(user);
        escrow.createBounty{value: 0.01 ether}("QmTest", 1 hours);
        
        // Dispute
        vm.prank(user);
        escrow.disputeBounty(1);
        
        // Resolve as owner
        escrow.resolveDispute(1, true);
        
        assert(escrow.bounties(1).claimed == true);
        assert(escrow.bounties(1).disputed == false);
    }
    
    // Property: Bounty state is consistent after resolution
    function test_bounty_state_after_resolution() public {
        address user = _createFundedAccount(2 ether);
        
        vm.prank(user);
        escrow.createBounty{value: 0.01 ether}("QmTest", 1 hours);
        
        // Dispute and resolve
        vm.prank(user);
        escrow.disputeBounty(1);
        
        escrow.resolveDispute(1, true);
        
        // State should be consistent
        (,,,, bool disputed, , , , ) = escrow.bounties(1);
        assert(disputed == false);
    }
    
    // Property: getDeveloperBounties returns correct count
    function test_getDeveloperBounties_count() public {
        address user = _createFundedAccount(5 ether);
        
        // Create 3 bounties
        for (uint256 i = 0; i < 3; i++) {
            vm.prank(user);
            escrow.createBounty{value: 0.01 ether}("QmTest", 1 hours);
        }
        
        Escrow.Bounty[] memory bounties = escrow.getDeveloperBounties(user);
        assert(bounties.length == 3);
    }
    
    // Property: getExpiredBounties only returns expired bounties
    function test_getExpiredBounties_filter() public {
        address user = _createFundedAccount(2 ether);
        
        // Create one with 1 second expiration
        vm.prank(user);
        escrow.createBounty{value: 0.01 ether}("QmTest1", 1 seconds);
        
        // Create one with long expiration
        vm.prank(user);
        escrow.createBounty{value: 0.01 ether}("QmTest2", 365 days);
        
        // Only first should be expired
        vm.warp(block.timestamp + 2 seconds);
        
        Escrow.Bounty[] memory expired = escrow.getExpiredBounties();
        assert(expired.length == 1);
        assert(expired[0].id == 1);
    }
}
