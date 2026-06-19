"""Liquid State Machine for INDIRA Pattern Recognition.

This module provides Liquid State Machine (LSM) capabilities for temporal
pattern recognition in market data, enabling adaptive learning and real-time
anomaly detection with minimal training requirements.
"""

from __future__ import annotations

import logging
import threading
import time
import numpy as np
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque
import math

logger = logging.getLogger(__name__)


class LSMTopology(str, Enum):
    """Types of LSM topologies."""
    RANDOM = "RANDOM"
    SMALL_WORLD = "SMALL_WORLD"
    SCALE_FREE = "SCALE_FREE"
    RING = "RING"
    GRID = "GRID"


class LSMActivation(str, Enum):
    """Types of activation functions for liquid neurons."""
    TANH = "TANH"
    RELU = "RELU"
    SIGMOID = "SIGMOID"
    LIF = "LIF"


@dataclass
class LSMState:
    """State of the liquid network."""
    state_id: str
    reservoir_activity: np.ndarray  # Activity of all reservoir neurons
    readout_output: np.ndarray  # Output from readout layer
    pattern_signature: np.ndarray  # Temporal pattern signature
    confidence: float
    timestamp: float


@dataclass
class PatternRecognitionResult:
    """Result of pattern recognition."""
    pattern_id: str
    pattern_type: str
    pattern_strength: float
    temporal_signature: np.ndarray
    predicted_outcome: str
    confidence: float
    anomaly_score: float
    timestamp: float


class LiquidReservoir:
    """Liquid reservoir for temporal pattern processing."""

    def __init__(self, n_neurons: int = 100, 
                 connectivity: float = 0.1,
                 spectral_radius: float = 0.9,
                 topology: LSMTopology = LSMTopology.RANDOM,
                 activation: LSMActivation = LSMActivation.TANH):
        """
        Initialize liquid reservoir.
        
        Args:
            n_neurons: Number of neurons in reservoir
            connectivity: Connectivity probability
            spectral_radius: Spectral radius for stability
            topology: Network topology
            activation: Activation function
        """
        self.n_neurons = n_neurons
        self.connectivity = connectivity
        self.spectral_radius = spectral_radius
        self.topology = topology
        self.activation = activation
        
        # Build reservoir weights
        self.reservoir_weights = self._build_reservoir_weights()
        
        # Reservoir state
        self.state = np.zeros(n_neurons)
        
        # Input weights
        self.input_weights = None  # Will be initialized when input dimension is known
        
        # Temporal history
        self.state_history: deque = deque(maxlen=100)
        
        logger.info(f"[INDIRA_LSM] Liquid Reservoir initialized with {n_neurons} neurons, "
                   f"{topology} topology, {activation} activation")
    
    def _build_reservoir_weights(self) -> np.ndarray:
        """Build reservoir weight matrix."""
        # Initialize sparse random weights
        weights = np.random.randn(self.n_neurons, self.n_neurons)
        
        # Apply connectivity mask
        mask = np.random.random((self.n_neurons, self.n_neurons)) < self.connectivity
        weights = weights * mask
        
        # Scale to desired spectral radius
        if np.max(np.abs(np.linalg.eigvals(weights))) > 0:
            weights = weights / np.max(np.abs(np.linalg.eigvals(weights))) * self.spectral_radius
        
        return weights
    
    def initialize_input_weights(self, n_inputs: int) -> None:
        """Initialize input weights."""
        self.input_weights = np.random.uniform(-0.5, 0.5, (self.n_neurons, n_inputs))
    
    def update(self, input_signal: np.ndarray, dt: float = 1.0) -> np.ndarray:
        """
        Update reservoir state with input signal.
        
        Args:
            input_signal: Input signal vector
            dt: Time step
        
        Returns:
            New reservoir state
        """
        if self.input_weights is None or self.input_weights.shape[1] != len(input_signal):
            self.initialize_input_weights(len(input_signal))
        
        # Compute reservoir update
        input_projection = self.input_weights @ input_signal
        reservoir_projection = self.reservoir_weights @ self.state
        
        # Apply activation function
        if self.activation == LSMActivation.TANH:
            new_state = np.tanh(input_projection + reservoir_projection)
        elif self.activation == LSMActivation.RELU:
            new_state = np.maximum(0, input_projection + reservoir_projection)
        elif self.activation == LSMActivation.SIGMOID:
            new_state = 1 / (1 + np.exp(-(input_projection + reservoir_projection)))
        else:  # LIF-like
            # Leaky integration
            decay = 0.9
            new_state = decay * self.state + (1 - decay) * np.tanh(input_projection + reservoir_projection)
        
        # Update state
        self.state = new_state
        self.state_history.append(new_state.copy())
        
        return new_state
    
    def get_state(self) -> np.ndarray:
        """Get current reservoir state."""
        return self.state.copy()
    
    def reset(self) -> None:
        """Reset reservoir state."""
        self.state = np.zeros(self.n_neurons)
        self.state_history.clear()


