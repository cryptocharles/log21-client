import sys
import json
import click
import two1
import sqlite3
from two1.commands.util import bitcoin_computer
from two1.commands.config import Config
from two1.commands import status
from two1.server import rest_client
from two1.server import machine_auth_wallet
from two1.commands.util import config as two1_config
from two1.commands.util import wallet as wallet_utils
from two1.commands.util import account as account_utils
from two1.commands.util import uxstring
from two1.commands.util import exceptions
from two1.wallet import Wallet
from two1.bitrequests import BitTransferRequests

wallet = Wallet()
username = Config().username
requests = BitTransferRequests(wallet, username)
server_url = 'http://21.log21.io:9999/'

def initialize_client():
    uuid = bitcoin_computer.get_device_uuid()
    if uuid:
        two1.TWO1_DEVICE_ID = uuid
    try:
        config = two1_config.Config(two1.TWO1_CONFIG_FILE, dict())
        ctx = dict()
    except exceptions.FileDecodeError as e:
        raise click.ClickException(uxstring.UxString.Error.file_decode.format((str(e))))
    wallet = wallet_utils.get_or_create_wallet(config.wallet_path)
    machine_auth = machine_auth_wallet.MachineAuthWallet(wallet)
    config.username = account_utils.get_or_create_username(config, machine_auth)
    client = rest_client.TwentyOneRestClient(two1.TWO1_HOST, machine_auth, config.username)
    ctx['client'] = client
    ctx['config'] = config
    ctx['wallet'] = wallet
    return ctx;

def status_wallet(client, wallet):
    result = status.status_wallet(client, wallet)
    address_balances = wallet.balances_by_address(0)
    status_addresses = []
    for addr, balances in address_balances.items():
        if balances['confirmed'] > 0 or balances['total'] > 0:
            status_addresses.append(dict(address=addr, confirmed=balances['confirmed'], total=balances['total']))
    result['addresses'] = status_addresses
    return result

def inbox(client, config):
    resp = client.get_notifications(config.username, detailed=True)
    resp_json = resp.json()
    if "messages" not in resp_json:
        return []
    unreads = resp_json["messages"]["unreads"]
    reads = resp_json["messages"]["reads"]
    return unreads + reads;

def all_logs():
    ctx = initialize_client()
    client = ctx['client']
    config = ctx['config']
    wallet = ctx['wallet']
    result = dict()
    result['mining'] = status.status_mining(client)
    result['wallet'] = status_wallet(client, wallet)
    result['account'] = status.status_account(config, wallet)
    result['logs'] = client.get_earning_logs()['logs']
    result['earning'] = client.get_earnings()
    result['inbox'] = inbox(client, config)
    return result

def sensor_measurements(db):
    measurements_count = 60 * 24
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    res = cursor.execute('SELECT * FROM Barometer ORDER BY Id DESC LIMIT (?);', (measurements_count,))
    data = res.fetchall()
    conn.close()
    barometer_package = []
    for x in range(0, len(data)):
        barometer_package.append({
            'timestamp': data[x][1],
            'temperature': data[x][2],
            'pressure': data[x][3]
        })
    return json.dumps(barometer_package)

@click.command()
@click.option("--db", default='/home/twenty/sensor21/measurements.db')
def cli_sensor(db):
    json_logs = sensor_measurements(db)
    token_response = requests.get(url=server_url + 'tokens')
    upload_response = requests.post(url=server_url + 'measurements/' + token_response.text, json=json_logs)
    click.echo(json.loads(upload_response.text))

@click.command()
def cli():
    json_logs = json.loads(json.dumps(all_logs()))
    token_response = requests.get(url=server_url + 'tokens')
    upload_response = requests.post(url=server_url + 'all-logs/' + token_response.text, json=json_logs)
    click.echo(json.loads(upload_response.text))
