# API KEYS SETUP GUIDE

## ✅ **CURRENTLY CONFIGURED**

| Source | Status | Notes |
|--------|--------|-------|
| Alpha Vantage | ✅ Working | Financial data - stock prices, forex, indicators |
| OpenRouter | ✅ Working | LLM features |
| CoinGecko | ✅ Working | Crypto prices - FREE, no key required |
| Frankfurter | ✅ Working | Forex rates - FREE, no key required |
| FRED | ✅ Working | Macro indicators - FREE, no key required |

---

## 🚀 **FREE API KEYS (RECOMMENDED)**

Get these FREE API keys to enhance system capabilities:

### **Perplexity AI** (Best Real-Time Search)
**Why**: Best-in-class real-time search, web browsing, citations
**Free Tier**: Yes - generous free tier
**Sign Up**: https://www.perplexity.ai
**Instructions**:
1. Sign up for free account
2. Go to API Settings in dashboard
3. Copy your API key
4. Add to `.dix_secrets.env`: `PERPLEXITY_API_KEY=your_key`

**Cost**: FREE (with option to upgrade)

---

### **Cohere** (Embeddings & RAG)
**Why**: Advanced embeddings, retrieval-augmented generation, search
**Free Tier**: Yes - 1000 free API calls/month
**Sign Up**: https://cohere.com
**Instructions**:
1. Sign up for free account
2. Go to API Keys section
3. Generate new API key
4. Add to `.dix_secrets.env`: `COHERE_API_KEY=your_key`

**Cost**: FREE (with option to upgrade)

---

### **Mistral AI** (Open-Source Models)
**Why**: State-of-the-art open-source models
**Free Tier**: Yes - free credits for testing
**Sign Up**: https://mistral.ai
**Instructions**:
1. Sign up for free account
2. Go to Platform > API Keys
3. Create new API key
4. Add to `.dix_secrets.env`: `MISTRAL_API_KEY=your_key`

**Cost**: FREE (with option to upgrade)

---

### **Hugging Face** (1000+ Models)
**Why**: Access to 1000+ pre-trained models
**Free Tier**: Yes - free inference API
**Sign Up**: https://huggingface.co
**Instructions**:
1. Sign up for free account
2. Go to Settings > Access Tokens
3. Create new token
4. Add to `.dix_secrets.env`: `HUGGINGFACE_API_KEY=your_key`

**Cost**: FREE (with option to upgrade)

---

### **Tavily** (AI-Powered Research)
**Why**: AI-powered research, real-time answers, citations
**Free Tier**: Yes - 1000 free API calls/month
**Sign Up**: https://tavily.com
**Instructions**:
1. Sign up for free account
2. Go to API Keys section
3. Copy your API key
4. Add to `.dix_secrets.env`: `TAVILY_API_KEY=your_key`

**Cost**: FREE (with option to upgrade)

---

### **Serper.dev** (Google Search API)
**Why**: Fast Google Search API, real-time results
**Free Tier**: 100 free requests/month
**Sign Up**: https://serper.dev
**Instructions**:
1. Sign up for free account
2. Get your API key from dashboard
3. Add to `.dix_secrets.env`: `SERPER_API_KEY=your_key`

**Cost**: 100 free requests/month (then paid)

---

### **SerpApi** (Multiple Search Engines)
**Why**: Google, Bing, Yahoo, Yandex, Baidu, DuckDuckGo
**Free Tier**: Yes - 100 free searches/month
**Sign Up**: https://serpapi.com
**Instructions**:
1. Sign up for free account
2. Get your API key from dashboard
3. Add to `.dix_secrets.env`: `SERPAPI_API_KEY=your_key`

**Cost**: 100 free searches/month (then paid)

---

### **Apify** (Web Scraping)
**Why**: Web scraping with AI, data extraction
**Free Tier**: Yes - free tier for development
**Sign Up**: https://apify.com
**Instructions**:
1. Sign up for free account
2. Get your API key from dashboard
3. Add to `.dix_secrets.env`: `APIFY_API_KEY=your_key`

**Cost**: FREE (with option to upgrade)

---

## 💳 **PAID API KEYS (OPTIONAL)**

Only get these if you specifically need them:

### **ChatGPT Plus** ($20/month)
- Web browsing capability
- Sign up: https://chat.openai.com
- Add: `CHATGPTPLUS_API_KEY=your_key`

### **Claude Computer Use** (usage-based)
- Tool-based browsing, computer use
- Sign up: https://claude.ai
- Add: `CLAUDE_API_KEY=your_key`

### **Microsoft Copilot** (enterprise)
- Enterprise search integration
- Sign up: https://copilot.microsoft.com
- Add: `COPILOT_API_KEY=your_key`

### **Kagi** ($5/month)
- Premium unbiased search
- Sign up: https://kagi.com
- Add: `KAGI_API_KEY=your_key`

---

## 🎯 **PRIORITY ORDER**

### **High Priority (Get These First)**
1. **Perplexity AI** - Best real-time search (FREE)
2. **Cohere** - Embeddings/RAG (FREE)
3. **Hugging Face** - 1000+ models (FREE)

### **Medium Priority (Optional)**
4. **Mistral AI** - Open-source models (FREE)
5. **Tavily** - AI research (FREE)
6. **Serper.dev** - Google Search (100 free/month)

### **Low Priority (Only if Needed)**
7. **SerpApi** - Multiple engines (100 free/month)
8. **Apify** - Web scraping (FREE)
9. **Paid providers** - Only if budget allows

---

## ✅ **HOW TO ADD KEYS**

1. Sign up for the service
2. Get your API key from their dashboard
3. Open `.dix_secrets.env`
4. Add your key: `PROVIDER_API_KEY=your_actual_key`
5. Save the file
6. Restart your application

---

## 🧪 **TESTING**

After adding API keys, test them:

```bash
# Test individual providers
python tests/test_ai_providers.py

# Test free sources
python tests/test_free_sources_working.py

# Test Alpha Vantage
python tests/test_alpha_vantage.py
```

---

## 📊 **CURRENT CAPABILITIES**

**With Current Setup** (Alpha Vantage + OpenRouter + Free Sources):
- ✅ Financial data (Alpha Vantage)
- ✅ LLM features (OpenRouter)
- ✅ Crypto prices (CoinGecko - free)
- ✅ Forex rates (Frankfurter - free)
- ✅ Macro indicators (FRED - free)
- ✅ DYON can call Local Devin CLI (unlimited coding)

**After Adding Free AI Keys**:
- ✅ Real-time search (Perplexity)
- ✅ Embeddings/RAG (Cohere)
- ✅ 1000+ models (Hugging Face)
- ✅ AI research (Tavily)
- ✅ Google Search (Serper)
- ✅ Much more...

---

## 🚀 **NEXT STEPS**

1. Get Perplexity AI key (FREE) - highest priority
2. Get Cohere key (FREE) - for embeddings
3. Get Hugging Face key (FREE) - for models
4. Test all providers
5. Enjoy enhanced AI capabilities!

---

**Total Cost to Get Started**: $0 (all recommended providers have FREE tiers)

---

**Your system is ready to use with the current configuration. Adding the free AI keys will significantly enhance capabilities at no cost.** 🎊
