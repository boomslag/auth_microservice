import rsa
import os
from cryptography.fernet import Fernet
from pyAesCrypt import decryptFile
from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from blockfrost import BlockFrostApi, ApiError, ApiUrls

 
cardano_api_rpc = settings.CARDANO_RPC_API
cardano_rpc = settings.CARDANO_RPC

api = BlockFrostApi(
    project_id=cardano_api_rpc,  # or export environment variable BLOCKFROST_PROJECT_ID
    # optional: pass base_url or export BLOCKFROST_API_URL to use testnet, defaults to ApiUrls.mainnet.value
    base_url=ApiUrls.testnet.value,
)

User = settings.AUTH_USER_MODEL
encryption_password = settings.ENCRYPTION_PASSWORD

from web3 import Web3

infura_url=settings.INFURA_URL
polygon_rpc=settings.POLYGON_RPC
polygon_web3 = Web3(Web3.HTTPProvider(polygon_rpc))

from eth_account import Account

import secrets
import base64
import json
from core.producer import producer
from django.utils.timezone import now
from djoser.signals import  user_registered

debug = settings.DEBUG

pdm_goerli = settings.PDM_ADDRESS_GOERLI
pdm_mainnet = settings.GALR_ADDRESS_GOERLI
galr_goerli = settings.PDM_ADDRESS_MAINNET
galr_mainnet = settings.GALR_ADDRESS_MAINNET


# Create your models here.
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')

    # Ethereum Wallet
    address = models.CharField(max_length=255, unique=True)
    private_key = models.TextField(unique=True)

    # Polygon Wallet
    polygon_address = models.CharField(max_length=255, unique=True)
    polygon_private_key = models.TextField(unique=True)

    savings = models.DecimalField(max_digits=1000, decimal_places=2, default=0, blank=False)
    product_sales = models.DecimalField(max_digits=1000, decimal_places=2, default=0, blank=False)
    course_sales = models.DecimalField(max_digits=1000, decimal_places=2, default=0, blank=False)
    total_earnings = models.DecimalField(max_digits=1000, decimal_places=2, default=0, blank=False)
    total_spent = models.DecimalField(max_digits=1000, decimal_places=2, default=0, blank=False)
    total_transfered = models.DecimalField(max_digits=1000, decimal_places=2, default=0, blank=False)
    total_received = models.DecimalField(max_digits=1000, decimal_places=2, default=0, blank=False)

    save_card = models.BooleanField(default=False)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    from_address = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    tx_hash = models.CharField(max_length=255)

    def __str__(self):
        return self.tx_hash


class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transactions = models.ManyToManyField(Transaction, blank=True)
    def __str__(self):
        return self.user.email


def create_user_wallet(request, user, *args, **kwargs):
    # Import the public_key.txt using the Django settings module
    public_key_path = os.path.join(settings.BASE_DIR, 'public_key.txt')
    with open(public_key_path, "rb") as f:
        pubkey = rsa.PublicKey.load_pkcs1(f.read())

    # 1. Define user
    user = user
    # 2. Create Wallet
    wallet = Wallet.objects.create(user=user)
    
    # 3. Get Wallet private key and public key
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    
    # 4. Encrypt the private key with RSA
    private_key_bytes = private_key.encode('ascii')
    encrypted_key_bytes = rsa.encrypt(private_key_bytes, pubkey)

    # 5. Encode the encrypted private key as base64
    base64_bytes = base64.b64encode(encrypted_key_bytes)
    encoded_string = base64_bytes.decode('ascii')

    # 6. Save the encoded private key to the user wallet
    wallet.private_key = encoded_string
    wallet.address = acct.address
    wallet.save()

    # CREATE POLGYON WALLET
    # Get Polygon wallet private key and public key
    polygon_priv_key = polygon_web3.eth.account.create().privateKey.hex()
    
    # Encrypt the Polygon private key with RSA
    polygon_priv_bytes = polygon_priv_key.encode('ascii')
    polygon_encrypted_bytes = rsa.encrypt(polygon_priv_bytes, pubkey)

    # Encode the encrypted Polygon private key as base64
    polygon_base64_bytes = base64.b64encode(polygon_encrypted_bytes)
    polygon_encoded_string = polygon_base64_bytes.decode('ascii')

    # Save the encoded Polygon private key to the user wallet
    wallet.polygon_private_key = polygon_encoded_string
    wallet.polygon_address = polygon_web3.toChecksumAddress(polygon_web3.eth.account.from_key(polygon_priv_key).address)
    wallet.save()

    item = {}
    item['address'] = acct.address
    item['polygon_address'] = wallet.polygon_address
    producer.produce(
        'wallet_created',
        key='create_wallet',
        value=json.dumps(item).encode('utf-8')
    )
    producer.flush()

    # # CREATE CARDANO WALLET
    # # Create a new Cardano wallet
    # response = api.wallets.post()
    # wallet_id = response.get("id")

    # # Get the wallet address and private key
    # response = api.wallets_addresses_post(wallet_id)
    # cardano_address = response[0].get("address")
    # cardano_private_key = response[0].get("private_key")

    # # Save the wallet address and private key to the user wallet
    # wallet.cardano_address = cardano_address
    # wallet.cardano_private_key = cardano_private_key
    # wallet.save()

user_registered.connect(create_user_wallet)
