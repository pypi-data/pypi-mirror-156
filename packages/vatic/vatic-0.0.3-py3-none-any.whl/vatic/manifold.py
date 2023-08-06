"""
Interfacing with Manifold Markets.
"""

import httpx

class User:
    """ Represents a user on Manifold.
    """
    def __init__(self, data):
        self._data = data

class Bet:
    """ Represents a bet made on Manifold.
    """
    def __init__(self, data):
        self._data = data

class Market:
    """ Represents a market posted to Manifold.
    """
    def __init__(self, manifold, data):
        self.manifold = manifold
        self._data = data
        self.id = data['id']
        self.question = data['question']
        self.description = data['description']
        self.isResolved = data['isResolved']
        self.lite = True
        if 'bets' in data:
            self.bets = []
            for b in data['bets']:
                self.bets.append(Bet(b))
        if 'probability' in data:
            self.probability = float(data['probability'])

    def _get(self):
        dat = self.manifold._get(f'market/{self.id}').json()
        self.__init__(self.manifold, dat)

    def bet(self, amount, outcome):
        """ Place a bet.

        This is an alias for the corresponding call to the parent :class:`Manifold` instance.
        """
        return self.manifold.bet(self, amount, outcome)

class BinaryMarket(Market):
    pass

class FreeResponseMarket(Market):
    pass

class Manifold:
    def __init__(self, auth=None, dest='https://manifold.markets/api/v0'):
        self.auth = auth
        self.dest = dest

        self.headers = {}
        if self.auth is not None:
            self.headers['Authorization'] = self.auth

    def _get(self, endpoint, *args, **kwargs):
        return httpx.get(f'{self.dest}/{endpoint}', *args, headers=self.headers, timeout=10, **kwargs)
    
    def _post(self, endpoint, *args, **kwargs):
        return httpx.post(f'{self.dest}/{endpoint}', *args, headers=self.headers, timeout=10, **kwargs)

    def _get_markets(self, before=None):
        params = {}
        if before is not None:
            params['before'] = before
        return self._get('markets', params=params).json()

    def get_markets(self):
        """ Fetch list of markets.
        """
        self.markets = []
        before = None
        while len(mkts := [Market(self, d) for d in self._get_markets(before)]) > 0:
            self.markets += mkts
            before = mkts[-1].id
        return self.markets

    def get_users(self):
        """ Fetch a list of users.
        """
        self.users = [User(d) for d in self._get('users').json()]

    def _get_slug(self, slug):
        """ Return a `Market` object from the given slug.

        This makes a `GET` request to `/slug`.
        """
        return Market(self, self._get(f'slug/{slug}').json())

    def bet(self, market, amount, outcome):
        """ Place a bet.

        Args:
            market: The market on which to place a bet. This can be either
                a :class:`Market` or a string with the market ID.
            amount: The amount of M$ to bet.
            outcome: The expected outcome.

        Returns:
            The outcome of the bet.

        Raises:
            Error: if something failed.
        """
        if isinstance(market, Market):
            market = market.id
        dat = {
                'contractId': market,
                'amount': amount,
                'outcome': outcome,
        }
        response = self._post('bet', json=dat)
        return response.json()

    def binary_market(self, question, description, closeTime, tags, initialProb=50):
        """ Create a binary market.
        """
        outcomeType = 'BINARY'
        raise NotImplementedError()
        # TODO

    def free_response_market(self, question, description, closeTime, tags):
        """ Create a free response market.
        """
        outcomeType = 'FREE_RESPONSE'
        raise NotImplementedError()
        # TODO

