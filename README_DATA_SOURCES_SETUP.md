# DIX VISION DATA SOURCES - SETUP GUIDE

## 🎯 **COMPLETE SETUP INSTRUCTIONS**

This guide provides step-by-step instructions for setting up all 94 data sources in the DIX VISION system, including:
- How to create accounts/profiles on each platform
- How to get API access
- Required API keys and credentials
- Special requirements (developer accounts, business accounts, etc.)
- Costs and pricing tiers
- Configuration instructions

---

## 📋 **QUICK REFERENCE**

### **Free / No Key Required** (25 sources)
- SEC 13F, ArXiv, CBOE, StockTwits, NVD CVE, BSE
- Telegram, Viber
- CoinGecko, Frankfurter (for basic usage)
- And 15+ others (see detailed list below)

### **Freemium / Optional Key** (40 sources)
- Seeking Alpha, TipRanks, FRED, Alpha Vantage
- Binance, Kraken (for enhanced features)
- And 35+ others

### **Paid / Subscription Required** (8 sources)
- Bloomberg Terminal (enterprise)
- AlphaSense (enterprise)
- Whale Alert (required)
- CryptoQuant (freemium, paid for full)
- Weibo (Chinese developer account)
- WeChat (business account)
- Douyin (approval required)
- Snapchat (approval required)

### **Limited / Approval Required** (21 sources)
- Various platforms requiring approval
- Alternative platforms (Parler, Truth Social)

---

## 📊 **DETAILED SETUP INSTRUCTIONS**

---

## 🪙 **CRYPTO SOURCES (19 sources)**

### **1. CoinGecko** (FREE - No Key Required for Basic)
- **Sign Up**: https://www.coingecko.com/en/api
- **API Access**: No key required for basic tier (10-30 calls/min)
- **Enhanced Access**: Create free account for higher rate limits
- **Cost**: Free
- **Setup**:
  1. No setup required for basic usage
  2. Optional: Create account at https://www.coingecko.com/en/dashboard
  3. Get API key from dashboard for enhanced limits
- **Environment Variable**: `COINGECKO_API_KEY=your_key_here` (optional)
- **Documentation**: https://www.coingecko.com/en/api/docs

### **2. Binance** (FREE - No Key for Market Data)
- **Sign Up**: https://www.binance.com/en
- **API Access**: Create account, enable API in profile settings
- **Cost**: Free for public market data
- **Setup**:
  1. Create account at https://www.binance.com/en/register
  2. Go to "API Management" in profile
  3. Create new API key
  4. Enable "Spot & Margin Trading" and "Reading" permissions
- **Environment Variable**: `BINANCE_API_KEY=your_key_here`
- **Security**: Restrict IP addresses, enable 2FA
- **Documentation**: https://binance-docs.github.io/apidocs/

### **3. Kraken** (FREE - No Key for Market Data)
- **Sign Up**: https://www.kraken.com/sign-up
- **API Access**: Create account, generate API keys
- **Cost**: Free for public market data
- **Setup**:
  1. Create account at https://www.kraken.com/signup
  2. Go to Settings > API > Create New Key
  3. Enable "Query" permission
- **Environment Variable**: `KRAKEN_API_KEY=your_key_here`
- **Security**: Use API key, not secret key for read-only
- **Documentation**: https://docs.kraken.com/rest/

### **4. CoinMarketCap** (FREEMIUM)
- **Sign Up**: https://coinmarketcap.com/api/
- **API Access**: Create account, get API key from dashboard
- **Cost**: Free tier (10,000 calls/month), Paid tiers available
- **Setup**:
  1. Create account at https://coinmarketcap.com/api/
  2. Go to dashboard > API Keys
  3. Create new API key
- **Environment Variable**: `COINMARKETCAP_API_KEY=your_key_here`
- **Documentation**: https://coinmarketcap.com/api/documentation/v1/

### **5. Coinbase** (FREEMIUM)
- **Sign Up**: https://www.coinbase.com/join
- **API Access**: Create account, enable API in settings
- **Cost**: Free for basic data
- **Setup**:
  1. Create account at https://www.coinbase.com/join
  2. Go to Settings > API
  3. Create new API key
- **Environment Variable**: `COINBASE_API_KEY=your_key_here`
- **Security**: Enable 2FA, restrict IP
- **Documentation**: https://docs.cloud.coinbase.com/exchange/

### **6. CoinPaprika** (FREE)
- **Sign Up**: https://coinpaprika.com/
- **API Access**: No key required for basic tier
- **Cost**: Free
- **Setup**: No setup required for basic usage
- **Enhanced**: Create account for higher rate limits
- **Documentation**: https://api.coinpaprika.com/

### **7. CryptoCompare** (FREEMIUM)
- **Sign Up**: https://www.cryptocompare.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (100,000 calls/month)
- **Setup**:
  1. Create account at https://www.cryptocompare.com/
  2. Go to account > API Keys
  3. Generate API key
- **Environment Variable**: `CRYPTOCOMPARE_API_KEY=your_key_here`
- **Documentation**: https://min-api.cryptocompare.com/

### **8. CoinCap** (FREE)
- **Sign Up**: https://coincap.io/
- **API Access**: No key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://docs.coincap.io/

### **9. Nomics** (FREEMIUM)
- **Sign Up**: https://nomics.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (100 calls/day)
- **Setup**:
  1. Create account at https://nomics.com/
  2. Get API key from dashboard
