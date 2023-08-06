"""
Interfacing with Manifold Markets.
"""

import httpx

class Bet:
    def __init__(self, data):
        pass

class Market:
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

    def _get(self):
        dat = self.manifold._get(f'market/{self.id}').json()
        self.__init__(self.manifold, dat)

    def bet(self, amount, outcome):
        """ Place a bet.
        """
        return self.manifold.bet(self, amount, outcome)

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
        self.markets = []
        before = None
        while len(mkts := [Market(self, d) for d in self._get_markets(before)]) > 0:
            self.markets += mkts
            before = mkts[-1].id
        return self.markets

    def _get_slug(self, slug):
        """ Return a `Market` object from the given slug.

        This makes a `GET` request to `/slug`.
        """
        return Market(self, self._get(f'slug/{slug}').json())

    def bet(self, market, amount, outcome):
        """ Place a bet.

        Args:
            self:
            market:
            amount:
            outcome:

        Returns:
            The outcome of the bet

        Raises:
            Error: if something failed
        """
        if isinstance(market, Market):
            market = market.id
        # TODO

    def binary_market(self, question, description, closeTime, tags, initialProb=50):
        """ Create a binary market.
        """
        outcomeType = 'BINARY'
        # TODO
        pass

    def free_response_market(self, question, description, closeTime, tags):
        """ Create a free response market.
        """
        outcomeType = 'FREE_RESPONSE'
        # TODO
        pass

