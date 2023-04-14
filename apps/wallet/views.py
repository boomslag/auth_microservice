from rest_framework_api.views import BaseAPIView, StandardAPIView
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.cache import cache
import json
from .models import Wallet
from .serializers import UserWalletSerializer,UserWalletPrivateKeySerializer
from django.db.models.query_utils import Q
from django.db.models import F
import os
import requests
from django.conf import settings
from web3 import Web3
infura_url=settings.INFURA_URL
web3 = Web3(Web3.HTTPProvider(infura_url))
ETHERSCAN_API_KEY=settings.ETHERSCAN_API_KEY
DEBUG=settings.DEBUG

def get_contract_abi(address):
    if DEBUG:
        url = f'https://api-goerli.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_API_KEY}'
    else:
        url = f'https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={ETHERSCAN_API_KEY}'

    response = requests.get(url)
    data = response.json()

    if data['status'] == '1':
        return data['result']
    else:
        return None

# Create your views here.
class MyUserWalletView(StandardAPIView):
    def get(self,request,*args, **kwargs):
        user = self.request.user
        wallet = Wallet.objects.get(user=user)
        serializer = UserWalletSerializer(wallet)
        wallet_data = serializer.data
        return self.send_response(wallet_data,status=status.HTTP_200_OK)

class GetUserWalletView(StandardAPIView):
    def get(self,request,*args, **kwargs):
        address = request.query_params.get('address', None)
        wallet = Wallet.objects.get(address=address)
        serializer = UserWalletPrivateKeySerializer(wallet)
        wallet_data = serializer.data
        return self.send_response(wallet_data,status=status.HTTP_200_OK)

class GetUserPolygonWalletView(StandardAPIView):
    def get(self,request,*args, **kwargs):
        address = request.query_params.get('address', None)
        wallet = Wallet.objects.get(polygon_address=address)
        serializer = UserWalletPrivateKeySerializer(wallet)
        wallet_data = serializer.data
        return self.send_response(wallet_data,status=status.HTTP_200_OK)


class MyUserWalletBalanceView(StandardAPIView):
    def get(self,request,*args, **kwargs):
        user = self.request.user
        wallet = Wallet.objects.get(user=user)
        balance = web3.eth.getBalance(wallet.address)
        wallet_balance = web3.fromWei(balance,"ether")
        # return Response({'balance':web3.fromWei(balance,"ether")},status=status.HTTP_200_OK)
        return self.send_response(wallet_balance,status=status.HTTP_200_OK)


class GetPraediumBalanceView(StandardAPIView):
    def get(self,request,*args, **kwargs):
        user = self.request.user
        wallet = Wallet.objects.get(user=user)

        json_path = os.path.join(settings.BASE_DIR, 'apps/wallet/contracts/PraediumToken.sol/PraediumToken.json')
        with open(json_path) as f:
            json_data = json.load(f)
            abi = json_data["abi"]

        contract_address = '0x018bCe5a7416DEf133BDf76eef6fEADdfE83f2ec'  # replace with your actual contract address
        contract = web3.eth.contract(address=contract_address, abi=abi)
        balance_wei = contract.functions.balanceOf(wallet.address).call()
        balance_ether = Web3.fromWei(balance_wei, 'ether')
        # print(contract)
        return self.send_response(balance_ether,status=status.HTTP_200_OK)


class GetGalacticReserveBalanceView(StandardAPIView):
    def get(self,request,*args, **kwargs):
        user = self.request.user
        wallet = Wallet.objects.get(user=user)

        json_path = os.path.join(settings.BASE_DIR, 'apps/wallet/contracts/GalacticReserveToken.sol/GalacticReserveToken.json')
        with open(json_path) as f:
            json_data = json.load(f)
            abi = json_data["abi"]

        contract_address = '0x399e35c6b05f16D26EeeeEbf1b49c267C0d5aE12'  # replace with your actual contract address
        contract = web3.eth.contract(address=contract_address, abi=abi)
        balance_wei = contract.functions.balanceOf(wallet.address).call()
        balance_ether = Web3.fromWei(balance_wei, 'ether')
        # print(contract)
        return self.send_response(balance_ether,status=status.HTTP_200_OK)
    
