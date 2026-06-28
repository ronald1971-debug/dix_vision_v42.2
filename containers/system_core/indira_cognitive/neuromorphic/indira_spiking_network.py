"""Spiking Neural Network for INDIRA Trading Intelligence.

This module provides spiking neural network (SNN) capabilities for INDIRA,
enabling event-driven, energy-efficient, and biologically plausible trading
intelligence with temporal pattern recognition and adaptive learning.
"""

from __future__ import annotations

import logging
import math
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class NeuronModel(str, Enum):
    """Types of spiking neuron models."""

    LIF = "LIF"  # Leaky Integrate-and-Fire
    IZHIKEVICH = "IZHIKEVICH"
    HODGKIN_HUXLEY = "HODGKIN_HUXLEY"
    ADAPTIVE_LIF = "ADAPTIVE_LIF"


class SpikeEncoding(str, Enum):
    """Types of spike encoding."""

    RATE = "RATE"
    TEMPORAL = "TEMPORAL"
    PHASE = "PHASE"
    BURST = "BURST"


@dataclass
class SpikeTrain:
    """Spike train from a neuron."""

    neuron_id: str
    spike_times: List[float]  # Timestamps in seconds
    spike_indices: np.ndarray  # Time bin indices
    encoding: SpikeEncoding


@dataclass
class TradingSpikeEvent:
    """Trading event converted to spike."""

    event_id: str
    event_type: str  # "price_tick", "volume_surge", "signal_change", etc.
    asset: str
    spike_train: SpikeTrain
    raw_data: Dict[str, Any]
    timestamp: float


@dataclass
class SNNResponse:
    """Response from spiking neural network."""

    response_id: str
    spike_output: Dict[str, SpikeTrain]
    membrane_potentials: Dict[str, np.ndarray]
    decision_signal: float  # Aggregated decision signal
    confidence: float
    temporal_features: Dict[str, float]
    timestamp: float


class LeakyIntegrateFireNeuron:
    """Leaky Integrate-and-Fire (LIF) neuron implementation."""

    def __init__(
        self,
        neuron_id: str,
        tau_mem: float = 20.0,
        threshold: float = 1.0,
        reset: float = 0.0,
        resting_potential: float = 0.0,
    ):
        """
        Initialize LIF neuron.

        Args:
            tau_mem: Membrane time constant (ms)
            threshold: Firing threshold
            reset: Reset potential after spike
            resting_potential: Resting membrane potential
        """
        self.neuron_id = neuron_id
        self.tau_mem = tau_mem  # Membrane time constant
        self.threshold = threshold
        self.reset = reset
        self.resting_potential = resting_potential

        # Neuron state
        self.membrane_potential = resting_potential
        self.last_spike_time = -float("inf")
        self.spike_history: deque = deque(maxlen=1000)

        # Adaptive parameters
        self.adaptation_current = 0.0
        self.adaptation_tau = 200.0  # Adaptation time constant

    def process_spike(
        self, spike_time: float, input_current: float = 1.0, dt: float = 1.0
    ) -> Optional[float]:
        """
        Process incoming spike and return output spike time if neuron fires.

        Args:
            spike_time: Time of incoming spike
            input_current: Input current amplitude
            dt: Time step (ms)

        Returns:
            Spike time if neuron fires, None otherwise
        """
        # Update membrane potential with leak
        leak = (self.resting_potential - self.membrane_potential) / self.tau_mem
        self.membrane_potential += (leak * dt) + input_current

        # Apply adaptation current
        self.adaptation_current *= math.exp(-dt / self.adaptation_tau)
        self.membrane_potential -= self.adaptation_current

        # Check threshold
        if self.membrane_potential >= self.threshold:
            # Neuron fires
            spike_time = spike_time
            self.membrane_potential = self.reset
            self.last_spike_time = spike_time
            self.spike_history.append(spike_time)

            # Increase adaptation current
            self.adaptation_current += 0.1

            return spike_time

        return None

    def get_state(self) -> Dict[str, float]:
        """Get current neuron state."""
        return {
            "membrane_potential": self.membrane_potential,
            "adaptation_current": self.adaptation_current,
            "last_spike_time": self.last_spike_time,
            "spike_count": len(self.spike_history),
        }


