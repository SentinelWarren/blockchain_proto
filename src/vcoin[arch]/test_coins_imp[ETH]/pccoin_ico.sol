// Powercoins[pccoin] ICO

// Version of compiler
pragma solidity ^0.4.11:

contract pccoin_ico {

    // Defining the max number of pccoins available for sale
    uint public max_pccoins = 1000000;

    // Defining the USD to pccoins conversion rate
    uint public usd_to_pccoins = 1000;

    // Defining the total number of pccoins that have been bought by investors
    uint public total_pccoin_bought = 0;

    // Mapping from the investor address to is equity in pccoins and USD
    mapping(address => uint) equity_pccoins;
    mapping(address => uint) equity_usd;

    // Checking if investor can buy coins
    modifier can_buy_pccoins(uint usd_invested) {
        require (usd_invested * usd_to_pccoins + total_pccoin_bought <= max_pccoins);
        _;
    }

    // Getting the equity in pccoins of an investor
    function equity_in_pccoins(address investor) external constant returns(uint)
}