- **Environment Variable**: `NOMICS_API_KEY=your_key_here`
- **Documentation**: https://docs.nomics.com/

### **10. Glassnode** (FREEMIUM)
- **Sign Up**: https://glassnode.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://glassnode.com/
  2. Get API key from account settings
- **Environment Variable**: `GLASSNODE_API_KEY=your_key_here`
- **Documentation**: https://docs.glassnode.com/

### **11. Messari** (FREEMIUM)
- **Sign Up**: https://messari.io/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://messari.io/
  2. Get API key from account
- **Environment Variable**: `MESSARI_API_KEY=your_key_here`
- **Documentation**: https://docs.messari.io/

### **12. Santiment** (FREEMIUM)
- **Sign Up**: https://santiment.net/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://santiment.net/
  2. Get API key from account settings
- **Environment Variable**: `SANTIMENT_API_KEY=your_key_here`
- **Documentation**: https://docs.santiment.net/

### **13. IntoTheBlock** (FREEMIUM)
- **Sign Up**: https://intotheplock.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://intotheplock.com/
  2. Get API key from dashboard
- **Environment Variable**: **INTOTHEBLOCK_API_KEY=your_key_here**
- **Documentation**: https://docs.intotheplock.com/

### **14. CoinMetrics** (FREEMIUM)
- **Sign Up**: https://coinmetrics.io/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://coinmetrics.io/
  2. Get API key from account
- **Environment Variable**: `COINMETRICS_API_KEY=your_key_here`
- **Documentation**: https://coinmetrics.io/community-api/

### **15. DexScreener** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://docs.dexscreener.com/

### **16. CoinStats** (FREE)
- **Sign Up**: https://coinstats.app/
- **API Access**: No key required for basic tier
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://coinstats.app/api/

### **17. CoinLore** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://www.coinlore.com/

### **18. BraveNewCoin** (FREEMIUM)
- **Sign Up**: https://bravenewcoin.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://bravenewcoin.com/
  2. Get API key from account
- **Environment Variable**: `BRAVENEWCOIN_API_KEY=your_key_here`
- **Documentation**: https://api.bravenewcoin.com/

### **19. DEXTools** (FREE)
- **Sign Up**: Not required for basic
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required for basic usage
- **Documentation**: https://www.dextools.io/

### **20. Bybit** (FREE - No Key for Market Data)
- **Sign Up**: https://www.bybit.com/
- **API Access**: Create account, enable API
- **Cost**: Free for public market data
- **Setup**:
  1. Create account at https://www.bybit.com/
  2. Go to API > Create API Key
- **Environment Variable**: `BYBIT_API_KEY=your_key_here`
- **Documentation**: https://bybit-exchange.github.io/docs/

### **21. Whale Alert** (PAID - REQUIRED)
- **Sign Up**: https://whale-alert.io/
- **API Access**: Create account, purchase subscription
- **Cost**: $9.99/month (Basic), $24.99/month (Pro)
- **Setup**:
  1. Create account at https://whale-alert.io/
  2. Purchase subscription
  3. Get API key from account dashboard
- **Environment Variable**: `WHALE_ALERT_API_KEY=your_key_here` (REQUIRED)
- **Documentation**: https://docs.whale-alert.io/

### **22. CryptoQuant** (FREEMIUM)
- **Sign Up**: https://cryptoquant.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://cryptoquant.com/
  2. Get API key from account settings
- **Environment Variable**: `CRYPTOQUANT_API_KEY=your_key_here`
- **Documentation**: https://docs.cryptoquant.com/

---

## 💱 **FOREX SOURCES (10 sources)**

### **1. ExchangeRate-API** (FREE - No Key for Basic)
- **Sign Up**: https://www.exchangerate-api.com/
- **API Access**: No key required for free tier
- **Cost**: Free (1000 requests/month), Paid tiers available
- **Setup**: No setup required for basic usage
- **Enhanced**: Create account for higher limits
- **Environment Variable**: `EXCHANGERATE_API_KEY=your_key_here` (optional)
- **Documentation**: https://www.exchangerate-api.com/docs/

### **2. Frankfurter** (FREE - No Key Required)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://api.frankfurter.app/

### **3. Alpha Vantage** (FREEMIUM)
- **Sign Up**: https://www.alphavantage.co/support/#api-key
- **API Access**: Create account, get API key
- **Cost**: Free (25 requests/day), Paid tiers available
- **Setup**:
  1. Create account at https://www.alphavantage.co/support/#api-key
  2. Get free API key via email
- **Environment Variable**: `ALPHAVANTAGE_API_KEY=your_key_here`
- **Documentation**: https://www.alphavantage.co/documentation/

### **4. TrueFX** (FREE)
- **Sign Up**: https://www.truefx.com/
- **API Access**: Create account for access
- **Cost**: Free for historical data
- **Setup**:
  1. Create account at https://www.truefx.com/
  2. Download API credentials
- **Environment Variable**: `TRUEFX_API_KEY=your_key_here`
- **Documentation**: https://www.truefx.com/?page=api

### **5. XE** (FREEMIUM)
- **Sign Up**: https://www.xe.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.xe.com/
  2. Get API key from account
- **Environment Variable**: `XE_API_KEY=your_key_here`
- **Documentation**: https://www.xe.com/api/

### **6. OANDA** (FREEMIUM)
- **Sign Up**: https://www.oanda.com/
- **API Access**: Create account, generate API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.oanda.com/
  2. Go to Account > Manage API Access
  3. Generate API key
