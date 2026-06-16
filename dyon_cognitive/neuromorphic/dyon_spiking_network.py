"""Spiking Neural Network for DYON Engineering Intelligence.

This module provides spiking neural network (SNN) capabilities for DYON,
enabling event-driven, energy-efficient system monitoring, anomaly detection,
and engineering intelligence with temporal pattern recognition.
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


class SystemSignalType(str, Enum):
    """Types of system signals for DYON."""
    PERFORMANCE_METRIC = "PERFORMANCE_METRIC"
    RESOURCE_USAGE = "RESOURCE_USAGE"
    EVENT_RATE = "EVENT_RATE"
    ERROR_RATE = "ERROR_RATE"
    LATENCY = "LATENCY"
    MEMORY_PRESSURE = "MEMORY_PRESSURE"
    CODE_QUALITY = "CODE_QUALITY"
    TEST_COVERAGE = "TEST_COVERAGE"


@dataclass
class SystemSpikeEvent:
    """System event converted to spike."""
    event_id: str
    signal_type: SystemSignalType
    component: str
    spike_train: List[float]  # Spike times
    raw_value: float
    timestamp: float


@dataclass
class DYONSNNResponse:
    """Response from DYON spiking neural network."""
    response_id: str
    anomaly_score: float
    system_health_signal: float
    resource_pressure_signal: float
    performance_degradation_signal: float
    temporal_features: Dict[str, float]
    confidence: float
    timestamp: float


class DYONLeakyIntegrateFireNeuron:
    """LIF neuron for DYON system monitoring."""

    def __init__(self, neuron_id: str, tau_mem: float = 15.0,
                 threshold: float = 1.0, sensitivity: float = 0.1):
        """
        Initialize DYON LIF neuron.
        
        Args:
            tau_mem: Membrane time constant (ms) - faster for system monitoring
            threshold: Firing threshold
            sensitivity: Sensitivity to input signals
        """
        self.neuron_id = neuron_id
        self.tau_mem = tau_mem
        self.threshold = threshold
        self.sensitivity = sensitivity
        
        self.membrane_potential = 0.0
        self.last_spike_time = -float('inf')
        self.spike_history: deque = deque(maxlen=500)
        
        # Adaptive parameters for system monitoring
        self.baseline_potential = 0.0
        self.adaptation_rate = 0.05
    
    def process_system_signal(self, signal_value: float, timestamp: float,
                             dt: float = 1.0) -> Optional[float]:
        """
        Process system signal.
        
        Args:
            signal_value: Normalized system signal value (0-1)
            timestamp: Signal timestamp
            dt: Time step
        
        Returns:
            Spike time if neuron fires, None otherwise
        """
        # Apply sensitivity
        input_current = signal_value * self.sensitivity
        
        # Update membrane potential with leak
        leak = (self.baseline_potential - self.membrane_potential) / self.tau_mem
        self.membrane_potential += (leak * dt) + input_current
        
        # Slow adaptation to baseline
        self.baseline_potential += (self.membrane_potential - self.baseline_potential) * self.adaptation_rate
        
        # Check threshold
        if self.membrane_potential >= self.threshold:
            # Neuron fires
            self.membrane_potential = 0.0
            self.last_spike_time = timestamp
            self.spike_history.append(timestamp)
            return timestamp
        
        return None
    
    def get_firing_rate(self, window_ms: float = 1000.0) -> float:
        """Calculate firing rate in spikes per second."""
        current_time = time.time() * 1000  # Convert to ms
        recent_spikes = [t for t in self.spike_history if current_time - t < window_ms]
        
        if window_ms > 0:
            return len(recent_spikes) / (window_ms / 1000.0)
        return 0.0


class DYONSpikingNetwork:
    """Spiking neural network for DYON engineering intelligence."""

    def __init__(self, n_signal_neurons: int = 20,
                 n_hidden_neurons: int = 50,
                 n_anomaly_neurons: int = 10):
        """
        Initialize DYON spiking network.
        
        Args:
            n_signal_neurons: Number of signal processing neurons
            n_hidden_neurons: Number of hidden layer neurons
            n_anomaly_neurons: Number of anomaly detection neurons
        """
        self.n_signal_neurons = n_signal_neurons
        self.n_hidden_neurons = n_hidden_neurons
        self.n_anomaly_neurons = n_anomaly_neurons
        
        # Create specialized neurons
        self.signal_neurons = [
            DYONLeakyIntegrateFireNeuron(f"signal_{i}", sensitivity=0.15)
            for i in range(n_signal_neurons)
        ]
        
        self.hidden_neurons = [
            DYONLeakyIntegrateFireNeuron(f"hidden_{i}", sensitivity=0.1)
            for i in range(n_hidden_neurons)
        ]
        
        self.anomaly_neurons = [
            DYONLeakyIntegrateFireNeuron(f"anomaly_{i}", sensitivity=0.2)
            for i in range(n_anomaly_neurons)
        ]
        
        # Connection weights
        self.signal_to_hidden_weights = np.random.uniform(0.1, 0.5, 
                                                          (n_signal_neurons, n_hidden_neurons))
        self.hidden_to_anomaly_weights = np.random.uniform(0.2, 0.8, 
                                                          (n_hidden_neurons, n_anomaly_neurons))
        
        # Spike history
        self.anomaly_spike_history: deque = deque(maxlen=100)
        
        self.lock = threading.Lock()
        
        logger.info(f"[DYON_SNN] DYON Spiking Network initialized with "
                   f"{n_signal_neurons} signal, {n_hidden_neurons} hidden, "
                   f"{n_anomaly_neurons} anomaly neurons")
    
    def encode_system_signals(self, system_metrics: Dict[str, float]) -> List[SystemSpikeEvent]:
        """
        Encode system metrics to spike events.
        
        Args:
            system_metrics: Dictionary of system metrics
        
        Returns:
            List of system spike events
        """
        spike_events = []
        current_time = time.time() * 1000  # Convert to ms
        
        # Encode different signal types
        metric_mappings = {
            "cpu_usage": (SystemSignalType.RESOURCE_USAGE, "cpu", 0),
            "memory_usage": (SystemSignalType.MEMORY_PRESSURE, "memory", 1),
            "latency_p99": (SystemSignalType.LATENCY, "latency", 2),
            "error_rate": (SystemSignalType.ERROR_RATE, "errors", 3),
            "event_rate": (SystemSignalType.EVENT_RATE, "events", 4),
            "test_coverage": (SystemSignalType.TEST_COVERAGE, "coverage", 5),
            "code_complexity": (SystemSignalType.CODE_QUALITY, "complexity", 6),
        }
        
        for metric_name, (signal_type, component, neuron_idx) in metric_mappings.items():
            if metric_name in system_metrics:
                value = system_metrics[metric_name]
                normalized_value = self._normalize_metric(metric_name, value)
                
                # Generate spike based on signal strength
                if normalized_value > 0.7:  # High signal strength
                    spike_events.append(SystemSpikeEvent(
                        event_id=f"{metric_name}_spike_{int(current_time)}",
                        signal_type=signal_type,
                        component=component,
                        spike_train=[current_time],
                        raw_value=value,
                        timestamp=time.time()
                    ))
        
        return spike_events
    
    def _normalize_metric(self, metric_name: str, value: float) -> float:
        """Normalize system metric to 0-1 range."""
        normalization_rules = {
            "cpu_usage": lambda v: v / 100.0,
            "memory_usage": lambda v: v / 100.0,
            "latency_p99": lambda v: min(v / 1000.0, 1.0),
            "error_rate": lambda v: min(v * 10.0, 1.0),
            "event_rate": lambda v: min(v / 1000.0, 1.0),
            "test_coverage": lambda v: v / 100.0,
            "code_complexity": lambda v: min(v / 50.0, 1.0),
        }
        
        return normalization_rules.get(metric_name, lambda v: v)(value)
    
    def process_signals(self, spike_events: List[SystemSpikeEvent],
                       dt: float = 1.0, duration_ms: float = 100.0) -> DYONSNNResponse:
        """
        Process system signals through the network.
        
        Args:
            spike_events: List of spike events
            dt: Time step
            duration_ms: Duration to simulate
        
        Returns:
            DYON SNN response
        """
        with self.lock:
            response_id = f"dyon_snn_response_{int(time.time())}"
            
            # Reset neurons
            self._reset_neurons()
            
            # Simulate network
            time_steps = int(duration_ms / dt)
            
            total_anomaly_spikes = 0
            signal_spike_counts = [0] * self.n_signal_neurons
            
            for t in range(time_steps):
                current_time_ms = t * dt
                
                # Process signal layer
                for event in spike_events:
                    for spike_time_ms in event.spike_train:
                        if abs(spike_time_ms - current_time_ms) < dt:
                            # Find appropriate signal neuron
                            neuron_idx = min(signal_spike_counts.index(min(signal_spike_counts)),
                                           len(self.signal_neurons) - 1)
                            self.signal_neurons[neuron_idx].process_system_signal(
                                event.raw_value / 100.0, current_time_ms, dt
                            )
                            signal_spike_counts[neuron_idx] += 1
                
                # Propagate to hidden layer
                for i, signal_neuron in enumerate(self.signal_neurons):
                    if signal_neuron.last_spike_time == current_time_ms:
                        for j, hidden_neuron in enumerate(self.hidden_neurons):
                            weight = self.signal_to_hidden_weights[i, j]
                            hidden_neuron.process_system_signal(weight, current_time_ms, dt)
                
                # Propagate to anomaly layer
                for i, hidden_neuron in enumerate(self.hidden_neurons):
                    if hidden_neuron.last_spike_time == current_time_ms:
                        for j, anomaly_neuron in enumerate(self.anomaly_neurons):
                            weight = self.hidden_to_anomaly_weights[i, j]
                            if anomaly_neuron.process_system_signal(weight, current_time_ms, dt):
                                total_anomaly_spikes += 1
                                self.anomaly_spike_history.append(current_time_ms)
            
            # Calculate signals
            anomaly_score = min(total_anomaly_spikes / self.n_anomaly_neurons, 1.0)
            system_health_signal = 1.0 - anomaly_score
            resource_pressure_signal = self._calculate_resource_pressure()
            performance_degradation_signal = self._calculate_performance_degradation()
            
            # Extract temporal features
            temporal_features = self._extract_temporal_features()
            
            # Calculate confidence
            confidence = min(1.0, len(spike_events) / 10.0) if spike_events else 0.5
            
            response = DYONSNNResponse(
                response_id=response_id,
                anomaly_score=anomaly_score,
                system_health_signal=system_health_signal,
                resource_pressure_signal=resource_pressure_signal,
                performance_degradation_signal=performance_degradation_signal,
                temporal_features=temporal_features,
                confidence=confidence,
                timestamp=time.time()
            )
            
            return response
    
    def _reset_neurons(self) -> None:
        """Reset all neurons."""
        for neuron in self.signal_neurons + self.hidden_neurons + self.anomaly_neurons:
            neuron.membrane_potential = 0.0
            neuron.last_spike_time = -float('inf')
    
    def _calculate_resource_pressure(self) -> float:
        """Calculate resource pressure signal."""
        cpu_rate = self.signal_neurons[0].get_firing_rate() if len(self.signal_neurons) > 0 else 0.0
        memory_rate = self.signal_neurons[1].get_firing_rate() if len(self.signal_neurons) > 1 else 0.0
        
        # Normalize firing rates to 0-1 range
        resource_pressure = min((cpu_rate + memory_rate) / 20.0, 1.0)
        return resource_pressure
    
    def _calculate_performance_degradation(self) -> float:
        """Calculate performance degradation signal."""
        latency_rate = self.signal_neurons[2].get_firing_rate() if len(self.signal_neurons) > 2 else 0.0
        error_rate = self.signal_neurons[3].get_firing_rate() if len(self.signal_neurons) > 3 else 0.0
        
        degradation = (latency_rate + error_rate) / 20.0  # Normalize
        return min(1.0, degradation)
    
    def _extract_temporal_features(self) -> Dict[str, float]:
        """Extract temporal features from spike history."""
        if not self.anomaly_spike_history:
            return {"spike_rate": 0.0, "burstiness": 0.0, "regularity": 0.5}
        
        spikes = list(self.anomaly_spike_history)
        spike_rate = len(spikes) / 10.0  # Rate over recent window
        
        # Calculate burstiness (variance in inter-spike intervals)
        if len(spikes) > 1:
            isis = np.diff(spikes)
            burstiness = np.std(isis) / (np.mean(isis) if np.mean(isis) > 0 else 1.0)
        else:
            burstiness = 0.0
        
        # Calculate regularity (inverse of burstiness)
        regularity = 1.0 / (1.0 + burstiness)
        
        return {
            "spike_rate": float(spike_rate),
            "burstiness": float(burstiness),
            "regularity": float(regularity)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get network statistics."""
        with self.lock:
            return {
                "n_signal_neurons": self.n_signal_neurons,
                "n_hidden_neurons": self.n_hidden_neurons,
                "n_anomaly_neurons": self.n_anomaly_neurons,
                "total_anomaly_spikes": len(self.anomaly_spike_history),
                "average_anomaly_spike_rate": len(self.anomaly_spike_history) / max(1, len(self.anomaly_spike_history))
            }


