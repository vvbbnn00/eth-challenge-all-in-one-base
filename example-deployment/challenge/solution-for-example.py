# _*_ coding: utf-8 _*_
"""
Time:     2023/3/14 17:19
Author:   不做评论(vvbbnn00)
Version:  
File:     solution-for-example.py
Describe: 
"""
from web3 import Web3, HTTPProvider

contractABI = """[
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_greeting",
				"type": "string"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"inputs": [],
		"name": "greet",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "isSolved",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_greeting",
				"type": "string"
			}
		],
		"name": "setGreeting",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	}
]"""

web3 = Web3(HTTPProvider("http://127.0.0.1:18081/jsonrpc"))
print(web3.isConnected())
account = web3.eth.account.privateKeyToAccount('0x1145141919810191919191191919a9961a0419190721072100772211aabbccdd')
print(account.address)
print(web3.eth.getBalance(account.address))

if __name__ == '__main__':
    # 部署合约
    contract = web3.eth.contract(abi=contractABI, address="0xC3A69a6c811Bc9F2c8Fab89a20fEC5c36628F57E")
    tx = contract.functions.setGreeting("HelloSLCTF(Exp)").buildTransaction({
        'from': account.address,
        'nonce': web3.eth.getTransactionCount(account.address),
        'gas': 3000000,
        'gasPrice': web3.toWei('1', 'gwei'),
    })
    signed_tx = account.signTransaction(tx)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
    print('Transaction', tx_receipt)
