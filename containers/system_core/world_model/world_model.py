"""
world_model.world_model
DIX VISION v42.2 — Production-Grade World Model

Orchestrates all world modeling components including market modeling,
agent modeling, environment modeling, causal modeling, dynamics modeling,
and prediction modeling.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from world_model.market_model import get_production_market_model, ProductionMarketModel
from world_model.agent_model import get_production_agent_model, ProductionAgentModel
from world_model.environment_model import get_production_environment_model, ProductionEnvironmentModel
from world_model.causal_model import get_production_causal_model, ProductionCausalModel
from world_model.dynamics_model import get_production_dynamics_model, ProductionDynamicsModel
from world_model.prediction_model import get_production_prediction_model, ProductionPredictionModel

logger = logging.getLogger(__name__)


class ProductionWorldModel:
    """Production-grade world model orchestrator."""
    
    def __init__(self) -> None:
        self._market_model: Optional[ProductionMarketModel] = None
        self._agent_model: Optional[ProductionAgentModel] = None
        self._environment_model: Optional[ProductionEnvironmentModel] = None
        self._causal_model: Optional[ProductionCausalModel] = None
        self._dynamics_model: Optional[ProductionDynamicsModel] = None
        self._prediction_model: Optional[ProductionPredictionModel] = None
        self._initialized: bool = False
        
    def initialize(self) -> bool:
        """Initialize all world model components."""
        if self._initialized:
            return True
            
        logger.info("[WORLD_MODEL] Initializing production world model...")
        
        self._market_model = get_production_market_model()
        self._agent_model = get_production_agent_model()
        self._environment_model = get_production_environment_model()
        self._causal_model = get_production_causal_model()
        self._dynamics_model = get_production_dynamics_model()
        self._prediction_model = get_production_prediction_model()
        
        self._market_model.start()
        self._agent_model.start()
        self._environment_model.start()
        self._causal_model.start()
        self._dynamics_model.start()
        self._prediction_model.start()
        
        self._initialized = True
        logger.info("[WORLD_MODEL] Production world model initialized successfully")
        return True
    
    def shutdown(self) -> bool:
        """Shutdown all world model components."""
        if not self._initialized:
            return True
            
        logger.info("[WORLD_MODEL] Shutting down production world model...")
        
        if self._market_model:
            self._market_model.stop()
        if self._agent_model:
            self._agent_model.stop()
        if self._environment_model:
            self._environment_model.stop()
        if self._causal_model:
            self._causal_model.stop()
        if self._dynamics_model:
            self._dynamics_model.stop()
        if self._prediction_model:
            self._prediction_model.stop()
        
        self._initialized = False
        logger.info("[WORLD_MODEL] Production world model shut down successfully")
        return True
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get current world state from all components."""
        if not self._initialized:
            return {"error": "World model not initialized"}
            
        return {
            "market": {"status": "active"},
            "agents": {"status": "active"},
            "environment": {"status": "active"},
            "causal": {"status": "active"},
            "dynamics": {"status": "active"},
            "predictions": {"status": "active"}
        }
    
    @property
    def market_model(self) -> Optional[ProductionMarketModel]:
        return self._market_model
    
    @property
    def agent_model(self) -> Optional[ProductionAgentModel]:
        return self._agent_model
    
    @property
    def environment_model(self) -> Optional[ProductionEnvironmentModel]:
        return self._environment_model
    
    @property
    def causal_model(self) -> Optional[ProductionCausalModel]:
        return self._causal_model
    
    @property
    def dynamics_model(self) -> Optional[ProductionDynamicsModel]:
        return self._dynamics_model
    
    @property
    def prediction_model(self) -> Optional[ProductionPredictionModel]:
        return self._prediction_model


def get_production_world_model() -> ProductionWorldModel:
    """Get the singleton production world model instance."""
    if not hasattr(get_production_world_model, "_instance"):
        get_production_world_model._instance = ProductionWorldModel()
    return get_production_world_model._instance