import httpx

class Bet:
    def __init__(self):
        pass

class Market:
    def __init__(self, manifold, data):
        self.manifold = manifold
        self._data = data
        self.id = data['id']
        self.question = data['question']
        self.isResolved = data['isResolved']
        self.lite = True

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
        return httpx.get(f'{self.dest}/{endpoint}', *args, headers=self.headers, **kwargs)
    
    def _post(self, endpoint, *args, **kwargs):
        return httpx.post(f'{self.dest}/{endpoint}', *args, headers=self.headers, **kwargs)

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

    def get_slug(self):
        # TODO look up a market by slug
        pass

    def bet(self, market, amount, outcome):
        """ Place a bet.
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