class LSMReadoutLayer:
    """Readout layer for Liquid State Machine."""

    def __init__(self, n_output: int = 5):
        """
        Initialize readout layer.
        
        Args:
            n_output: Number of output units
        """
        self.n_output = n_output
        self.weights = None  # Will be trained
        self.bias = None
        self._trained = False
        
        logger.info(f"[INDIRA_LSM] Readout layer initialized with {n_output} outputs")
    
    def train(self, reservoir_states: List[np.ndarray], targets: List[np.ndarray],
              method: str = "ridge", alpha: float = 0.01) -> None:
        """
        Train readout layer weights.
        
        Args:
            reservoir_states: List of reservoir states
            targets: List of target outputs
            method: Training method ("ridge", "linear")
            alpha: Regularization parameter for ridge regression
        """
        # Stack reservoir states and targets
        X = np.vstack(reservoir_states)
        Y = np.vstack(targets)
        
        if method == "ridge":
            # Ridge regression with regularization
            I = np.eye(X.shape[1])
            self.weights = np.linalg.solve(X.T @ X + alpha * I, X.T @ Y)
        else:
            # Linear regression
            self.weights = np.linalg.lstsq(X, Y, rcond=None)[0]
        
        # Add bias term
        self.bias = np.mean(Y - X @ self.weights, axis=0)
        
        self._trained = True
        logger.info(f"[INDIRA_LSM] Readout layer trained with {len(reservoir_states)} samples")
    
    def predict(self, reservoir_state: np.ndarray) -> np.ndarray:
        """
        Predict output from reservoir state.
        
        Args:
            reservoir_state: Current reservoir state
        
        Returns:
            Output prediction
        """
        if not self._trained or self.weights is None:
            # Return random prediction if not trained
            return np.random.rand(self.n_output)
        
        output = reservoir_state @ self.weights + self.bias
        return output
    
    def is_trained(self) -> bool:
        """Check if readout layer is trained."""
        return self._trained


