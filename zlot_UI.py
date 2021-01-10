import requests
import logging
import json
import os
import subprocess
import sys

from pycoingecko import CoinGeckoAPI
from web3 import Web3

infura_url='https://mainnet.infura.io/v3/f9a81520189642c89e0e2163ede73662'

web3 = Web3(Web3.HTTPProvider(infura_url))

zLot_token_address = '0xA8e7AD77C60eE6f30BaC54E2E7c0617Bd7B5A03E'
hegic_token_address = '0x584bC13c7D411c00c01A62e8019472dE68768430'
zHegic_pool_address = '0x9E4E091fC8921FE3575eab1c9a6446114f3b5Ef2'
zGovernance_address = '0x7c7b924b4eaed3DA875Bc792b5C1a0b33d118047'

hegic_abi = json.load(open('abi/hegic_token.json', 'r'))
zlot_abi = json.load(open('abi/zlot_token.json', 'r'))
hegic_pool_abi = json.load(open('abi/zhegic_pool_abi.json', 'r'))
zgovernance_abi = json.load(open('abi/zgovernance.json', 'r'))

HegicContract = web3.eth.contract(address=hegic_token_address, abi=hegic_abi)
zLotContract = web3.eth.contract(address=zLot_token_address, abi=zlot_abi)
zPoolContract = web3.eth.contract(address=zHegic_pool_address, abi=hegic_pool_abi)
zGovernanceContract = web3.eth.contract(address=zGovernance_address, abi=zgovernance_abi)

hegic_total_supply = HegicContract.functions.totalSupply().call()

price_per_share = zPoolContract.functions.getPricePerFullShare().call()
total_underlying = zPoolContract.functions.totalUnderlying().call()
progress_to_next_lot = zPoolContract.functions.unusedUnderlyingBalance().call()

zlot_total_supply = zLotContract.functions.totalSupply().call()
zlot_total_locked = zGovernanceContract.functions.totalSupply().call()

pps_eth = float(web3.fromWei(price_per_share, 'ether'))
total_u = float(web3.fromWei(total_underlying, 'ether'))
lot_progress = float(web3.fromWei(progress_to_next_lot, 'ether'))
zlot_supply = float(web3.fromWei(zlot_total_supply, 'ether'))
zlot_locked = float(web3.fromWei(zlot_total_locked, 'ether'))
hegic_supply = float(web3.fromWei(hegic_total_supply, 'ether'))

print(type(web3.fromWei(price_per_share, 'ether')))
print(type(web3.fromWei(total_u, 'ether')))
print(type(web3.fromWei(progress_to_next_lot, 'ether')))

APY = (pps_eth**(1.0/46.0*365.0)) - 1

cg = CoinGeckoAPI()
hegic_price = cg.get_price(ids='hegic', vs_currencies='usd')
zlot_price = cg.get_price(ids='zlot', vs_currencies='usd')

hegic_per_lot = 888888

print(' -------------- ZLOT Metrics -------------------- ')
print('TVL: ${}'.format(float(total_u)*hegic_price['hegic']['usd']))
print('APY: {}%, APW: {} %, APD: {} %, APH: {} %'.format(APY*100.0, APY/52.0*100.0, APY/365.25*100.0, APY/8760.0*100.0))
print('Hegic/zHegic Ratio: {}'.format(price_per_share))
print('Total Hegic Locked: {}'.format(total_u))
print('Total Lots Purchased: {}'.format(int(total_u/hegic_per_lot)))
print('Progress to Next Lot: {} - {} %'.format(float(lot_progress), (lot_progress/hegic_per_lot)*100.0))
print(' ==================================================')
print('Hegic Price: ${}, Zlot Price: ${}'.format(hegic_price['hegic']['usd'], zlot_price['zlot']['usd']))
print('Hegic Total Supply: {}, zLot Total Supply: {}'.format(hegic_supply, zlot_supply))
print('Total Hegic Staked: {}, Total zLot in Governance: {}'.format(10,zlot_total_locked))

df = {
    "hegic_price": hegic_price['hegic']['usd'],
    "zlot_price": zlot_price['zlot']['usd'],
    "hegic_staked": total_u,
    "lots_purchased": int(total_u/hegic_per_lot),
    "hegic_zhegic_ratio": price_per_share, 
    "tvl": float(total_u)*hegic_price['hegic']['usd'],
    "apy": APY*100.0,
    "apw": APY/52.0*100.0,
    "apd": APY/365.25*100.0
}

out = json.dumps(df)
print(out)

with open('data.json', 'w') as f:
    f.write(out)
    f.close()


# print(contract.ContractFunctions)


# # ENABLE LOGGING - options, DEBUG,INFO, WARNING?
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
# # if ETH --> DAI - (enter the amount in units Ether)
# amount_to_exchange = Web3.toWei(3, 'ether')
#
# # if DAI --> ETH (using base unit, so 1 here = 1 DAI/MCD)
# amount_of_dai = Web3.toWei(50, 'ether')
#
# hegic_pool = Web3.toChecksumAddress(
#     '0x584bC13c7D411c00c01A62e8019472dE68768430')
#
# w3 = Web3(Web3.HTTPProvider(
# # w3 = Web3(IPCProvider())
#
# hegic_abi = json.load(open('abi/hegic_abi.json', 'r'))
#
# hegic_token_contract = w3.eth.contract(address='0x584bC13c7D411c00c01A62e8019472dE68768430', abi=hegic_abi)
# hegic_pool_contract = w3.eth.contract(address='0x9E4E091fC8921FE3575eab1c9a6446114f3b5Ef2', abi=hegic_abi)
#
#
#
# token = w3.eth.contract(
#     '0x9E4E091fC8921FE3575eab1c9a6446114f3b5Ef2',
#     abi=hegic_abi,
# )
# print(token)
# print("Token balance of wallet", hegic_pool_contract, "is", token.functions.balanceOf(hegic_pool_contract))
#
# # print(hegic_token_contract)
# # print(hegic_pool_contract.functions)
# #
# # balance = hegic_pool_contract.functions.balanceOf().call({'from':0x9E4E091fC8921FE3575eab1c9a6446114f3b5Ef2})
#
# # raw_balance = hegic_token_contract.functions.balanceOf(hegic_pool_contract).call()
#
