import random
import requests
import json
import time
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_abi import abi
from pyuseragents import random as random_useragent




class ZAT(object):

    def __init__(self,private_key, proxy = None):

        if proxy != None:
                self.proxy = {'https': f'http://{proxy}', 'http': f'http://{proxy}'}
                self.web3 = Web3(Web3.HTTPProvider('https://mainnet.era.zksync.io', request_kwargs={
                    "proxies": self.proxy}))

        else:
            self.web3 = Web3(Web3.HTTPProvider('https://mainnet.era.zksync.io'))
            self.proxy = proxy

        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.private_key = private_key
        self.address = (self.web3.eth.account.from_key(private_key)).address
        self.user_agent = random_useragent()

        with open('abi.json') as f:
            self.abi = json.load(f)
        self.contract_ZAT = self.web3.eth.contract(
            address=self.web3.to_checksum_address('0x47ef4a5641992a72cfd57b9406c9d9cefee8e0c4'),
            abi=[self.abi['balanceOf'],self.abi['allowance']]
        )
        self.contract_clime = self.web3.eth.contract(
            address=self.web3.to_checksum_address('0x9aA48260Dc222Ca19bdD1E964857f6a2015f4078'),
            abi=[self.abi['clime'],self.abi['claimed']]
        )






    def swap_data(self,n=10):

        try:
            r = requests.get(
                url='https://app.geckoterminal.com/api/p1/zksync/pools/0x2A936038B695F48b68a560cf01C4Cf8899616C5c'
                    '?include=dex%2Cdex.network.explorers%2Cnetwork_link_services%2Ctoken_link_services'
                    '%2Cdex_link_services&base_token=0',
                proxies=self.proxy
            ).json()

            return r


        except requests.exceptions.ProxyError as e:

            if n <= 0:
                return

            print(
                f"\033[31mPossibly a wrong proxy format was entered.\nCheck: login,password@ip,port\nAccount "
                f"{self.address} error : {e}\nLets try {n} more time")

            time.sleep(10)
            n -= 1
            return self.swap_data(n)

        except Exception as e:
            if n <= 0:
                return
            print(f"\033[31mAccount {self.address} error get swap_data: {e}\nLets try {n} more time")

            time.sleep(10)
            n -= 1
            return self.swap_data(n)




    def send_swap(self,r,n=5):

        try:

            tokenIn = self.web3.to_checksum_address('0x47ef4a5641992a72cfd57b9406c9d9cefee8e0c4')
            stepTo = self.address
            withdrawMode = 1

            pool = self.web3.to_checksum_address('0x2a936038b695f48b68a560cf01c4cf8899616c5c')
            data = abi.encode(["address", "address", "uint8"], [tokenIn, stepTo, withdrawMode])
            callback = '0x0000000000000000000000000000000000000000'
            callbackData = b''

            

            amountIn = self.balance_ZAT

            steps = [[pool, data, callback, callbackData]]
            paths = [[steps, tokenIn, amountIn]]
            amountOutMin = int((float(r['data']['attributes']['price_in_target_token']) * self.balance_ZAT * 0.97))
            deadline = (int(time.time()) + 12000)

            contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address('0x2da10a1e27bf85cedd8ffb1abbe97e53391c0295'),
                abi=[self.abi['swap']]
            )

            dict_transaction = {
                'chainId': 324,
                'from': self.address,
                'nonce': self.web3.eth.get_transaction_count(self.address),
                'gas': random.randint(3853366, 5853367),
                'gasPrice': self.web3.to_wei(0.25, 'gwei')
            }

            transaction = contract.functions.swap(
                paths, amountOutMin, deadline
            ).build_transaction(dict_transaction)

            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)


            try_b = 10
            while try_b>0:
                try_b -=1
                time.sleep(10)
                w = self.web3.eth.get_transaction_receipt(txn_hash)
                if 'status' in w and w['status'] ==1:
                    for topic in range(0, len(w.logs)):
                        t = w.logs[topic]

                        if len(t['topics']) > 1 and self.web3.to_checksum_address(
                                '0x' + str(t['topics'][1].hex())[-40:]) == '0x621425a1Ef6abE91058E9712575dcc4258F8d091':
                            swap_eth = float(str(int(str(t['data'].hex()), 0)) + 'e-18')
                            return print(f'\033[32mAccount {self.address} swap {self.balance_ZAT} $ZAT to {swap_eth} $ETH\n{txn_hash.hex()}')
                    return print(f'\033[32mAccount {self.address} swap {self.balance_ZAT} $ZAT to $ETH\n{txn_hash.hex()}')

            n-=1
            print(f"\033[31mAccount {self.address} failed swap:\n{txn_hash.hex()}\nLets try {n} more time")
            return self.send_swap(r,n)

        except Exception as e:
            if n <= 0:
                return
            print(f"\033[31mAccount {self.address} error swap: {e}\nLets try {n} more time")

            time.sleep(10)
            n -= 1
            return self.send_swap(r,n)





    def swap(self):

        self.balance_ZAT = self.contract_ZAT.functions.balanceOf(self.address).call()
        if self.balance_ZAT ==0:
            return print(f"\033[31mAccount {self.address} no tokens for swap")

        allowance = self.contract_ZAT.functions.allowance(self.address, self.web3.to_checksum_address('0x2da10a1e27bf85cedd8ffb1abbe97e53391c0295')).call()
        if allowance < self.balance_ZAT:
            self.approve()
            time.sleep(random.randint(30,60))

        data = self.swap_data()
        if data!= None:
            return self.send_swap(data)
        return





    def approve(self,n=5):
        try:

            transaction = {
                'chainId': 324,
                'to': self.web3.to_checksum_address('0x47ef4a5641992a72cfd57b9406c9d9cefee8e0c4'),
                'from': self.address,
                'nonce': self.web3.eth.get_transaction_count(self.address),
                'gas': random.randint(1323062, 1523062),
                'gasPrice': self.web3.to_wei(0.25, 'gwei'),
                'data': '0x095ea7b30000000000000000000000002da10a1e27bf85cedd8ffb1abbe97e53391c0295ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'
            }

            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            try_a = 10
            while try_a > 0:

                w = self.web3.eth.get_transaction_receipt(txn_hash)
                if 'status' in w and w['status'] == 0:
                    time.sleep(5)
                    try_a -= 1

                elif 'status' in w and w['status'] == 1:

                    allowance = self.contract_ZAT.functions.allowance(self.address, self.web3.to_checksum_address('0x2da10a1e27bf85cedd8ffb1abbe97e53391c0295')).call()

                    if allowance >= self.balance_ZAT:
                        print(f'\033[32mAccount {self.address} approve $ZAT:\n{txn_hash.hex()}')
                        return allowance
                    else:
                        time.sleep(5)
                        try_a -= 1

                    return allowance




            return self.approve(n)



        except Exception as e:
            if n <= 0:
                return
            print(f"\033[31mAccount {self.address} error approve: {e}\nLets try {n} more time")

            time.sleep(10)
            n -= 1
            return self.approve(n)



    def clime_data(self,n=10):
        try:

            claimed = self.contract_clime.functions.claimed(self.address).call()

            if claimed ==True:
                print(f'\033[32mAccount {self.address} already claimed $ZAT')
                return


            data = json.dumps({"address": self.address})

            headers = {

                'accept': 'application/json,text/plain,*/*',
                'accept-language': 'ru,en-US;q=0.9,en;q=0.8,ru-RU;q=0.7',
                'accept-encoding': 'gzip, deflate, br',
                'content-type': 'application/json',
                'user-agent': self.user_agent
            }

            r = requests.post(
                url='https://zksync-ape-apis.zkape.io/airdrop/index/getcertificate',
                headers=headers,
                data=data,
                proxies=self.proxy
            ).json()



            if r['Code'] == 400:

                return print(f'\033[31mAccount {self.address} not eligible')
            elif r['Code'] == 200 and 'value' in r['Data']:
                print(f'\033[32mAccount {self.address} eligible {float(str(int(r["Data"]["value"])) + "e-18")} $ZAT')
                return r
            else:
                return print(f'\033[31mAccount {self.address} unknown error get clime_data')


        except requests.exceptions.ProxyError as e:

            if n <= 0:
                return

            print(
                f"\033[31mPossibly a wrong proxy format was entered.\nCheck: login,password@ip,port\nAccount "
                f"{self.address} error : {e}\nLets try {n} more time")

            time.sleep(10)
            n -= 1
            return self.clime_data(n)

        except Exception as e:
            if n <= 0:
                return
            print(f"\033[31mAccount {self.address} error get clime_data: {e}\nLets try {n} more time")

            time.sleep(10)
            n -= 1
            return self.clime_data(n)

    def send_clime(self,r, n=5):

        try:

            owner = r['Data']['owner']
            value = int(r['Data']['value'])
            nonce = int(r['Data']['nonce'])
            deadline = int(r['Data']['deadline'])
            _v = int(r['Data']['v'])
            _r = self.web3.to_bytes(hexstr=r['Data']['r'])
            _s = self.web3.to_bytes(hexstr=r['Data']['s'])

            dict_transaction = {
                'chainId': 324,
                'from': self.address,
                'nonce': self.web3.eth.get_transaction_count(self.address),
                'gas': random.randint(4500000, 6100000),
                'gasPrice': self.web3.to_wei(0.25, 'gwei')
            }

            transaction = self.contract_clime.functions.claim(
                owner,
                value,
                nonce,
                deadline,
                _v,
                _r,
                _s).build_transaction(dict_transaction)

            signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
            txn_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)

            try_b = 10
            while try_b > 0:

                w = self.web3.eth.get_transaction_receipt(txn_hash)
                if 'status' in w and w['status'] == 0:
                    time.sleep(5)
                    try_b -= 1

                elif 'status' in w and w['status'] == 1:
                    balance_ZAT = self.contract_ZAT.functions.balanceOf(self.address).call()
                    print(
                        f'\033[32mAccount {self.address} clime {float(str(balance_ZAT) + "e-18")} $ZAT\n{txn_hash.hex()}')
                    return balance_ZAT


            return self.send_clime(r, n)


        except Exception as e:
            if n <= 0:
                return
            print(f"\033[31mAccount {self.address} error send clime: {e}\nLets try {n} more time")

            time.sleep(10)
            n -= 1
            return self.send_clime(r, n)





    def clime(self):

        r = self.clime_data()
    


        if r == None:
            return
        else:
            time.sleep(random.randint(5, 10))
            return self.send_clime(r)


    def all(self):

        self.clime()
        time.sleep(random.randint(60, 120))
        return self.swap()




