import sys
import json
import click
from two1.commands.config import Config
from two1.lib.wallet import Wallet
from two1.lib.bitrequests import BitTransferRequests

wallet = Wallet()
username = Config().username
requests = BitTransferRequests(wallet, username)
server_url = 'http://21.log21.io:9999/'

@click.command()
def cli():
    #21 log --json > $HOME/log21.json && curl -XPOST -H'Content-Type: application/json' http://21.log21.io:9999/logs/$(21 buy url http://21.log21.io:9999/tokens | sed -n 1p) -d @$HOME/log21.json && rm $HOME/log21.json
    #sel_url = server_url+'tips/{}?amount={}'.format(username, amount)
    #click.echo(json.loads(requests.get(url=sel_url).text))
    
