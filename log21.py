import sys
import json
import click
from subprocess import check_output
from two1.commands.config import Config
from two1.lib.wallet import Wallet
from two1.lib.bitrequests import BitTransferRequests

wallet = Wallet()
username = Config().username
requests = BitTransferRequests(wallet, username)
server_url = 'http://21.log21.io:9999/'

@click.command()
def cli():
    json_logs = json.loads(check_output(["21", "log", "--json"]).decode("utf8"))
    token_response = requests.get(url=server_url + 'tokens')
    upload_response = requests.post(url=server_url + 'logs/' + token_response.text, json=json_logs)
    click.echo(json.loads(upload_response.text))
