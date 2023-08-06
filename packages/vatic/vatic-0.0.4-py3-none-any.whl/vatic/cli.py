import re
from tqdm import tqdm

def autotrade(manifold, args):
    pass

def pairs(manifold, args):
    manifold.get_markets()
    def words(s):
        return list(filter(lambda w: len(w)>0, re.split('[^A-Za-z]', s)))
    # Construct a frequency table:
    freq = {}
    for m in manifold.markets:
        for w in words(m.question):
            if w not in freq:
                freq[w] = 0
            freq[w] += 1

    mkts = list(filter(lambda m: not m.isResolved, manifold.markets))
    for idx, m1 in enumerate(mkts):
        words1 = words(m1.question)
        for m2 in mkts[:idx]:
            words2 = words(m2.question)
            count = sum([1/freq[w1] for w1 in words1 for w2 in words2 if w1 == w2])
            if count >= 1.2:
                print(f'{count:.2} | {m1.question} | {m2.question}')

def search(manifold, args):
    manifold.get_markets()
    for m in manifold.markets:
        if args.open:
            if m.isResolved:
                continue
        s = f'{m.question}\n{m.description}'
        if args.query in s:
            print(m.question)

def statistics(manifold, args):
    manifold.get_markets()
    print(f'{len(manifold.markets)} markets')

def unusual(manifold, args):
    manifold.get_markets()
    mkts = manifold.markets
    if args.open:
        mkts = list(filter(lambda m: not m.isResolved, mkts))
    for m in tqdm(mkts, desc='Fetching'):
        m._get()
    # TODO

def main():
    import argparse
    import configparser

    from . import kalshi, manifold, metaculus

    parser = argparse.ArgumentParser(
            description="Interface with prediction markets",
            fromfile_prefix_chars='@')
    parser.add_argument('-C', '--cache', type=str, help='cache file')
    parser.add_argument('-S', '--secrets', type=argparse.FileType('r'), help='secrets file')

    subparsers = parser.add_subparsers(title='Methods', required=True)

    parser_autotrade = subparsers.add_parser('autotrade', help='A conservative automatic trading strategy')
    parser_autotrade.set_defaults(func=autotrade)

    parser_pairs = subparsers.add_parser('pairs', help='Search for pairs of markets')
    parser_pairs.set_defaults(func=pairs)

    parser_search = subparsers.add_parser('search', help='Search for markets')
    parser_search.add_argument('-O', '--open', action='store_true', help='Limit to open markets')
    parser_search.add_argument('query', help='terms to search')
    parser_search.set_defaults(func=search)

    parser_statistics = subparsers.add_parser('statistics', help='Print statistics')
    parser_statistics.set_defaults(func=statistics)

    parser_unusual = subparsers.add_parser('unusual', help='Scan for anomalous probabilities')
    parser_unusual.add_argument('-O', '--open', action='store_true', help='Limit to open markets')
    parser_unusual.set_defaults(func=unusual)

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


