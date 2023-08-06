import argparse
import configparser

from . import kalshi, manifold, metaculus

parser = argparse.ArgumentParser(
        description="Interface with prediction markets",
        fromfile_prefix_chars='@')
parser.add_argument('-C', '--cache', type=str, help='cache file')
parser.add_argument('-S', '--secrets', type=argparse.FileType('r'), help='secrets file')

subparsers = parser.add_subparsers(title='Methods', required=True)

def autotrade(manifold, args):
    pass

def search(manifold, args):
    manifold.get_markets()

def statistics(manifold, args):
    manifold.get_markets()
    print(len(manifold.markets))

parser_autotrade = subparsers.add_parser('autotrade', help='A conservative automatic trading strategy')
parser_autotrade.set_defaults(func=autotrade)

parser_search = subparsers.add_parser('search', help='Search for markets')
parser_search.set_defaults(func=search)

parser_statistics = subparsers.add_parser('statistics', help='Print statistics')
parser_statistics.set_defaults(func=statistics)

args = parser.parse_args()

# TODO turn this into an action, which will then automatically support multiple
# secrets files
secrets = configparser.ConfigParser()
if args.secrets is not None:
    secrets.read_file(args.secrets)

manifold_auth = None
if 'Manifold' in secrets:
    if 'Key' in secrets['Manifold']:
        manifold_auth = f"Key {secrets['Manifold']['Key']}"
mani = manifold.Manifold(auth=manifold_auth)
args.func(mani, args)