- **Environment Variable**: `OANDA_API_KEY=your_key_here`
- **Documentation**: https://developer.oanda.com/

### **7. OpenExchangeRates** (FREEMIUM)
- **Sign Up**: https://openexchangerates.org/
- **API Access**: Create account, get API key
- **Cost**: Free (1000 requests/month), Paid tiers available
- **Setup**:
  1. Create account at https://openexchangerates.org/
  2. Get API key from account
- **Environment Variable**: `OPENEXCHANGERATES_API_KEY=your_key_here`
- **Documentation**: https://docs.openexchangerates.org/

### **8. Fixer** (FREEMIUM)
- **Sign Up**: https://fixer.io/
- **API Access**: Create account, get API key
- **Cost**: Free (1000 requests/month), Paid tiers available
- **Setup**:
  1. Create account at https://fixer.io/
  2. Get API key from account
- **Environment Variable**: `FIXER_API_KEY=your_key_here`
- **Documentation**: https://fixer.io/documentation/

### **9. CurrencyLayer** (FREEMIUM)
- **Sign Up**: https://currencylayer.com/
- **API Access**: Create account, get API key
- **Cost**: Free (1000 requests/month), Paid tiers available
- **Setup**:
  1. Create account at https://currencylayer.com/
  2. Get API key from account
- **Environment Variable**: `CURRENCYLAYER_API_KEY=your_key_here`
- **Documentation**: https://currencylayer.com/documentation/

### **10. Finage** (FREEMIUM)
- **Sign Up**: https://finage.co.uk/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://finage.co.uk/
  2. Get API key from account
- **Environment Variable**: `FINAGE_API_KEY=your_key_here`
- **Documentation**: https://finage.co.uk/documentation/

---

## 📈 **STOCKS/ALPHA SOURCES (7 sources)**

### **1. Tiingo** (FREEMIUM)
- **Sign Up**: https://api.tiingo.com/
- **API Access**: Create account, get API key
- **Cost**: Free (500 requests/day), Paid tiers available
- **Setup**:
  1. Create account at https://api.tiingo.com/
  2. Get API key from dashboard
- **Environment Variable**: `TIINGO_API_KEY=your_key_here`
- **Documentation**: https://api.tiingo.com/documentation/

### **2. IEX Cloud** (FREEMIUM)
- **Sign Up**: https://iexcloud.io/
- **API Access**: Create account, get publishable token
- **Cost**: Free (100,000 requests/month), Paid tiers available
- **Setup**:
  1. Create account at https://iexcloud.io/
  2. Get publishable token from account
- **Environment Variable**: `IEX_PUBLISHABLE_TOKEN=your_token_here`
- **Documentation**: https://iexcloud.io/docs/

### **3. Polygon.io** (FREEMIUM)
- **Sign Up**: https://polygon.io/
- **API Access**: Create account, get API key
- **Cost**: Free (5 requests/minute), Paid tiers available
- **Setup**:
  1. Create account at https://polygon.io/
  2. Get API key from dashboard
- **Environment Variable**: `POLYGON_API_KEY=your_key_here`
- **Documentation**: https://polygon.io/docs/

### **4. Financial Modeling Prep (FMP)** (FREEMIUM)
- **Sign Up**: https://financialmodelingprep.com/
- **API Access**: Create account, get API key
- **Cost**: Free (250 requests/day), Paid tiers available
- **Setup**:
  1. Create account at https://financialmodelingprep.com/
  2. Get API key from account
- **Environment Variable**: `FMP_API_KEY=your_key_here`
- **Documentation**: https://financialmodelingprep.com/developer/docs/

### **5. Yahoo Finance** (FREE - No Key Required)
- **Sign Up**: Not required for basic usage
- **API Access**: yfinance Python library (unofficial)
- **Cost**: Free
- **Setup**:
  1. Install: `pip install yfinance`
  2. No API key required
- **Documentation**: https://github.com/ranaroussi/yfinance

### **6. Quandl** (FREEMIUM)
- **Sign Up**: https://www.quandl.com/
- **API Access**: Create account, get API key
- **Cost**: Free (50,000 calls/day), Paid tiers available
- **Setup**:
  1. Create account at https://www.quandl.com/
  2. Get API key from account settings
- **Environment Variable**: `QUANDL_API_KEY=your_key_here`
- **Documentation**: https://docs.quandl.com/

### **7. SEC EDGAR** (FREE - No Key Required)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Note**: Respect rate limiting (10 requests/second)
- **Documentation**: https://www.sec.gov/edgar/sec-api-documentation

---

## 📊 **MACRO/POLICY SOURCES (7 sources)**

### **1. FRED (Federal Reserve)** (FREEMIUM)
- **Sign Up**: https://fred.stlouisfed.org/
- **API Access**: Create account, get API key
- **Cost**: Free (120 requests/minute), No key required for basic
- **Setup**:
  1. Create account at https://fred.stlouisfed.org/docs/api/api_key.html
  2. Get API key from account
- **Environment Variable**: `FRED_API_KEY=your_key_here` (optional)
- **Documentation**: https://fred.stlouisfed.org/docs/api/fred/

### **2. BLS (Bureau of Labor Statistics)** (FREE)
- **Sign Up**: https://www.bls.gov/developers/
- **API Access**: Register for API key
- **Cost**: Free
- **Setup**:
  1. Register at https://www.bls.gov/developers/register.htm
  2. Get API key via email
- **Environment Variable**: `BLS_API_KEY=your_key_here`
- **Documentation**: https://www.bls.gov/developers/