class DYONSpikingIntelligence:
    """DYON spiking intelligence integration."""

    def __init__(self):
        self.snn = DYONSpikingNetwork()
        self._initialized = False
    
    def start(self) -> bool:
        """Start DYON spiking intelligence."""
        logger.info("[DYON_SNN] Starting DYON spiking intelligence...")
        self._initialized = True
        logger.info("[DYON_SNN] DYON spiking intelligence started")
        return True
    
    def stop(self) -> bool:
        """Stop DYON spiking intelligence."""
        logger.info("[DYON_SNN] Stopping DYON spiking intelligence...")
        self._initialized = False
        logger.info("[DYON_SNN] DYON spiking intelligence stopped")
        return True
    
    def analyze_system_with_snn(self, system_metrics: Dict[str, float]) -> DYONSNNResponse:
        """Analyze system metrics using spiking neural network."""
        # Encode metrics to spikes
        spike_events = self.snn.encode_system_signals(system_metrics)
        
        # Process through SNN
        response = self.snn.process_signals(spike_events)
        
        return response
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get DYON spiking intelligence statistics."""
        return self.snn.get_statistics()


# Singleton instance
_dyon_spiking_intelligence: Optional[DYONSpikingIntelligence] = None
_dyon_spiking_intelligence_lock = threading.Lock()


def get_dyon_spiking_intelligence() -> DYONSpikingIntelligence:
    """Get the singleton DYON spiking intelligence instance."""
    global _dyon_spiking_intelligence
    if _dyon_spiking_intelligence is None:
        with _dyon_spiking_intelligence_lock:
            if _dyon_spiking_intelligence is None:
                _dyon_spiking_intelligence = DYONSpikingIntelligence()
    return _dyon_spiking_intelligence


__all__ = [
    "DYONSpikingIntelligence",
    "get_dyon_spiking_intelligence",
    "DYONSpikingNetwork",
    "DYONLeakyIntegrateFireNeuron",
    "SystemSpikeEvent",
    "DYONSNNResponse",
    "SystemSignalType",
]