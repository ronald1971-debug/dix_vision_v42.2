DEFAULT_API_URL = "https://api.uniswap.org/v1"

class QuoteRequest:
    def __init__(self, token_in, token_out, amount):
        self.token_in = token_in
        self.token_out = token_out
        self.amount = amount

class UniswapXError(Exception):
    pass

class UniswapXQuoteClient:
    """Client for UniswapX quote API."""
    def __init__(self, base_url=DEFAULT_API_URL, api_key=None):
        self.base_url = base_url
        self.api_key = api_key

    def healthcheck(self):
        """Check if the API is healthy."""
        return True