### **3. US Treasury** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://fiscaldata.treasury.gov/

### **4. CFTC** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://www.cftc.gov/

### **5. CME** (FREE)
- **Sign Up**: https://www.cmegroup.com/
- **API Access**: Create account for data access
- **Cost**: Free for some data, Paid for others
- **Setup**:
  1. Create account at https://www.cmegroup.com/
  2. Request API access
- **Environment Variable**: `CME_API_KEY=your_key_here`
- **Documentation**: https://www.cmegroup.com/

### **6. World Bank** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://datahelpdesk.worldbank.org/

### **7. IMF** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://dataservices.imf.org/

---

## 🌍 **GLOBAL STOCKS SOURCES (10 sources)**

### **1. Morningstar** (FREEMIUM)
- **Sign Up**: https://www.morningstar.com/
- **API Access**: Create account, get API key
- **Cost**: Freemium, Paid tiers available
- **Setup**:
  1. Create account at https://www.morningstar.com/
  2. Request API access
- **Environment Variable**: `MORNINGSTAR_API_KEY=your_key_here`
- **Documentation**: https://www.morningstar.com/api/

### **2. EODHD** (FREEMIUM)
- **Sign Up**: https://eodhd.com/
- **API Access**: Create account, get API key
- **Cost**: Free (2000 requests/day), Paid tiers available
- **Setup**:
  1. Create account at https://eodhd.com/
  2. Get API key from account
- **Environment Variable**: `EODHD_API_KEY=your_key_here`
- **Documentation**: https://eodhd.com/api/

### **3. Investing.com** (FREEMIUM)
- **Sign Up**: https://www.investing.com/
- **API Access**: Create account, get API access
- **Cost**: Freemium, Paid tiers available
- **Setup**:
  1. Create account at https://www.investing.com/
  2. Request API access
- **Environment Variable**: `INVESTING_API_KEY=your_key_here`
- **Documentation**: https://www.investing.com/api/

### **4. Refinitiv** (FREEMIUM)
- **Sign Up**: https://www.refinitiv.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.refinitiv.com/
  2. Get API key from account
- **Environment Variable**: **REFINITIV_API_KEY=your_key_here**
- **Documentation**: https://developers.refinitiv.com/

### **5. Bloomberg** (PAID - ENTERPRISE)
- **Sign Up**: https://www.bloomberg.com/professional/
- **API Access**: Bloomberg Terminal subscription required
- **Cost**: $24,000+ per year
- **Setup**:
  1. Contact Bloomberg sales
  2. Purchase Bloomberg Terminal subscription
  3. Get API credentials from Bloomberg
- **Environment Variable**: `BLOOMBERG_API_KEY=your_key_here`
- **Note**: Enterprise only, very expensive
- **Documentation**: https://www.bloomberg.com/professional/api/

### **6. OpenFIGI** (FREE)
- **Sign Up**: https://www.openfigi.com/
- **API Access**: Create account, get API key
- **Cost**: Free (1000 requests/day)
- **Setup**:
  1. Create account at https://www.openfigi.com/
  2. Get API key from account
- **Environment Variable**: `OPENFIGI_API_KEY=your_key_here`
- **Documentation**: https://www.openfigi.com/

### **7. World Federation of Exchanges** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://www.world-exchanges.org/

### **8. Yahoo Finance Global** (FREE)
- **Sign Up**: Not required
- **API Access**: yfinance library
- **Cost**: Free
- **Setup**: Install yfinance library
- **Documentation**: https://github.com/ranaroussi/yfinance

### **9. MSCI** (PAID)
- **Sign Up**: https://www.msci.com/
- **API Access**: Contact for enterprise access
- **Cost**: Enterprise pricing
- **Setup**:
  1. Contact MSCI sales
  2. Purchase data license
  3. Get API credentials
- **Environment Variable**: `MSCI_API_KEY=your_key_here`
- **Documentation**: https://www.msci.com/

### **10. STOXX** (FREEMIUM)
- **Sign Up**: https://www.stoxx.com/
- **API Access**: Create account, get API key
- **Cost**: Freemium, Paid tiers available
- **Setup**:
  1. Create account at https://www.stoxx.com/
  2. Get API key from account
- **Environment Variable**: `STOXX_API_KEY=your_key_here`
- **Documentation**: https://www.stoxx.com/

---

## 🏦 **NEWS/RESEARCH SOURCES (10 sources)**

### **1. Seeking Alpha** (FREEMIUM)
- **Sign Up**: https://seekingalpha.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://seekingalpha.com/
  2. Go to Account > API Access
  3. Get API key
- **Environment Variable**: `SEEKING_ALPHA_API_KEY=your_key_here`
- **Documentation**: https://seekingalpha.com/api/docs/

### **2. TipRanks** (FREEMIUM)
- **Sign Up**: https://www.tipranks.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.tipranks.com/
  2. Get API key from account settings
- **Environment Variable**: `TIPRANKS_API_KEY=your_key_here`
- **Documentation**: https://www.tipranks.com/api/docs/

### **3. AlphaSense** (PAID - ENTERPRISE)
- **Sign Up**: https://www.alphasense.com/
- **API Access**: Contact for enterprise access
- **Cost**: Enterprise pricing
- **Setup**:
  1. Contact AlphaSense sales
  2. Purchase subscription
  3. Get API credentials
