-- PostgreSQL initialization script for DIX VISION production
-- This script is automatically executed when the PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create market data table
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) NOT NULL,
    timestamp BIGINT NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    volume DECIMAL(20, 8),
    bid DECIMAL(20, 8),
    ask DECIMAL(20, 8),
    spread DECIMAL(20, 8),
    volatility DECIMAL(10, 8),
    momentum DECIMAL(10, 8),
    trend DECIMAL(10, 8),
    support_level DECIMAL(20, 8),
    resistance_level DECIMAL(20, 8),
    data_source VARCHAR(50),
    data_quality VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    order_side VARCHAR(10) NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    price DECIMAL(20, 8),
    stop_price DECIMAL(20, 8),
    time_in_force VARCHAR(10) DEFAULT 'GTC',
    status VARCHAR(20) DEFAULT 'PENDING',
    filled_quantity DECIMAL(20, 8) DEFAULT 0,
    average_fill_price DECIMAL(20, 8) DEFAULT 0,
    timestamp BIGINT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create positions table
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(50) UNIQUE NOT NULL,
    quantity DECIMAL(20, 8) NOT NULL,
    average_entry_price DECIMAL(20, 8) NOT NULL,
    unrealized_pnl DECIMAL(20, 8) DEFAULT 0,
    realized_pnl DECIMAL(20, 8) DEFAULT 0,
    timestamp BIGINT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trust anchors table
CREATE TABLE IF NOT EXISTS trust_anchors (
    id SERIAL PRIMARY KEY,
    anchor_id VARCHAR(100) UNIQUE NOT NULL,
    purpose VARCHAR(100) NOT NULL,
    key_type VARCHAR(20) NOT NULL,
    public_key TEXT NOT NULL,
    private_key_encrypted TEXT,
    key_size INTEGER,
    registration_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create foundation hashes table
CREATE TABLE IF NOT EXISTS foundation_hashes (
    id SERIAL PRIMARY KEY,
    hash_id VARCHAR(100) UNIQUE NOT NULL,
    component VARCHAR(100) NOT NULL,
    version VARCHAR(50),
    hash_value VARCHAR(256) NOT NULL,
    hash_algorithm VARCHAR(20) DEFAULT 'SHA256',
    timestamp_ns BIGINT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create verification artifacts table
CREATE TABLE IF NOT EXISTS verification_artifacts (
    id SERIAL PRIMARY KEY,
    artifact_id VARCHAR(100) UNIQUE NOT NULL,
    hash_id VARCHAR(100) NOT NULL,
    anchor_id VARCHAR(100) NOT NULL,
    verification_data JSONB DEFAULT '{}',
    signature TEXT NOT NULL,
    signature_algorithm VARCHAR(50),
    created_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'verified',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (anchor_id) REFERENCES trust_anchors(anchor_id)
);

-- Create trading decisions table
CREATE TABLE IF NOT EXISTS trading_decisions (
    id SERIAL PRIMARY KEY,
    decision_id VARCHAR(100) UNIQUE NOT NULL,
    decision_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    reasoning TEXT,
    confidence DECIMAL(5, 4),
    confidence_level VARCHAR(20),
    expected_outcome TEXT,
    risk_assessment JSONB DEFAULT '{}',
    alternative_actions JSONB DEFAULT '[]',
    supporting_evidence JSONB DEFAULT '[]',
    contradictory_evidence JSONB DEFAULT '[]',
    timestamp BIGINT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    component VARCHAR(100),
    action VARCHAR(100),
    details JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'INFO',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);

CREATE INDEX IF NOT EXISTS idx_orders_symbol_status ON orders(symbol, status);
CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_timestamp ON orders(timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol);

CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_timestamp ON positions(timestamp);

CREATE INDEX IF NOT EXISTS idx_trust_anchors_anchor_id ON trust_anchors(anchor_id);
CREATE INDEX IF NOT EXISTS idx_trust_anchors_status ON trust_anchors(status);

CREATE INDEX IF NOT EXISTS idx_foundation_hashes_hash_id ON foundation_hashes(hash_id);
CREATE INDEX IF NOT EXISTS idx_foundation_hashes_component ON foundation_hashes(component);

CREATE INDEX IF NOT EXISTS idx_verification_artifacts_artifact_id ON verification_artifacts(artifact_id);
CREATE INDEX IF NOT EXISTS idx_verification_artifacts_hash_id ON verification_artifacts(hash_id);

CREATE INDEX IF NOT EXISTS idx_trading_decisions_decision_id ON trading_decisions(decision_id);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_timestamp ON trading_decisions(timestamp);
CREATE INDEX IF NOT EXISTS idx_trading_decisions_decision_type ON trading_decisions(decision_type);

CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_severity ON audit_log(severity);

-- Create functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_market_data_updated_at BEFORE UPDATE ON market_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_trust_anchors_updated_at BEFORE UPDATE ON trust_anchors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create sample data for testing (optional)
INSERT INTO market_data (symbol, timestamp, price, volume, bid, ask, spread, volatility, momentum, trend, support_level, resistance_level, data_source, data_quality)
VALUES 
    ('BTC/USD', 1718467200000, 45000.00, 1000.0, 44995.00, 45005.00, 10.00, 0.02, 0.01, 50.0, 44000.00, 46000.00, 'websocket', 'HIGH')
ON CONFLICT DO NOTHING;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dix_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dix_user;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'DIX VISION PostgreSQL database initialized successfully';
END $$;