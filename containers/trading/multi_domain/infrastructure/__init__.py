"""
Multi-Domain Trading Support Infrastructure
Contract-Compliant Real Implementation

Real multi-domain trading infrastructure for unified trading across financial domains
"""

from .crypto_domain import (
    BlockchainType,
    CryptoDomainAdapter,
    CryptoInstrument,
    CryptoOrderConfig,
    CryptoToken,
)
from .domain_abstraction import (
    DomainAbstractionLayer,
    DomainAdapter,
    Instrument,
    InstrumentType,
    OrderSide,
    PositionSide,
    TradingDomain,
    UnifiedMarketData,
    UnifiedOrder,
    UnifiedPosition,
)
from .forex_domain import (
    CurrencyPair,
    ForexDomainAdapter,
    ForexOrderConfig,
    ForexPricing,
    ForexSession,
)
from .futures_domain import (
    ContractMonth,
    FuturesContract,
    FuturesContractType,
    FuturesDomainAdapter,
    FuturesOrderConfig,
)
from .stocks_domain import OrderCondition, StockMarketHours, StockOrderConfig, StocksDomainAdapter

__all__ = [
    # Domain Abstraction Layer
    "DomainAbstractionLayer",
    "Instrument",
    "UnifiedOrder",
    "UnifiedPosition",
    "UnifiedMarketData",
    "DomainAdapter",
    "TradingDomain",
    "InstrumentType",
    "OrderSide",
    "PositionSide",
    # Stocks Domain
    "StocksDomainAdapter",
    "StockMarketHours",
    "OrderCondition",
    "StockOrderConfig",
    # Futures Domain
    "FuturesDomainAdapter",
    "FuturesContract",
    "FuturesContractType",
    "ContractMonth",
    "FuturesOrderConfig",
    # Forex Domain
    "ForexDomainAdapter",
    "CurrencyPair",
    "ForexSession",
    "ForexPricing",
    "ForexOrderConfig",
    # Crypto Domain
    "CryptoDomainAdapter",
    "CryptoToken",
    "BlockchainType",
    "CryptoInstrument",
    "CryptoOrderConfig",
]