- **Environment Variable**: `ALPHASENSE_API_KEY=your_key_here`
- **Note**: Enterprise only, AI-powered insights
- **Documentation**: https://www.alphasense.com/api/

### **4. Reuters** (FREEMIUM)
- **Sign Up**: https://www.reuters.com/
- **API Access**: Refinitiv API (freemium)
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://developers.refinitiv.com/
  2. Get API key
- **Environment Variable**: `REUTERS_API_KEY=your_key_here`
- **Documentation**: https://developers.refinitiv.com/

### **5. ArXiv** (FREE - No Key Required)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Note**: Respect rate limiting (1 request/3 seconds)
- **Documentation**: http://export.arxiv.org/api_help/

### **6. CoinDesk** (FREE)
- **Sign Up**: Not required
- **API Access**: RSS feed or public API
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://www.coindesk.com/

### **7. GDELT** (FREE - No Key Required)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Note**: Respect rate limiting
- **Documentation**: https://www.gdeltproject.org/api.html

### **8. Bloomberg News** (PAID - ENTERPRISE)
- **Sign Up**: https://www.bloomberg.com/professional/
- **API Access**: Bloomberg Terminal subscription
- **Cost**: $24,000+ per year
- **Setup**: See Bloomberg above
- **Environment Variable**: `BLOOMBERG_NEWS_API_KEY=your_key_here`

### **9. UN Data** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://data.un.org/

### **10. OECD** (FREE)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://data.oecd.org/

---

## 🔐 **SECURITY/SOURCES (3 sources)**

### **1. NVD CVE Database** (FREE - No Key Required)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Note**: Respect rate limiting (5 requests/rolling 30 seconds)
- **Documentation**: https://nvd.nist.gov/developers/request-an-api-key

### **2. GitHub Trending** (FREEMIUM)
- **Sign Up**: https://github.com/
- **API Access**: Create account, get personal access token
- **Cost**: Free (5000 requests/hour), Paid tiers available
- **Setup**:
  1. Create account at https://github.com/
  2. Go to Settings > Developer settings > Personal access tokens
  3. Generate new token
- **Environment Variable**: `GITHUB_TOKEN=your_token_here`
- **Security**: Use personal access token, not password
- **Documentation**: https://docs.github.com/en/rest

### **3. SEC EDGAR (13F)** (FREE - No Key Required)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Note**: Respect rate limiting (10 requests/second)
- **Documentation**: https://www.sec.gov/edgar/sec-api-documentation

---

## 📊 **OPTIONS/SOURCES (2 sources)**

### **1. CBOE Options** (FREE - No Key Required)
- **Sign Up**: Not required
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required
- **Documentation**: https://www.cboe.com/

### **2. Unusual Whales** (FREEMIUM)
- **Sign Up**: https://unusualwhales.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://unusualwhales.com/
  2. Get API key from account
- **Environment Variable**: `UNUSUAL_WHALES_API_KEY=your_key_here`
- **Documentation**: https://unusualwhales.com/api/

---

## 💬 **SOCIAL SENTIMENT SOURCES (2 sources)**

### **1. StockTwits** (FREE - No Key Required)
- **Sign Up**: Not required for basic
- **API Access**: Public API, no key required
- **Cost**: Free
- **Setup**: No setup required for basic usage
- **Enhanced**: Create account for higher limits
- **Documentation**: https://api.stocktwits.com/

### **2. Social Reddit** (FREE - Requires OAuth)
- **Sign Up**: https://www.reddit.com/
- **API Access**: Create app, get OAuth credentials
- **Cost**: Free
- **Setup**:
  1. Create account at https://www.reddit.com/
  2. Go to https://www.reddit.com/prefs/apps
  3. Create app, get client_id and client_secret
- **Environment Variable**: `REDDIT_CLIENT_ID=your_client_id`
- **Environment Variable**: `REDDIT_CLIENT_SECRET=your_client_secret`
- **Documentation**: https://www.reddit.com/dev/api/

---

## 🌏 **INTERNATIONAL SOCIAL PLATFORMS (17 sources)**

### **CHINA (5 sources)**

#### **1. Weibo (Chinese Twitter)** (REQUIRES CHINESE DEVELOPER ACCOUNT)
- **Sign Up**: https://weibo.com/
- **API Access**: Requires Chinese developer account
- **Cost**: Free with Chinese developer account
- **Requirements**: 
  - Chinese phone number or ID
  - Chinese address verification
  - Chinese developer approval
- **Setup**:
  1. Create account at https://weibo.com/
  2. Apply for developer account
  3. Provide Chinese ID/phone verification
  4. Get API key from developer console
- **Environment Variable**: `WEIBO_API_KEY=your_key_here`
- **Note**: Requires Chinese residency or business registration
- **Documentation**: https://open.weibo.com/wiki/

#### **2. WeChat (Super App)** (REQUIRES BUSINESS ACCOUNT)
- **Sign Up**: https://mp.weixin.qq.com/
- **API Access**: WeChat Official Account (business)
- **Cost**: Free for basic business account
- **Requirements**:
  - Chinese business license
  - Business registration
  - Chinese verification
- **Setup**:
  1. Register Official Account at https://mp.weixin.qq.com/
  2. Provide business license
  3. Complete business verification
  4. Get API credentials from dashboard
- **Environment Variable**: `WECHAT_APP_ID=your_app_id`
- **Environment Variable**: `WECHAT_APP_SECRET=your_app_secret`
- **Note**: Requires Chinese business registration
- **Documentation**: https://developers.weixin.qq.com/doc/

