
# import the following dependencies
import json
from web3 import Web3
import asyncio
from params import provider, uniswap_router, uniswap_factory, uniswap_factory_abi, EIP20_ABI, bnb_contract_address, testnet_provider, testnet_uniswap_router, testnet_uniswap_factory, testnet_bnb_contract_address
from uniswap import Uniswap
from scrape import webScrap

testnet = False

    
bnb_price = 330
market_cap_limit = 1*10**7/bnb_price #10 million

address = "0xdE3D71943855bd7734756b8D3CC8401CC6bfcc17"          # or None if you're not going to make transactions
private_key = "09346b9ae064ed911065e756dcdd0ad3132753936323d119db11ea1084d4af06"  # or None if you're not going to make transactions
version = 2                       # specify which version of Uniswap to use
#provider = "WEB3 PROVIDER URL"    # can also be set through the environment variable `PROVIDER`

uniswap = Uniswap(address=address, private_key=private_key, version=version, provider=provider, router_contract_addr= uniswap_router, factory_contract_addr = uniswap_factory, default_slippage = 0.25)



# add your blockchain connection information
web3 = Web3(Web3.HTTPProvider(provider))
contract = web3.eth.contract(address=uniswap_factory, abi=uniswap_factory_abi)

    
# define function to handle events and print to the console
def handle_event(event):
    # print(Web3.toJSON(event))
    pair_details = Web3.toJSON(event)
    pair_details = json.loads(pair_details)
    print('-----------------------------')
    # print(pair_details['args'])
    identifier0 = "Unknown"
    identifier1 = "Unknown"
    pair = pair_details['args']['pair']
    token0 = pair_details['args']['token0']
    token1 = pair_details['args']['token1']
    token0_is_bnb = False
    token1_is_bnb = False
    if token0 == bnb_contract_address:
            token_address = token1
            token0_is_bnb = True
    elif token1 == bnb_contract_address:
            token_address = token0
            token1_is_bnb = True
    if token0_is_bnb or token1_is_bnb:
        address = web3.toChecksumAddress(token_address)
        contract = web3.eth.contract(address, abi=EIP20_ABI)
        identifier = contract.functions.name().call()
        decimals = contract.functions.decimals().call()
        supply = contract.functions.totalSupply().call()/(10**decimals)
        #Check if identifier and supply are correct
        #if identifier.lower() == 'simbax' and supply == 1000000000000000000000000000000000:
        #if supply == 1000000000000000000000000000000000: #will there be 18 decimals. If we don't know, best we can't use it as a filter
        #    print('supply is 1 quadrillion!!!!!!')
        if 'a' in identifier.lower(): #if 'simbax' in identifier.lower():
            if webScrap('simbax'): #if webScrap(str(contract))
                bnb_to_invest = 0.005
                amount_to_purchase = uniswap.get_price_input(bnb_contract_address, address, int(bnb_to_invest*10**18))/(10**decimals)
                print(f'Amount to Purchase: {amount_to_purchase}')
                price = bnb_to_invest/amount_to_purchase
                print(f'Price: {price}')
                mcap = price * supply
                if  mcap < market_cap_limit:
                    print(f'BUY! Marketcap is {mcap * bnb_price/1000000} million')
                    uniswap.make_trade(bnb_contract_address, address, int(bnb_to_invest*10**18))
                    print('transaction sent')
                else:
                    print(f'Do Not buy! Marketcap is too high. Marketcap is {mcap * bnb_price/1000000} million')
            
        print("Searching")
        if token0_is_bnb:
            print(f'BNB: {token0}\n{identifier}: {token1}\npair: {pair}')
            print(f'Supply: {supply}')
        elif token1_is_bnb:
            print(f'{identifier}: {token0}\nBNB: {token1}\npair: {pair}')
            print(f'Supply: {supply}')
        else:
            print(f'Unknown: {token0}\nUnknown: {token1}\npair: {pair}')
        print(f'decimals: {decimals}')


# asynchronous defined function to loop
# this loop sets up an event filter and is looking for new entires for the "PairCreated" event
# this loop runs on a poll interval
async def log_loop(event_filter, poll_interval):
    while True:
        for PairCreated in event_filter.get_new_entries():
            handle_event(PairCreated)
        await asyncio.sleep(poll_interval)


# when main is called
# create a filter for the latest block and look for the "PairCreated" event for the uniswap factory contract
# run an async loop
# try to run the log_loop function above every 2 seconds
def main():
    event_filter = contract.events.PairCreated.createFilter(fromBlock='latest')
    #block_filter = web3.eth.filter('latest')
    # tx_filter = web3.eth.filter('pending')
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(event_filter, 2)))
        # log_loop(block_filter, 2),
        # log_loop(tx_filter, 2)))
    finally:
        # close loop to free up system resources
        loop.close()


if __name__ == "__main__":
    main()
