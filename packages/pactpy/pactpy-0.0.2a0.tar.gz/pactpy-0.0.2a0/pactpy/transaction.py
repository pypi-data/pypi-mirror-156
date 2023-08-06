import json
import yaml
import pyblake2
import requests
import datetime
import hashlib
import time
import base64
from nacl.encoding import Base64Encoder
from nacl.signing import SigningKey


class PactTransaction:
    """'The fastast roadway' to interact with the Chainweb API."""

    def __init__(self):

        self.networks = {
        "development":"https://testnet.kaddex.com",
        "mainnet": "https://api.chainweb.com",
        "testnet04": "https://api.testnet.chainweb.com",
        "P2P": "https://us-e1.chainweb.com",
    }
        self.endpoints = ["send", "local"]
        self.header = {"Content-Type": "application/json"}
        self.hash = "123"
        self.sigs = []
        self.signers = []
        self.metadata = ""
        self.cmd = ""
        self.keypairs = {
            "public":[],
            "private":[]
        }

    ## NOTE: Should run before generate_cmd!
    def generate_metadata(self,
                          chain: str,
                          gasLimit: int,
                          gasPrice: float,
                          sender: str,
                          ttl: int):
        """Generate the metadata to be placed in the 'cmd' field of the final
        JSON. This method recieves the chain number (currenty 0-19) as a string.
        Also recieves the gasLimit (int), the gasPrice (float), the sender (str), and the ttl (int).
        All the parameter names are self-explanatory and have the same meaning as in PACT. If
        the user does not generate their own custom metadata, default values will be set when
        sending your command. Check the 'execute' functions' code to
        to change the default parameters."""

        date_time = datetime.datetime.now()
        dic = {
            "creationTime": time.mktime(date_time.timetuple()),  # something like 1654807588
            "ttl": ttl,
            "gasLimit": gasLimit,
            "chainId": chain,
            "gasPrice": gasPrice,
            "sender": sender,
        }

        self.metadata = dic

    def generate_exec(self, data: dict, code: str):
        """Generate the exec section to be placed in the in the 'cmd' field of the final
        JSON. This function is meant for internal use and its body only contains trivial code.
        Thus, we don't bother getting into it's details."""
        dic = {"data": data, "code": code}
        return dic

    def generate_payload(self, data: dict, code: str):
        """Generate the payload section to be placed in the 'cmd' field of the final
        JSON. This function runs only internally and it's code is trivial. Don't waste
        your time reading about it. """

        dic = {"exec": self.generate_exec(data, code)}
        return dic

    def generate_cmd(self, network: str, code: str, data: dict):
        """This function aggregates the appropriate fields into the final 'cmd'
        command. It is important that no parameter for the is changed after running this functions.
        The 'hash' and 'sigs' fields of the final JSON depend on the output of this function. Thus,
        this value cannot change after the hash is computed and the transaction is signed. """
        #NOTE: Auto Generate metadata with default values if self.metadata == ''. That is,
        #if the user does not generate a custom one.
        #FIXME: Sender field below
        if self.metadata == '':
            self.generate_metadata(
                chain ="0",
                gasLimit = 3000,
                gasPrice = 1e-7,
                sender = "?"
            )

        creation_time = str(datetime.datetime.now())
        dic = {
            "networkId": network,
            "payload": self.generate_payload(data, code),
            "signers": self.signers,
            "meta": self.metadata,
            "nonce": creation_time,
        }

        return json.dumps(dic)

    # NOTE: Signing Transactions: cmd -> hash (blake2b) -> sign using ED25519 ->
    # sha1 (hexadecimal)

    def sign_transaction(self, keys: str, cmd: str):
        """Sign transaction based on private key and stringified 'cmd'"""
        for signers in self.signers:
            # TODO: method for retrieving private keys
            self.sigs.append(signers.key.sign(cmd, encoder=Base64Encoder))
            json.dumps(sigs)

        return self.sigs

    def retrieve_keys(self, filename:str):

        """A simple method to retrieve keys from local file.
        It recieves a file name (string) as an argument and
        returns the keys."""

        file = open(filename, "r")
        lines = file.readlines()
        # assign list elements to variables
        public = lines[0][8:-1]
        private = lines[1][8:-1]
        self.keypairs["public"].append(public)
        self.keypairs["private"].append(private)

    def generate_local_command(self, cmd: str):
        hash = hashlib.blake2b(cmd.encode("utf-8"), digest_size=32).digest()
        encoded_hash = base64.urlsafe_b64encode(hash)
        dic = {"hash": encoded_hash.decode("utf-8"), "sigs": [], "cmd": cmd}
        return json.dumps(dic, indent=4)

    # NOTE: 'hash' field above uses
    # Unpadded Base64URL of Blake2b-256 hash of the cmd field value.
    # Serves as a #command requestKey since each transaction must be unique.

    def generate_send_command(self, cmd:str):
        """Adapt the result of 'generate_local_command' to be sent to the 'send'
        endpoint."""
        dic = {"cmds":[]}
        dic["cmds"].append(self.generate_local_command(cmd))
        return json.dumps(dic)

    def compose_url(self, network:str, endpoint:str, chain:int):
        """Compose the correct URL for interacting with the Chainweb API based on
        this function's self-explanatory parameters. We observe that
        the association between network IDS and URLs is done by the networks
        attribute. """
        url = self.networks[network] + "/chainweb/0.0/" + network + "/chain/" + str(chain) + "/pact/api/v1/" + endpoint
        return url

    def execute_command_local(self, network:str, chain:int, command:str):
        """This function is the main entrypoint for the PactTransaction class."""
        url = self.compose_url(network, "local",  chain)
        resp = requests.post(url, data = self.generate_local_command(command), headers = self.header)
        return resp

    def execute_command_send(self, network:str, chain:int, command:str):
        # TODO: Assert/Add GasPayer automatically
        url = self.compose_url(network, "send",  chain)
        resp = requests.post(url, data = self.generate_send_command(command), headers = self.header)
        return resp

    # TODO: Create method execute_command_send_and_wait. Send the command
    # and listen for result

    #NOTE: The following function must run before generate_cmd!
    def add_capability(self, pub_key:str, name:str, args:list):
        """Associate capability with public key. The arguments this function
        recieves are the publc key 'pub_key', which is a string identifying the
        user who will sign the capability and the capability itself. A capability
        is specified by the two final arguments 'name' and 'args'. The name (string) is the
        name of the capability (e.g coin.TRANSFER). Also, args is an ordered
        list containing the arguments to the fed to the capability name."""
        a = 0
        pos = {}
        for i in range(len(self.signers)):
            if self.signers[i]["pubKey"] == pub_key:
                a = 1
                pos = i

        if a == 1:
            print("oi")
            dic_in = {
            "args": args,
            "name": name
             }
            self.signers[pos]["clist"].append(dic_in)

        else:
            dic_out = {
            "pubKey": pub_key,
            "clist" : [] }
            dic_in = {
            "args": args,
            "name": name
             }
            dic_out["clist"].append(dic_in)
            self.signers.append(dic_out)