#### **3. Douyin (Chinese TikTok)** (REQUIRES APPROVAL)
- **Sign Up**: https://www.douyin.com/
- **API Access**: Requires approval
- **Cost**: Free with approval
- **Requirements**:
  - Chinese phone number
  - Approval from Douyin
- **Setup**:
  1. Create account at https://www.douyin.com/
  2. Apply for developer access
  3. Wait for approval
  4. Get API credentials
- **Environment Variable**: `DOUYIN_API_KEY=your_key_here`
- **Note**: Approval process can take time
- **Documentation**: https://developer.open-douyin.com/

#### **4. Bilibili (Chinese YouTube)** (FREEMIUM)
- **Sign Up**: https://www.bilibili.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.bilibili.com/
  2. Go to account settings
  3. Apply for developer access
  4. Get API key
- **Environment Variable**: `BILIBILI_API_KEY=your_key_here`
- **Documentation**: https://api.bilibili.com/

#### **5. Zhihu (Chinese Quora)** (FREEMIUM)
- **Sign Up**: https://www.zhihu.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.zhihu.com/
  2. Go to settings > developer
  3. Get API key
- **Environment Variable**: `ZHIHU_API_KEY=your_key_here`
- **Documentation**: https://www.zhihu.com/

---

### **INDIA (3 sources)**

#### **6. ShareChat (India)** (FREEMIUM)
- **Sign Up**: https://www.sharechat.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.sharechat.com/
  2. Go to developer section
  3. Apply for API access
  4. Get API key
- **Environment Variable**: `SHARECHAT_API_KEY=your_key_here`
- **Documentation**: https://www.sharechat.com/api/

#### **7. Koo (Indian Twitter Alternative)** (FREEMIUM)
- **Sign Up**: https://www.kooapp.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://www.kooapp.com/
  2. Go to developer section
  3. Get API key
- **Environment Variable**: `KOO_API_KEY=your_key_here`
- **Documentation**: https://www.kooapp.com/developers/

#### **8. Chingari (Indian Short Video)** (LIMITED)
- **Sign Up**: https://www.chingari.io/
- **API Access**: Limited access, requires approval
- **Cost**: Free with approval
- **Setup**:
  1. Create account at https://www.chingari.io/
  2. Apply for developer access
  3. Wait for approval
- **Environment Variable**: `CHINGARI_API_KEY=your_key_here`
- **Note**: Approval required
- **Documentation**: https://www.chingari.io/api/

---

### **RUSSIA (3 sources)**

#### **9. VK (Russian Facebook)** (FREEMIUM)
- **Sign Up**: https://vk.com/
- **API Access**: Create account, generate API key
- **Cost**: Free
- **Setup**:
  1. Create account at https://vk.com/
  2. Go to https://vk.com/dev
  3. Create standalone app
  4. Get API credentials
- **Environment Variable**: `VK_API_KEY=your_key_here`
- **Documentation**: https://vk.com/dev/

#### **10. Telegram (Russia/Global)** (FREE - Bot API)
- **Sign Up**: https://telegram.org/
- **API Access**: Create bot, get bot token
- **Cost**: Free
- **Setup**:
  1. Create Telegram account
  2. Message @BotFather
  3. Create new bot with /newbot
  4. Get bot token
- **Environment Variable**: `TELEGRAM_BOT_TOKEN=your_bot_token_here`
- **Documentation**: https://core.telegram.org/bots/api

#### **11. Yandex Zen (Russian Content)** (FREEMIUM)
- **Sign Up**: https://zen.yandex.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://zen.yandex.com/
  2. Go to developer section
  3. Get API key
- **Environment Variable**: `YANDEX_ZEN_API_KEY=your_key_here`
- **Documentation**: https://zen.yandex.ru/api/

---

### **ASIA (2 sources)**

#### **12. Line (Japan/Asia)** (FREEMIUM)
- **Sign Up**: https://developers.line.biz/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://developers.line.biz/
  2. Create new channel
  3. Get API credentials
- **Environment Variable**: `LINE_CHANNEL_ACCESS_TOKEN=your_token_here`
- **Documentation**: https://developers.line.biz/

#### **13. KakaoTalk (South Korea)** (FREEMIUM)
- **Sign Up**: https://developers.kakao.com/
- **API Access**: Create account, get API key
- **Cost**: Free tier (limited), Paid tiers available
- **Setup**:
  1. Create account at https://developers.kakao.com/
  2. Create new app
  3. Get API key
- **Environment Variable**: `KAKAO_API_KEY=your_key_here`
- **Documentation**: https://developers.kakao.com/

---

### **GLOBAL/ALTERNATIVE (4 sources)**

#### **14. Snapchat (Global Gen Z)** (LIMITED - Requires Approval)
- **Sign Up**: https://marketing.snapchat.com/
- **API Access**: Create account, apply for approval
- **Cost**: Free with approval
- **Setup**:
  1. Create account at https://marketing.snapchat.com/
  2. Apply for developer access
  3. Wait for approval
  4. Get API credentials
- **Environment Variable**: `SNAPCHAT_API_KEY=your_key_here`
- **Note**: Approval process can take weeks
- **Documentation**: https://docs.snap.com/

#### **15. Viber (Eastern Europe/Middle East)** (FREE - Bot API)
- **Sign Up**: https://partners.viber.com/
- **API Access**: Create bot, get API key
- **Cost**: Free
- **Setup**:
  1. Create account at https://partners.viber.com/
  2. Create new bot
  3. Get API credentials