class TradingPatternRecognition:
    """Pattern recognition using Liquid State Machine for trading."""

    def __init__(self, n_reservoir_neurons: int = 100,
                 n_output: int = 5,
                 topology: LSMTopology = LSMTopology.RANDOM):
        """
        Initialize trading pattern recognition system.
        
        Args:
            n_reservoir_neurons: Number of reservoir neurons
            n_output: Number of pattern outputs
            topology: Reservoir topology
        """
        self.liquid_reservoir = LiquidReservoir(
            n_neurons=n_reservoir_neurons,
            topology=topology
        )
        self.readout_layer = LSMReadoutLayer(n_output=n_output)
        
        # Pattern database
        self.pattern_database: Dict[str, PatternRecognitionResult] = {}
        
        # Temporal window for pattern extraction
        self.temporal_window: deque = deque(maxlen=50)
        
        # Anomaly threshold
        self.anomaly_threshold = 0.7
        
        self.lock = threading.Lock()
        
        logger.info("[INDIRA_LSM] Trading Pattern Recognition initialized")
    
    def process_market_sequence(self, market_sequence: List[Dict[str, Any]]) -> PatternRecognitionResult:
        """
        Process a sequence of market data for pattern recognition.
        
        Args:
            market_sequence: Sequence of market data points
        
        Returns:
            Pattern recognition result
        """
        with self.lock:
            pattern_id = f"pattern_{int(time.time())}"
            
            # Convert market sequence to feature sequence
            feature_sequence = self._market_sequence_to_features(market_sequence)
            
            # Process through reservoir
            reservoir_states = []
            for features in feature_sequence:
                state = self.liquid_reservoir.update(features)
                reservoir_states.append(state)
                self.temporal_window.append(state.copy())
            
            # Get final reservoir state
            final_state = self.liquid_reservoir.get_state()
            
            # Get readout prediction
            output = self.readout_layer.predict(final_state)
            
            # Determine pattern type
            pattern_type = self._classify_pattern(output)
            
            # Calculate pattern strength
            pattern_strength = np.max(np.abs(output))
            
            # Extract temporal signature
            temporal_signature = self._extract_temporal_signature(reservoir_states)
            
            # Predict outcome
            predicted_outcome = self._predict_outcome(pattern_type, pattern_strength)
            
            # Calculate anomaly score
            anomaly_score = self._calculate_anomaly_score(temporal_signature)
            
            # Calculate confidence
            confidence = min(pattern_strength, 1.0 - anomaly_score)
            
            result = PatternRecognitionResult(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                pattern_strength=pattern_strength,
                temporal_signature=temporal_signature,
                predicted_outcome=predicted_outcome,
                confidence=confidence,
                anomaly_score=anomaly_score,
                timestamp=time.time()
            )
            
            # Store in pattern database
            self.pattern_database[pattern_id] = result
            
            # Reset reservoir for next sequence
            self.liquid_reservoir.reset()
            
            return result
    
    def _market_sequence_to_features(self, market_sequence: List[Dict[str, Any]]) -> List[np.ndarray]:
        """Convert market sequence to feature sequence."""
        feature_sequence = []
        
        for market_data in market_sequence:
            features = np.array([
                market_data.get("price_change_pct", 0.0),
                market_data.get("volume_change_pct", 0.0),
                market_data.get("volatility", 0.2),
                market_data.get("rsi", 50.0) / 100.0,  # Normalize
                market_data.get("macd", 0.0) / 100.0  # Normalize
            ])
            feature_sequence.append(features)
        
        return feature_sequence
    
    def _classify_pattern(self, output: np.ndarray) -> str:
        """Classify pattern from readout output."""
        # Simple classification based on output patterns
        max_idx = np.argmax(np.abs(output))
        
        pattern_types = [
            "uptrend_continuation",
            "downtrend_continuation",
            "reversal_potential",
            "consolidation",
            "high_volatility"
        ]
        
        return pattern_types[min(max_idx, len(pattern_types) - 1)]
    
    def _extract_temporal_signature(self, reservoir_states: List[np.ndarray]) -> np.ndarray:
        """Extract temporal signature from reservoir states."""
        if not reservoir_states:
            return np.zeros(10)
        
        # Compute statistics over time
        states_array = np.vstack(reservoir_states)
        
        signature = np.array([
            np.mean(states_array),
            np.std(states_array),
            np.max(states_array),
            np.min(states_array),
            np.median(states_array),
            np.percentile(states_array, 25),
            np.percentile(states_array, 75),
            np.mean(np.diff(states_array, axis=0)),
            np.max(np.diff(states_array, axis=0)),
            np.min(np.diff(states_array, axis=0))
        ])
        
        return signature
    
    def _predict_outcome(self, pattern_type: str, strength: float) -> str:
        """Predict trading outcome based on pattern."""
        if strength < 0.3:
            return "low_confidence_prediction"
        
        outcome_map = {
            "uptrend_continuation": "bullish_continuation",
            "downtrend_continuation": "bearish_continuation",
            "reversal_potential": "trend_reversal",
            "consolidation": "sideways_movement",
            "high_volatility": "high_volatility_risk"
        }
        
        return outcome_map.get(pattern_type, "unknown_pattern")
    
    def _calculate_anomaly_score(self, temporal_signature: np.ndarray) -> float:
        """Calculate anomaly score based on temporal signature."""
        # Use distance from typical signatures
        typical_signature = np.array([0.0, 0.5, 1.0, -1.0, 0.0, -0.5, 0.5, 0.0, 0.1, -0.1])
        
        distance = np.linalg.norm(temporal_signature - typical_signature)
        anomaly_score = min(1.0, distance / 5.0)  # Normalize
        
        return anomaly_score
    
    def train_offline(self, historical_sequences: List[List[Dict[str, Any]]],
                     pattern_labels: List[str]) -> None:
        """
        Train the LSM offline with historical data.
        
        Args:
            historical_sequences: List of historical market sequences
            pattern_labels: Corresponding pattern labels
        """
        logger.info(f"[INDIRA_LSM] Training LSM with {len(historical_sequences)} sequences")
        
        reservoir_states = []
        targets = []
        
        for sequence, label in zip(historical_sequences, pattern_labels):
            # Process sequence
            feature_sequence = self._market_sequence_to_features(sequence)
            
            # Collect reservoir states
            seq_states = []
            for features in feature_sequence:
                state = self.liquid_reservoir.update(features)
                seq_states.append(state)
            
            reservoir_states.append(seq_states[-1])  # Use final state
            
            # Convert label to target vector
            target = self._label_to_target(label)
            targets.append(target)
            
            # Reset for next sequence
            self.liquid_reservoir.reset()
        
        # Train readout layer
        self.readout_layer.train(reservoir_states, targets)
        
        logger.info("[INDIRA_LSM] LSM training completed")
    
    def _label_to_target(self, label: str) -> np.ndarray:
        """Convert pattern label to target vector."""
        label_map = {
            "uptrend": np.array([1.0, 0.0, 0.0, 0.0, 0.0]),
            "downtrend": np.array([0.0, 1.0, 0.0, 0.0, 0.0]),
            "reversal": np.array([0.0, 0.0, 1.0, 0.0, 0.0]),
            "consolidation": np.array([0.0, 0.0, 0.0, 1.0, 0.0]),
            "volatile": np.array([0.0, 0.0, 0.0, 0.0, 1.0])
        }
        
        return label_map.get(label.lower(), np.array([0.2, 0.2, 0.2, 0.2, 0.2]))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get LSM statistics."""
        with self.lock:
            return {
                "reservoir_neurons": self.liquid_reservoir.n_neurons,
                "readout_trained": self.readout_layer.is_trained(),
                "patterns_recognized": len(self.pattern_database),
                "anomaly_threshold": self.anomaly_threshold,
                "reservoir_topology": self.liquid_reservoir.topology.value,
                "reservoir_activation": self.liquid_reservoir.activation.value
            }


class INDIRALSMIntelligence:
    """INDIRA LSM intelligence integration."""

    def __init__(self):
        self.pattern_recognition = TradingPatternRecognition()
        self._initialized = False
    
    def start(self) -> bool:
        """Start LSM intelligence system."""
        logger.info("[INDIRA_LSM] Starting INDIRA LSM intelligence...")
        self._initialized = True
        logger.info("[INDIRA_LSM] INDIRA LSM intelligence started")
        return True
    
    def stop(self) -> bool:
        """Stop LSM intelligence system."""
        logger.info("[INDIRA_LSM] Stopping INDIRA LSM intelligence...")
        self._initialized = False
        logger.info("[INDIRA_LSM] INDIRA LSM intelligence stopped")
        return True
    
    def recognize_pattern(self, market_sequence: List[Dict[str, Any]]) -> PatternRecognitionResult:
        """Recognize pattern in market sequence."""
        return self.pattern_recognition.process_market_sequence(market_sequence)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get LSM intelligence statistics."""
        return self.pattern_recognition.get_statistics()


# Singleton instance
_indira_lsm_intelligence: Optional[INDIRALSMIntelligence] = None
_indira_lsm_intelligence_lock = threading.Lock()


def get_indira_lsm_intelligence() -> INDIRALSMIntelligence:
    """Get the singleton INDIRA LSM intelligence instance."""
    global _indira_lsm_intelligence
    if _indira_lsm_intelligence is None:
        with _indira_lsm_intelligence_lock:
            if _indira_lsm_intelligence is None:
                _indira_lsm_intelligence = INDIRALSMIntelligence()
    return _indira_lsm_intelligence


__all__ = [
    "INDIRALSMIntelligence",
    "get_indira_lsm_intelligence",
    "TradingPatternRecognition",
    "LiquidReservoir",
    "LSMReadoutLayer",
    "LSMState",
    "PatternRecognitionResult",
    "LSMTopology",
    "LSMActivation",
]