class TradingSpikingNetwork:
    """Spiking neural network for trading intelligence."""

    def __init__(
        self,
        n_input_neurons: int = 50,
        n_hidden_neurons: int = 100,
        n_output_neurons: int = 10,
        neuron_model: NeuronModel = NeuronModel.LIF,
    ):
        """
        Initialize trading spiking network.

        Args:
            n_input_neurons: Number of input neurons
            n_hidden_neurons: Number of hidden neurons
            n_output_neurons: Number of output neurons
            neuron_model: Type of neuron model to use
        """
        self.n_input_neurons = n_input_neurons
        self.n_hidden_neurons = n_hidden_neurons
        self.n_output_neurons = n_output_neurons
        self.neuron_model = neuron_model

        # Create neurons
        self.input_neurons = self._create_neurons("input", n_input_neurons)
        self.hidden_neurons = self._create_neurons("hidden", n_hidden_neurons)
        self.output_neurons = self._create_neurons("output", n_output_neurons)

        # Synaptic weights
        self.input_to_hidden_weights = self._initialize_weights(n_input_neurons, n_hidden_neurons)
        self.hidden_to_output_weights = self._initialize_weights(n_hidden_neurons, n_output_neurons)

        # Synaptic delays (ms)
        self.input_to_hidden_delays = np.random.uniform(1, 5, (n_input_neurons, n_hidden_neurons))
        self.hidden_to_output_delays = np.random.uniform(1, 5, (n_hidden_neurons, n_output_neurons))

        # Spike history for STDP
        self.spike_history: Dict[str, List[float]] = defaultdict(list)

        # Network state
        self.current_time = 0.0
        self.lock = threading.Lock()

        logger.info(
            f"[INDIRA_SNN] Trading Spiking Network initialized with {n_input_neurons} input, "
            f"{n_hidden_neurons} hidden, {n_output_neurons} output neurons"
        )

    def _create_neurons(self, layer_name: str, n_neurons: int) -> List[LeakyIntegrateFireNeuron]:
        """Create neurons for a layer."""
        neurons = []
        for i in range(n_neurons):
            neuron_id = f"{layer_name}_neuron_{i}"
            neurons.append(LeakyIntegrateFireNeuron(neuron_id))
        return neurons

    def _initialize_weights(self, pre_n: int, post_n: int) -> np.ndarray:
        """Initialize synaptic weights."""
        # Initialize with small random weights
        weights = np.random.uniform(0.1, 1.0, (pre_n, post_n))
        return weights

    def encode_market_data_to_spikes(
        self, market_data: Dict[str, Any], encoding: SpikeEncoding = SpikeEncoding.TEMPORAL
    ) -> List[TradingSpikeEvent]:
        """
        Encode market data into spike trains.

        Args:
            market_data: Dictionary containing market data
            encoding: Type of spike encoding to use

        Returns:
            List of trading spike events
        """
        spike_events = []

        # Encode price changes as temporal spikes
        price = market_data.get("price", 50000.0)
        price_change = market_data.get("price_change_pct", 0.0)
        volume = market_data.get("volume", 1000.0)
        volatility = market_data.get("volatility", 0.2)

        # Rate encoding: spike rate proportional to signal strength
        if encoding == SpikeEncoding.RATE:
            spike_rate = abs(price_change) * 100  # spikes per second
            n_spikes = int(spike_rate * 0.01)  # Scale to reasonable range
            spike_times = [self.current_time + i / spike_rate for i in range(n_spikes)]

            spike_events.append(
                TradingSpikeEvent(
                    event_id=f"price_spike_{int(self.current_time)}",
                    event_type="price_change",
                    asset=market_data.get("asset", "BTC"),
                    spike_train=SpikeTrain(
                        neuron_id="price_encoder",
                        spike_times=spike_times,
                        spike_indices=np.array([int(t * 1000) for t in spike_times]),
                        encoding=encoding,
                    ),
                    raw_data={"price": price, "change": price_change},
                    timestamp=self.current_time,
                )
            )

        # Temporal encoding: spike timing encodes signal value
        elif encoding == SpikeEncoding.TEMPORAL:
            # Higher signals fire earlier
            spike_time = self.current_time + (1.0 - abs(price_change)) * 0.01

            spike_events.append(
                TradingSpikeEvent(
                    event_id=f"price_temporal_{int(self.current_time)}",
                    event_type="price_change",
                    asset=market_data.get("asset", "BTC"),
                    spike_train=SpikeTrain(
                        neuron_id="price_temporal_encoder",
                        spike_times=[spike_time],
                        spike_indices=np.array([int(spike_time * 1000)]),
                        encoding=encoding,
                    ),
                    raw_data={"price": price, "change": price_change},
                    timestamp=self.current_time,
                )
            )

        return spike_events

    def process_spikes(
        self, spike_events: List[TradingSpikeEvent], dt: float = 1.0, duration_ms: float = 100.0
    ) -> SNNResponse:
        """
        Process spike events through the network.

        Args:
            spike_events: List of spike events to process
            dt: Time step (ms)
            duration_ms: Duration to simulate (ms)

        Returns:
            SNN response with output spikes and decision signal
        """
        with self.lock:
            response_id = f"snn_response_{int(time.time())}"

            # Reset neurons
            self._reset_neurons()

            # Simulate network over time
            time_steps = int(duration_ms / dt)

            membrane_potentials = {"input": [], "hidden": [], "output": []}

            output_spikes: Dict[str, List[float]] = defaultdict(list)

            for t in range(time_steps):
                current_time_ms = t * dt
                self.current_time = current_time_ms

                # Process input layer
                input_spikes = self._get_input_spikes_at_time(spike_events, current_time_ms)
                for i, neuron in enumerate(self.input_neurons):
                    if i < len(input_spikes) and input_spikes[i]:
                        neuron.process_spike(current_time_ms, input_current=1.0, dt=dt)
                    membrane_potentials["input"].append(neuron.membrane_potential)

                    # Propagate to hidden layer
                    self._propagate_spikes_to_hidden(i, neuron, current_time_ms, dt)

                # Process hidden layer
                for neuron in self.hidden_neurons:
                    membrane_potentials["hidden"].append(neuron.membrane_potential)

                    # Check if hidden neuron fired
                    if neuron.last_spike_time == current_time_ms:
                        self._propagate_spikes_to_output(neuron, current_time_ms, dt)

                # Process output layer
                for i, neuron in enumerate(self.output_neurons):
                    membrane_potentials["output"].append(neuron.membrane_potential)

                    # Check if output neuron fired
                    if neuron.last_spike_time == current_time_ms:
                        output_spikes[neuron.neuron_id].append(current_time_ms)

            # Calculate decision signal from output spikes
            decision_signal = self._calculate_decision_signal(output_spikes)
            confidence = min(abs(decision_signal), 1.0)

            # Extract temporal features
            temporal_features = self._extract_temporal_features(output_spikes)

            response = SNNResponse(
                response_id=response_id,
                spike_output=output_spikes,
                membrane_potentials=membrane_potentials,
                decision_signal=decision_signal,
                confidence=confidence,
                temporal_features=temporal_features,
                timestamp=time.time(),
            )

            return response

    def _reset_neurons(self) -> None:
        """Reset all neurons to resting state."""
        for neuron in self.input_neurons + self.hidden_neurons + self.output_neurons:
            neuron.membrane_potential = neuron.resting_potential
            neuron.last_spike_time = -float("inf")
            neuron.adaptation_current = 0.0

    def _get_input_spikes_at_time(
        self, spike_events: List[TradingSpikeEvent], current_time_ms: float
    ) -> List[float]:
        """Get input spikes at current time step."""
        input_currents = np.zeros(self.n_input_neurons)

        for event in spike_events:
            # Check if any spike occurred at this time
            for spike_time in event.spike_train.spike_times * 1000:  # Convert to ms
                if abs(spike_time - current_time_ms) < 1.0:  # Within 1ms window
                    # Distribute to input neurons
                    for i in range(min(len(input_currents), self.n_input_neurons)):
                        input_currents[i] = 1.0
                    break

        return input_currents

    def _propagate_spikes_to_hidden(
        self,
        input_idx: int,
        input_neuron: LeakyIntegrateFireNeuron,
        current_time_ms: float,
        dt: float,
    ) -> None:
        """Propagate spikes from input to hidden layer."""
        if input_neuron.last_spike_time == current_time_ms:
            for j, hidden_neuron in enumerate(self.hidden_neurons):
                # Apply synaptic weight
                weight = self.input_to_hidden_weights[input_idx, j]
                delay = self.input_to_hidden_delays[input_idx, j]

                # Schedule spike with delay
                delayed_time = current_time_ms + delay

                # For simplicity, apply immediately with delay factor
                hidden_neuron.process_spike(delayed_time, input_current=weight, dt=dt)

    def _propagate_spikes_to_output(
        self, hidden_neuron: LeakyIntegrateFireNeuron, current_time_ms: float, dt: float
    ) -> None:
        """Propagate spikes from hidden to output layer."""
        # Find hidden neuron index
        hidden_idx = self.hidden_neurons.index(hidden_neuron)

        for j, output_neuron in enumerate(self.output_neurons):
            # Apply synaptic weight
            weight = self.hidden_to_output_weights[hidden_idx, j]
            delay = self.hidden_to_output_delays[hidden_idx, j]

            # Schedule spike with delay
            delayed_time = current_time_ms + delay

            # Apply to output neuron
            output_neuron.process_spike(delayed_time, input_current=weight, dt=dt)

    def _calculate_decision_signal(self, output_spikes: Dict[str, List[float]]) -> float:
        """Calculate decision signal from output spikes."""
        # Sum all output spikes
        total_spikes = sum(len(spikes) for spikes in output_spikes.values())

        # Normalize by number of output neurons and time
        if total_spikes > 0:
            signal = (total_spikes / len(self.output_neurons)) * 0.1
        else:
            signal = 0.0

        return signal

    def _extract_temporal_features(self, output_spikes: Dict[str, List[float]]) -> Dict[str, float]:
        """Extract temporal features from output spikes."""
        if not output_spikes:
            return {"spike_count": 0.0, "spike_rate": 0.0, "synchrony": 0.0}

        all_spikes = []
        for spikes in output_spikes.values():
            all_spikes.extend(spikes)

        if not all_spikes:
            return {"spike_count": 0.0, "spike_rate": 0.0, "synchrony": 0.0}

        spike_count = len(all_spikes)
        spike_rate = (
            spike_count / (max(all_spikes) - min(all_spikes)) if len(all_spikes) > 1 else 0.0
        )

        # Calculate synchrony (coefficient of variation of inter-spike intervals)
        if len(all_spikes) > 1:
            isis = np.diff(sorted(all_spikes))
            synchrony = 1.0 - (np.std(isis) / np.mean(isis)) if np.mean(isis) > 0 else 0.0
        else:
            synchrony = 0.0

        return {
            "spike_count": float(spike_count),
            "spike_rate": float(spike_rate),
            "synchrony": float(synchrony),
        }

    def apply_stdp(
        self, pre_spike_time: float, post_spike_time: float, learning_rate: float = 0.01
    ) -> float:
        """
        Apply Spike-Timing Dependent Plasticity (STDP).

        Args:
            pre_spike_time: Time of presynaptic spike
            post_spike_time: Time of postsynaptic spike
            learning_rate: Learning rate

        Returns:
            Weight change
        """
        delta_t = post_spike_time - pre_spike_time

        # STDP rule: potentiation if post fires after pre, depression otherwise
        if delta_t > 0:
            # Potentiation
            weight_change = learning_rate * math.exp(-delta_t / 20.0)
        else:
            # Depression
            weight_change = -learning_rate * math.exp(delta_t / 20.0)

        return weight_change

    def get_statistics(self) -> Dict[str, Any]:
        """Get network statistics."""
        with self.lock:
            total_spikes = sum(
                len(neuron.spike_history)
                for neuron in self.input_neurons + self.hidden_neurons + self.output_neurons
            )

            return {
                "n_input_neurons": self.n_input_neurons,
                "n_hidden_neurons": self.n_hidden_neurons,
                "n_output_neurons": self.n_output_neurons,
                "total_spikes_processed": total_spikes,
                "average_firing_rate": total_spikes
                / max(1, len(self.input_neurons + self.hidden_neurons + self.output_neurons)),
                "synaptic_weights_range": {
                    "input_to_hidden": (
                        float(np.min(self.input_to_hidden_weights)),
                        float(np.max(self.input_to_hidden_weights)),
                    ),
                    "hidden_to_output": (
                        float(np.min(self.hidden_to_output_weights)),
                        float(np.max(self.hidden_to_output_weights)),
                    ),
                },
            }