- **Environment Variable**: `VIBER_AUTH_TOKEN=your_token_here`
- **Documentation**: https://developers.viber.com/

#### **16. Parler (Alternative Platform)** (LIMITED)
- **Sign Up**: https://parler.com/
- **API Access**: Limited, requires approval
- **Cost**: Free with approval
- **Setup**:
  1. Create account at https://parler.com/
  2. Apply for API access
  3. Wait for approval
- **Environment Variable**: `PARLER_API_KEY=your_key_here`
- **Note**: API availability limited
- **Documentation**: https://parler.com/api/

#### **17. Truth Social (Alternative Platform)** (LIMITED)
- **Sign Up**: https://truthsocial.com/
- **API Access**: Limited, requires approval
- **Cost**: Free with approval
- **Setup**:
  1. Create account at https://truthsocial.com/
  2. Apply for API access
  3. Wait for approval
- **Environment Variable**: `TRUTH_SOCIAL_API_KEY=your_key_here`
- **Note**: API availability limited
- **Documentation**: https://truthsocial.com/developers/

---

## 📝 **ENVIRONMENT CONFIGURATION**

### **.dix_secrets.env File**

Create or update `.dix_secrets.env` in the project root with your API keys:

```bash
# Crypto Sources (Recommended)
COINGECKO_API_KEY=your_coingecko_key
BINANCE_API_KEY=your_binance_key
KRAKEN_API_KEY=your_kraken_key
WHALE_ALERT_API_KEY=your_whale_alert_key  # REQUIRED
CRYPTOQUANT_API_KEY=your_cryptoquant_key

# Forex Sources
ALPHAVANTAGE_API_KEY=your_alphavantage_key
EXCHANGERATE_API_KEY=your_exchangerate_key

# Stock/Alpha Sources
TIINGO_API_KEY=your_tiingo_key
IEX_PUBLISHABLE_TOKEN=your_iex_token
POLYGON_API_KEY=your_polygon_key
FMP_API_KEY=your_fmp_key

# Macro Sources
FRED_API_KEY=your_fred_key
BLS_API_KEY=your_bls_key

# News/Research Sources
SEEKING_ALPHA_API_KEY=your_seeking_alpha_key
TIPRANKS_API_KEY=your_tipranks_key
ALPHASENSE_API_KEY=your_alphasense_key  # Enterprise
REUTERS_API_KEY=your_reuters_key
BLOOMBERG_API_KEY=your_bloomberg_key  # Enterprise

# Security/Sources
GITHUB_TOKEN=your_github_token

# Options Sources
UNUSUAL_WHALES_API_KEY=your_unusual_whales_key

# Social Sources
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret

# International Social Platforms
WEIBO_API_KEY=your_weibo_key  # Chinese developer account
WECHAT_APP_ID=your_wechat_app_id
WECHAT_APP_SECRET=your_wechat_app_secret
DOUYIN_API_KEY=your_douyin_key
BILIBILI_API_KEY=your_bilibili_key
ZHIHU_API_KEY=your_zhihu_key
SHARECHAT_API_KEY=your_sharechat_key
KOO_API_KEY=your_koo_key
CHINGARI_API_KEY=your_chingari_key
VK_API_KEY=your_vk_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
YANDEX_ZEN_API_KEY=your_yandex_zen_key
LINE_CHANNEL_ACCESS_TOKEN=your_line_token
KAKAO_API_KEY=your_kakao_key
SNAPCHAT_API_KEY=your_snapchat_key
VIBER_AUTH_TOKEN=your_viber_token
PARLER_API_KEY=your_parler_key
TRUTH_SOCIAL_API_KEY=your_truth_social_key

# Other Sources (add as needed)
COINMARKETCAP_API_KEY=your_coinmarketcap_key
COINBASE_API_KEY=your_coinbase_key
CRYPTOCOMPARE_API_KEY=your_cryptocompare_key
NOMICS_API_KEY=your_nomics_key
GLASSNODE_API_KEY=your_glassnode_key
MESSARI_API_KEY=your_messari_key
SANTIMENT_API_KEY=your_santiment_key
INTOTHEBLOCK_API_KEY=your_intotheplock_key
COINMETRICS_API_KEY=your_coinmetrics_key
TRUEFX_API_KEY=your_truefx_key
XE_API_KEY=your_xe_key
OANDA_API_KEY=your_oanda_key
OPENEXCHANGERATES_API_KEY=your_openexchangerates_key
FIXER_API_KEY=your_fixer_key
CURRENCYLAYER_API_KEY=your_currencylayer_key
FINAGE_API_KEY=your_finage_key
MORNINGSTAR_API_KEY=your_morningstar_key
EODHD_API_KEY=your_eodhd_key
INVESTING_API_KEY=your_investing_key
REFINITIV_API_KEY=your_refinitiv_key
OPENFIGI_API_KEY=your_openfigi_key
STOXX_API_KEY=your_stoxx_key
MORNINGSTAR_API_KEY=your_morningstar_key
MSCI_API_KEY=your_msci_key
WORLDBANK_API_KEY=your_worldbank_key
IMF_API_KEY=your_imf_key
OECD_API_KEY=your_oecd_key
UN_API_KEY=your_un_key
TREASURY_API_KEY=your_treasury_key
CFTC_API_KEY=your_cftc_key
CME_API_KEY=your_cme_key
```

---

## 🧪 **TESTING YOUR SETUP**

