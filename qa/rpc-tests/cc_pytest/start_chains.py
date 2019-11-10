import os
import time
import sys
import subprocess
from slickrpc import Proxy


clients_to_start = int(os.environ['CLIENTS'])
ac_name = os.environ['CHAIN']
# node1 params
test_address = os.environ['TEST_ADDY']
test_wif = os.environ['TEST_WIF']
test_pubkey = os.environ['TEST_PUBKEY']
# node2 params
test_address2 = os.environ['TEST_ADDY2']
test_wif2 = os.environ['TEST_WIF2']
test_pubkey2 = os.environ['TEST_PUBKEY2']
# expecting REGTEST or REGULAR there
chain_start_mode = os.environ['CHAIN_MODE']

# pre-creating separate folders and configs
for i in range(clients_to_start):
    os.mkdir("node_" + str(i))
    open("node_" + str(i) + "/" + ac_name + ".conf", 'a').close()
    with open("node_" + str(i) + "/" + ac_name + ".conf", 'a') as conf:
        conf.write("rpcuser=test" + '\n')
        conf.write("rpcpassword=test" + '\n')
        conf.write("rpcport=" + str(7000 + i) + '\n')
        conf.write("rpcbind=0.0.0.0\n")
        conf.write("rpcallowip=0.0.0.0/0\n")

# start numnodes daemons, changing folder name and port
for i in range(clients_to_start):
    # all nodes should search for first "mother" node
    if i == 0:
        start_args = ['../../../src//komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-port=' + str(6000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-pubkey=' + test_pubkey, '-whitelist=127.0.0.1']
        if chain_start_mode == 'REGTEST':
            start_args.append('-regtest')
            start_args.append('-daemon')
        else:
            start_args.append('-daemon')
        subprocess.call(start_args)
        time.sleep(5)
    else:
        start_args = ['../../../src//komodod', '-ac_name='+ac_name, '-conf=' + sys.path[0] + '/node_' + str(i) + "/" + ac_name + ".conf",
                         '-rpcport=' + str(7000 + i), '-port=' + str(6000 + i), '-datadir=' + sys.path[0] + '/node_' + str(i),
                         '-ac_supply=10000000000', '-ac_cc=2', '-addnode=127.0.0.1:6000', '-whitelist=127.0.0.1', '-listen=0', '-pubkey='+test_pubkey]
        if i == 1:
            start_args.append('-pubkey=' + test_pubkey2)
        if chain_start_mode == 'REGTEST':
            start_args.append('-regtest')
            start_args.append('-daemon')
        else:
            start_args.append('-daemon')
        subprocess.call(start_args)
        time.sleep(5)


# creating rpc proxies for all nodes
for i in range(clients_to_start):
    rpcport = 7000 + i
    globals()['proxy_%s' % i] = Proxy("http://%s:%s@127.0.0.1:%d"%("test", "test", int(rpcport)))
time.sleep(2)


# checking if proxies works as expected
for i in range(clients_to_start):
    while True:
        try:
           getinfo_output = globals()['proxy_%s' % i].getinfo()
           print(getinfo_output)
           break
        except Exception as e:
           print(e)
           time.sleep(2)

# importing privkeys
proxy_0.importprivkey(test_wif)
time.sleep(1)
proxy_1.importprivkey(test_wif2)

# checking if test addys belongs to relevant nodes wallets
assert proxy_0.validateaddress(test_address)["ismine"]
assert proxy_1.validateaddress(test_address2)["ismine"]

# checking if pubkeys set properly
assert proxy_0.getinfo()["pubkey"] == test_pubkey
assert proxy_1.getinfo()["pubkey"] == test_pubkey2

# starting blocks creation on second node, mining rewards will get first public node because of pubkey param
if chain_start_mode == 'REGTEST':
    while True:
       if int(os.environ['CLIENTS']) > 1:
           proxy_1.generate(1)
           time.sleep(5)
       else:
           proxy_0.generate(1)
           time.sleep(5)
else:
    if int(os.environ['CLIENTS']) > 1:
        print("Starting mining on node 2")
        proxy_1.setgenerate(True, 1)
    else:
        print("Starting mining on node 1")
        proxy_0.setgenerate(True, 1)


# TODO: load from bootstrap, asserts that all things initiated propertly