class INDIRASpikingIntelligence:
    """INDIRA spiking intelligence integration."""

    def __init__(self):
        self.snn = TradingSpikingNetwork()
        self._initialized = False

    def start(self) -> bool:
        """Start spiking intelligence system."""
        logger.info("[INDIRA_SNN] Starting INDIRA spiking intelligence...")
        self._initialized = True
        logger.info("[INDIRA_SNN] INDIRA spiking intelligence started")
        return True

    def stop(self) -> bool:
        """Stop spiking intelligence system."""
        logger.info("[INDIRA_SNN] Stopping INDIRA spiking intelligence...")
        self._initialized = False
        logger.info("[INDIRA_SNN] INDIRA spiking intelligence stopped")
        return True

    def analyze_market_with_snn(self, market_data: Dict[str, Any]) -> SNNResponse:
        """Analyze market data using spiking neural network."""
        # Encode market data to spikes
        spike_events = self.snn.encode_market_data_to_spikes(market_data)

        # Process through SNN
        response = self.snn.process_spikes(spike_events)

        return response

    def get_statistics(self) -> Dict[str, Any]:
        """Get spiking intelligence statistics."""
        return self.snn.get_statistics()


# Singleton instance
_indira_spiking_intelligence: Optional[INDIRASpikingIntelligence] = None
_indira_spiking_intelligence_lock = threading.Lock()


def get_indira_spiking_intelligence() -> INDIRASpikingIntelligence:
    """Get the singleton INDIRA spiking intelligence instance."""
    global _indira_spiking_intelligence
    if _indira_spiking_intelligence is None:
        with _indira_spiking_intelligence_lock:
            if _indira_spiking_intelligence is None:
                _indira_spiking_intelligence = INDIRASpikingIntelligence()
    return _indira_spiking_intelligence


__all__ = [
    "INDIRASpikingIntelligence",
    "get_indira_spiking_intelligence",
    "TradingSpikingNetwork",
    "LeakyIntegrateFireNeuron",
    "SpikeTrain",
    "TradingSpikeEvent",
    "SNNResponse",
    "NeuronModel",
    "SpikeEncoding",
]