### **Run Test Suite**
```bash
python tests/test_all_sources.py
```

### **Test Individual Sources**
```python
from data_sources.external.api_implementations import fetch_from_provider

# Test CoinGecko
data = fetch_from_provider("coingecko", "fetch_price", coin_id="bitcoin")
print(data)

# Test FRED
data = fetch_from_provider("fred", "fetch_indicator", series_id="GDP")
print(data)

# Test Telegram
data = fetch_from_provider("telegram", "fetch_channel_messages", channel="crypto")
print(data)
```

### **Verify API Keys**
```python
import os
from dotenv import load_dotenv

load_dotenv('.dix_secrets.env')

# Check if keys are loaded
print(f"COINGECKO_API_KEY: {os.getenv('COINGECKO_API_KEY')}")
print(f"TELEGRAM_BOT_TOKEN: {os.getenv('TELEGRAM_BOT_TOKEN')}")
```

---

## ⚠️ **TROUBLESHOOTING**

### **Common Issues**

#### **1. API Key Not Found**
- **Error**: "API key required"
- **Solution**: Ensure key is in `.dix_secrets.env` and file is loaded

#### **2. Rate Limit Exceeded**
- **Error**: "429 Too Many Requests"
- **Solution**: Increase cache TTL, reduce request frequency

#### **3. Invalid API Key**
- **Error**: "401 Unauthorized"
- **Solution**: Verify API key is correct, not expired

#### **4. Chinese Platform Access**
- **Error**: "Chinese developer account required"
- **Solution**: Requires Chinese business registration or residency

#### **5. Approval Required**
- **Error**: "API access pending approval"
- **Solution**: Wait for approval process (can take weeks)

#### **6. Connection Timeout**
- **Error**: "Connection timeout"
- **Solution**: Check internet connection, firewall settings

#### **7. Empty Response**
- **Error**: "No data returned"
- **Solution**: Verify API is working, check rate limits

---

## 📋 **RECOMMENDED STARTUP SEQUENCE**

### **Phase 1: Essential Free Sources (Immediate)**
1. CoinGecko (no key required)
2. Frankfurter (no key required)
3. FRED (no key required)
4. SEC 13F (no key required)
5. ArXiv (no key required)
6. CBOE (no key required)
7. StockTwits (no key required)
8. NVD CVE (no key required)
9. BSE (no key required)
10. Telegram (bot API, no key required)
11. Viber (bot API, no key required)

### **Phase 2: High-Value Freemium (Soon)**
1. Alpha Vantage (free tier)
2. Seeking Alpha (free tier)
3. TipRanks (free tier)
4. Binance (free market data)
5. Kraken (free market data)
6. GitHub (personal token)
7. CoinMarketCap (free tier)
8. CryptoQuant (free tier)

### **Phase 3: International Platforms (Optional)**
1. VK (Russia - free)
2. Line (Japan - free tier)
3. KakaoTalk (Korea - free tier)
4. ShareChat (India - free tier)
5. Koo (India - free tier)

### **Phase 4: Premium Sources (Optional)**
1. Bloomberg Terminal (enterprise)
2. AlphaSense (enterprise)
3. Whale Alert (paid)
4. Chinese platforms (require Chinese accounts)
5. Snapchat (approval required)

---

## 🚀 **QUICK START**

### **1. Install Dependencies**
```bash
pip install python-dotenv requests
```

### **2. Configure Environment**
```bash
# Copy example
cp .dix_secrets.env.example .dix_secrets.env

# Edit with your API keys
nano .dix_secrets.env
```

### **3. Test Basic Sources**
```bash
python tests/test_all_sources.py
```

### **4. Enable Sources in Source Manager**
```python
from system.source_manager import get_source_manager

manager = get_source_manager()

# Enable specific sources
manager.enable_source("SRC-CRYPTO-COINGECKO-001")
manager.enable_source("SRC-FOREX-FRANKFURTER-001")
```

---

## 📞 **SUPPORT**

### **Documentation Links**
- DIX VISION Docs: See project `/docs` folder
- API Documentation: See individual platform docs above
- Troubleshooting: See troubleshooting section above

### **Getting Help**
- Check platform-specific documentation
- Verify API keys are correct
- Check rate limits
- Review error messages
- Check `.dix_secrets.env` configuration

---

## ⚡ **PERFORMANCE TIPS**

1. **Use Caching**: All sources have cache policies configured
2. **Respect Rate Limits**: Built-in rate limiting in adapters
3. **Monitor Quality**: Use quality monitoring to track performance
4. **Disable Unused Sources**: Use source manager to disable
5. **Adjust TTL**: Tune cache policies based on usage

---

## 🔐 **SECURITY BEST PRACTICES**

1. **Never Commit API Keys**: Add `.dix_secrets.env` to `.gitignore`
2. **Use Environment Variables**: Never hardcode API keys
3. **Rotate Keys Regularly**: Update API keys periodically
4. **Use Least Privilege**: Use read-only API keys when possible
5. **Monitor Usage**: Track API usage for security
6. **Enable 2FA**: Use 2FA on all platforms
7. **Restrict IP**: Use IP restrictions when available

---

## 📊 **SUMMARY**

- **Total Sources**: 94
- **Free / No Key Required**: 25
- **Freemium**: 40
- **Paid / Subscription**: 8
- **Limited / Approval Required**: 21

**Start with Phase 1 (11 free sources) to get started immediately, then add more sources as needed.**

---

**Last Updated**: 2026-06-11
**Version**: 1.0
