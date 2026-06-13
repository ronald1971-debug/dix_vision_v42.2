"""
coordination_layer.concrete
DIX VISION v42.2 — Concrete Coordination Layer Implementation

Concrete implementation of Coordination Layer for cross-agent coordination with ACL protocols,
conflict resolution, shared mental models, resource allocation, and distributed governance.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import threading

from coordination_layer import (
    CoordinationLayerInterface,
    CoordinationStatus,
    ConflictType,
    CrossAgentConflict,
    KnowledgeExchangeRequest,
    ResourceAllocation,
    GovernancePolicy,
    EmergencyCoordination,
    CoordinationMetrics,
)
from indira_cognitive.shared_interfaces.enhanced_types import (
    ACLMessage,
    ConflictResolutionProposal,
    SharedMentalModel,
)
from coordination_layer.cognitive_economy import CognitiveEconomyManager, get_cognitive_economy_manager
from coordination_layer.operating_modes import OperatingModeManager, get_operating_mode_manager
from coordination_layer.learning_gate import LearningGateManager, get_learning_gate_manager


logger = logging.getLogger(__name__)


class ConcreteCoordinationLayer(CoordinationLayerInterface):
    """
    Concrete implementation of Coordination Layer for cross-agent coordination.
    
    Enhanced Features:
    - ACL protocol implementation
    - Advanced conflict resolution with negotiation
    - Event-driven knowledge exchange
    - Shared mental models with metacognitive alignment
    - Optimized resource allocation
    - Distributed governance
    - Emergency coordination with fault tolerance
    - Comprehensive monitoring
    - Integration with cognitive economy, operating modes, and learning gate
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        
        # Communication
        self._acl_messages: Dict[str, ACLMessage] = {}
        self._message_queue: List[ACLMessage] = []
        
        # Conflict management
        self._conflicts: Dict[str, CrossAgentConflict] = {}
        self._resolution_history: List[Dict[str, Any]] = []
        
        # Knowledge exchange
        self._knowledge_exchanges: Dict[str, KnowledgeExchangeRequest] = {}
        
        # Resource allocation
        self._resource_allocations: Dict[str, ResourceAllocation] = {}
        
        # Governance
        self._governance_policies: Dict[str, GovernancePolicy] = {}
        
        # Shared mental models
        self._shared_mental_models: Dict[str, SharedMentalModel] = {}
        
        # Emergency coordination
        self._emergency_coordination: Dict[str, EmergencyCoordination] = {}
        
        # Metrics
        self._metrics = CoordinationMetrics(
            metrics_id=f"coordination_metrics_{int(datetime.utcnow().timestamp())}"
        )
        
        # Integration with coordination components
        self._cognitive_economy: Optional[CognitiveEconomyManager] = None
        self._operating_modes: Optional[OperatingModeManager] = None
        self._learning_gate: Optional[LearningGateManager] = None
        
        # Agent registry
        self._registered_agents: Dict[str, Dict[str, Any]] = {}
        
        # Conversation tracking
        self._conversations: Dict[str, Dict[str, Any]] = {}
        
        # Protocol registry
        self._protocols: Dict[str, List[str]] = {
            "fipa_request": ["REQUEST", "AGREE", "REFUSE", "INFORM", "FAILURE"],
            "fipa_query": ["QUERY", "INFORM", "NOT_UNDERSTOOD"],
            "fipa_contract_net": ["CALL_FOR_PROPOSAL", "PROPOSE", "ACCEPT", "REJECT", "INFORM", "FAILURE"],
            "fipa_subscribe": ["SUBSCRIBE", "INFORM", "UNSUBSCRIBE"]
        }
        
        logger.info("[COORDINATION_LAYER] Concrete Coordination Layer initialized")
    
    def connect_coordination_components(
        self,
        cognitive_economy: CognitiveEconomyManager = None,
        operating_modes: OperatingModeManager = None,
        learning_gate: LearningGateManager = None
    ) -> None:
        """Connect to coordination components."""
        with self._lock:
            self._cognitive_economy = cognitive_economy or get_cognitive_economy_manager()
            self._operating_modes = operating_modes or get_operating_mode_manager()
            self._learning_gate = learning_gate or get_learning_gate_manager()
            
            logger.info("[COORDINATION_LAYER] Connected to coordination components")
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]) -> bool:
        """Register an agent with the coordination layer."""
        with self._lock:
            self._registered_agents[agent_id] = agent_info
            logger.info(f"[COORDINATION_LAYER] Registered agent: {agent_id}")
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the coordination layer."""
        with self._lock:
            if agent_id in self._registered_agents:
                del self._registered_agents[agent_id]
                logger.info(f"[COORDINATION_LAYER] Unregistered agent: {agent_id}")
                return True
            return False
    
    def send_acl_message(
        self,
        message: ACLMessage
    ) -> ACLMessage | None:
        """
        Send ACL message between agents.
        Enhanced with standard ACL protocol implementation.
        """
        try:
            # Validate message structure
            if not message.receiver_id:
                logger.warning("[COORDINATION_LAYER] ACL message missing receiver_id")
                return None
            
            if not message.sender_id:
                logger.warning("[COORDINATION_LAYER] ACL message missing sender_id")
                return None
            
            if not message.performative:
                logger.warning("[COORDINATION_LAYER] ACL message missing performative")
                return None
            
            # Check if receiver is registered
            if message.receiver_id not in self._registered_agents:
                logger.warning(f"[COORDINATION_LAYER] Receiver {message.receiver_id} not registered")
                return None
            
            # Validate performative (FIPA ACL standard performatives)
            valid_performatives = [
                "REQUEST", "INFORM", "QUERY", "PROPOSE", "ACCEPT",
                "REJECT", "CANCEL", "CALL_FOR_PROPOSAL", "AGREE",
                "REFUSE", "FAILURE", "NOT_UNDERSTOOD", "PROXY",
                "SUBSCRIBE", "UNSUBSCRIBE"
            ]
            if message.performative.upper() not in valid_performatives:
                logger.warning(f"[COORDINATION_LAYER] Invalid performative: {message.performative}")
                # Still allow it but with warning for extensibility
            
            # Add timestamp if not present
            if not message.timestamp:
                message.timestamp = datetime.utcnow()
            
            # Add reply_with if not present (for correlation)
            if not message.reply_with and message.performative in ["QUERY", "REQUEST"]:
                message.reply_with = f"reply_to_{message.message_id}"
            
            # Store message in message registry
            self._acl_messages[message.message_id] = message
            
            # Add to message queue with priority handling
            message_priority = message.metadata.get("priority", 5)  # Default priority 5 (1-10)
            self._message_queue.append(message)
            
            # Sort queue by priority (higher priority first)
            self._message_queue.sort(
                key=lambda m: m.metadata.get("priority", 5),
                reverse=True
            )
            
            # Update metrics
            self._metrics.messages_sent += 1
            
            # Check if acknowledgment is required
            if message.metadata.get("require_ack", False):
                # In a real implementation, this would wait for acknowledgment
                pass
            
            # Check if this is a conversation message and update conversation tracking
            if message.in_reply_to:
                self._metrics.concurrent_conversations += 1
            
            logger.info(f"[COORDINATION_LAYER] ACL message sent: {message.message_id} "
                       f"{message.performative} from {message.sender_id} to {message.receiver_id}")
            
            return message
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to send ACL message: {e}")
            return None
    
    def receive_acl_message(self, message: ACLMessage) -> bool:
        """Receive an ACL message."""
        try:
            self._message_queue.append(message)
            self._acl_messages[message.message_id] = message
            self._metrics.messages_received += 1
            
            logger.info(f"[COORDINATION_LAYER] ACL message received: {message.message_id}")
            return True
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to receive ACL message: {e}")
            return False
    
    def start_conversation(
        self,
        conversation_id: str,
        initiator_id: str,
        participant_ids: List[str],
        protocol: str = "fipa_request"
    ) -> Dict[str, Any]:
        """Start a new conversation between agents."""
        try:
            # Validate protocol
            if protocol not in self._protocols:
                logger.warning(f"[COORDINATION_LAYER] Unknown protocol: {protocol}")
                protocol = "fipa_request"  # Default to basic request protocol
            
            conversation = {
                "conversation_id": conversation_id,
                "initiator": initiator_id,
                "participants": participant_ids,
                "protocol": protocol,
                "status": "ACTIVE",
                "started_at": datetime.utcnow().isoformat(),
                "messages": [],
                "current_step": 0
            }
            
            self._conversations[conversation_id] = conversation
            
            logger.info(f"[COORDINATION_LAYER] Conversation started: {conversation_id} "
                       f"with protocol {protocol}")
            
            return conversation
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to start conversation: {e}")
            return {"error": str(e)}
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation details."""
        return self._conversations.get(conversation_id)
    
    def end_conversation(
        self,
        conversation_id: str,
        outcome: str = "COMPLETED"
    ) -> bool:
        """End a conversation."""
        try:
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                logger.warning(f"[COORDINATION_LAYER] Conversation {conversation_id} not found")
                return False
            
            conversation["status"] = outcome
            conversation["ended_at"] = datetime.utcnow().isoformat()
            
            # Update metrics
            self._metrics.concurrent_conversations -= 1
            
            logger.info(f"[COORDINATION_LAYER] Conversation ended: {conversation_id} with outcome {outcome}")
            
            return True
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to end conversation: {e}")
            return False
    
    def check_protocol_conformance(
        self,
        message: ACLMessage,
        conversation_id: Optional[str] = None
    ) -> bool:
        """Check if a message conforms to the expected protocol."""
        try:
            # If no conversation, perform basic validation
            if not conversation_id:
                return True  # Basic messages are always conformant
            
            conversation = self._conversations.get(conversation_id)
            if not conversation:
                logger.warning(f"[COORDINATION_LAYER] Conversation {conversation_id} not found")
                return False
            
            protocol = conversation.get("protocol", "fipa_request")
            expected_performatives = self._protocols.get(protocol, [])
            
            # Check if message performative is in expected protocol
            if message.performative.upper() not in expected_performatives:
                logger.warning(f"[COORDINATION_LAYER] Message performative {message.performative} "
                             f"not in protocol {protocol}")
                return False
            
            # Check protocol flow (simplified)
            current_step = conversation.get("current_step", 0)
            if current_step >= len(expected_performatives):
                logger.warning(f"[COORDINATION_LAYER] Conversation has completed all steps")
                return False
            
            # Check if this is the expected performative for current step
            expected = expected_performatives[current_step]
            if message.performative.upper() != expected:
                # Allow some flexibility for branching protocols
                logger.info(f"[COORDINATION_LAYER] Message performative {message.performative} "
                          f"differs from expected {expected}")
                # Still allow it for flexibility
                return True
            
            # Update conversation step
            conversation["current_step"] = current_step + 1
            
            return True
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Protocol conformance check failed: {e}")
            return False
    
    def route_message(
        self,
        message: ACLMessage,
        routing_strategy: str = "direct"
    ) -> List[str]:
        """Determine routing for a message based on strategy."""
        try:
            recipients = []
            
            if routing_strategy == "direct":
                # Direct routing to specified receiver
                if message.receiver_id:
                    recipients.append(message.receiver_id)
            
            elif routing_strategy == "broadcast":
                # Broadcast to all registered agents except sender
                recipients = [
                    agent_id for agent_id in self._registered_agents.keys()
                    if agent_id != message.sender_id
                ]
            
            elif routing_strategy == "multicast":
                # Multicast to specified receivers
                multicast_receivers = message.metadata.get("receivers", [])
                recipients = [
                    r for r in multicast_receivers 
                    if r in self._registered_agents and r != message.sender_id
                ]
            
            elif routing_strategy == "role_based":
                # Route based on agent roles
                target_role = message.metadata.get("target_role")
                if target_role:
                    recipients = [
                        agent_id for agent_id, agent_info in self._registered_agents.items()
                        if agent_info.get("type") == target_role and agent_id != message.sender_id
                    ]
            
            else:
                logger.warning(f"[COORDINATION_LAYER] Unknown routing strategy: {routing_strategy}")
                # Default to direct routing
                if message.receiver_id:
                    recipients.append(message.receiver_id)
            
            logger.info(f"[COORDINATION_LAYER] Message routing: {routing_strategy} -> {len(recipients)} recipients")
            
            return recipients
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Message routing failed: {e}")
            return []
    
    def apply_message_filter(
        self,
        message: ACLMessage,
        filter_rules: Dict[str, Any]
    ) -> bool:
        """Apply filtering rules to a message."""
        try:
            # Check performative filter
            allowed_performatives = filter_rules.get("allowed_performatives", [])
            if allowed_performatives and message.performative not in allowed_performatives:
                logger.info(f"[COORDINATION_LAYER] Message filtered by performative: {message.performative}")
                return False
            
            # Check sender filter
            blocked_senders = filter_rules.get("blocked_senders", [])
            if message.sender_id in blocked_senders:
                logger.info(f"[COORDINATION_LAYER] Message filtered by sender: {message.sender_id}")
                return False
            
            # Check priority filter
            min_priority = filter_rules.get("min_priority", 0)
            message_priority = message.metadata.get("priority", 5)
            if message_priority < min_priority:
                logger.info(f"[COORDINATION_LAYER] Message filtered by priority: {message_priority}")
                return False
            
            # Check size filter
            max_size = filter_rules.get("max_size_kb", 1000)
            message_size = len(str(message.content)) / 1024  # Simple size estimate
            if message_size > max_size:
                logger.info(f"[COORDINATION_LAYER] Message filtered by size: {message_size} KB")
                return False
            
            # Message passed all filters
            return True
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Message filtering failed: {e}")
            return True  # Default to allow on filter failure
    
    def detect_conflict(
        self,
        conflict_type: ConflictType,
        agent_a_id: str,
        agent_b_id: str,
        description: str = "",
        context: Dict[str, Any] = None
    ) -> CrossAgentConflict:
        """Detect and register a cross-agent conflict."""
        try:
            conflict_id = f"conflict_{int(datetime.utcnow().timestamp())}"
            
            conflict = CrossAgentConflict(
                conflict_id=conflict_id,
                conflict_type=conflict_type,
                agent_a_id=agent_a_id,
                agent_b_id=agent_b_id,
                description=description,
                conflict_context=context or {},
                status=CoordinationStatus.CONFLICT,
                detected_at=datetime.utcnow()
            )
            
            # Store conflict
            self._conflicts[conflict_id] = conflict
            
            # Update metrics
            self._metrics.conflicts_detected += 1
            
            logger.info(f"[COORDINATION_LAYER] Conflict detected: {conflict_type.value} between {agent_a_id} and {agent_b_id}")
            
            return conflict
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to detect conflict: {e}")
            return CrossAgentConflict(
                conflict_id=f"conflict_error_{int(datetime.utcnow().timestamp())}",
                conflict_type=conflict_type,
                status=CoordinationStatus.FAILED,
                metadata={"error": str(e)}
            )
    
    def resolve_conflict(
        self,
        conflict_id: str,
        resolution: ConflictResolutionProposal,
        resolution_strategy: str = "negotiation"
    ) -> bool:
        """Resolve a cross-agent conflict with advanced resolution strategies."""
        try:
            conflict = self._conflicts.get(conflict_id)
            if not conflict:
                logger.warning(f"[COORDINATION_LAYER] Conflict {conflict_id} not found")
                return False
            
            # Apply resolution strategy
            strategy_result = self._apply_resolution_strategy(
                conflict, resolution, resolution_strategy
            )
            
            if not strategy_result:
                logger.warning(f"[COORDINATION_LAYER] Resolution strategy {resolution_strategy} failed")
                return False
            
            # Accept the resolution
            conflict.accepted_resolution = resolution
            conflict.status = CoordinationStatus.RESOLVED
            conflict.resolved_at = datetime.utcnow()
            
            # Record resolution with strategy
            self._resolution_history.append({
                "conflict_id": conflict_id,
                "resolution_id": resolution.proposal_id,
                "resolution_type": resolution.resolution_type,
                "resolution_strategy": resolution_strategy,
                "resolved_at": datetime.utcnow().isoformat()
            })
            
            # Update metrics
            self._metrics.conflicts_resolved += 1
            if self._metrics.conflicts_detected > 0:
                self._metrics.resolution_success_rate = (
                    self._metrics.conflicts_resolved / self._metrics.conflicts_detected
                )
            
            logger.info(f"[COORDINATION_LAYER] Conflict resolved: {conflict_id} using {resolution_strategy}")
            
            return True
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to resolve conflict: {e}")
            return False
    
    def _apply_resolution_strategy(
        self,
        conflict: CrossAgentConflict,
        resolution: ConflictResolutionProposal,
        strategy: str
    ) -> bool:
        """Apply specific resolution strategy to conflict."""
        try:
            if strategy == "negotiation":
                return self._resolve_by_negotiation(conflict, resolution)
            elif strategy == "voting":
                return self._resolve_by_voting(conflict, resolution)
            elif strategy == "priority":
                return self._resolve_by_priority(conflict, resolution)
            elif strategy == "arbitration":
                return self._resolve_by_arbitration(conflict, resolution)
            else:
                logger.warning(f"[COORDINATION_LAYER] Unknown resolution strategy: {strategy}")
                return self._resolve_by_priority(conflict, resolution)  # Default to priority
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Resolution strategy application failed: {e}")
            return False
    
    def _resolve_by_negotiation(
        self,
        conflict: CrossAgentConflict,
        resolution: ConflictResolutionProposal
    ) -> bool:
        """Resolve conflict through negotiation."""
        try:
            # In a real implementation, this would:
            # 1. Send negotiation messages to both parties
            # 2. Collect proposals and counter-proposals
            # 3. Find acceptable compromise
            # 4. Verify agreement from both parties
            
            # Simplified negotiation simulation
            logger.info(f"[COORDINATION_LAYER] Negotiation resolution for conflict {conflict.conflict_id}")
            
            # Check if resolution is reasonable (simulated)
            if resolution.resolution_confidence > 0.6:
                return True
            else:
                logger.warning(f"[COORDINATION_LAYER] Negotiation resolution confidence too low")
                return False
                
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Negotiation resolution failed: {e}")
            return False
    
    def _resolve_by_voting(
        self,
        conflict: CrossAgentConflict,
        resolution: ConflictResolutionProposal
    ) -> bool:
        """Resolve conflict through voting."""
        try:
            # In a real implementation, this would:
            # 1. Gather votes from registered agents
            # 2. Apply voting rules (simple majority, weighted, etc.)
            # 3. Determine winning resolution
            
            # Simplified voting simulation
            logger.info(f"[COORDINATION_LAYER] Voting resolution for conflict {conflict.conflict_id}")
            
            # Check agent acceptance in resolution
            agent_acceptance = resolution.metadata.get("agent_acceptance", {})
            acceptance_count = sum(1 for accepted in agent_acceptance.values() if accepted)
            
            # Simple majority required
            total_agents = len(agent_acceptance)
            if total_agents > 0 and acceptance_count > total_agents / 2:
                logger.info(f"[COORDINATION_LAYER] Voting passed: {acceptance_count}/{total_agents}")
                return True
            else:
                logger.warning(f"[COORDINATION_LAYER] Voting failed: {acceptance_count}/{total_agents}")
                return False
                
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Voting resolution failed: {e}")
            return False
    
    def _resolve_by_priority(
        self,
        conflict: CrossAgentConflict,
        resolution: ConflictResolutionProposal
    ) -> bool:
        """Resolve conflict based on agent priorities."""
        try:
            # Check agent priorities
            agent_a_info = self._registered_agents.get(conflict.agent_a_id, {})
            agent_b_info = self._registered_agents.get(conflict.agent_b_id, {})
            
            priority_a = agent_a_info.get("priority", 5)  # Default priority 5
            priority_b = agent_b_info.get("priority", 5)
            
            logger.info(f"[COORDINATION_LAYER] Priority resolution: A={priority_a}, B={priority_b}")
            
            # Higher priority wins
            favored_agent = conflict.agent_a_id if priority_a > priority_b else conflict.agent_b_id
            
            # Check if resolution favors the higher priority agent
            resolution_favors = resolution.metadata.get("favored_agent")
            if resolution_favors == favored_agent:
                logger.info(f"[COORDINATION_LAYER] Priority resolution favors correct agent")
                return True
            else:
                logger.warning(f"[COORDINATION_LAYER] Priority resolution doesn't match priorities")
                return False
                
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Priority resolution failed: {e}")
            return False
    
    def _resolve_by_arbitration(
        self,
        conflict: CrossAgentConflict,
        resolution: ConflictResolutionProposal
    ) -> bool:
        """Resolve conflict through arbitration."""
        try:
            # In a real implementation, this would:
            # 1. Select arbitrator (third party or automated)
            # 2. Present conflict details to arbitrator
            # 3. Receive arbitration decision
            # 4. Enforce decision
            
            logger.info(f"[COORDINATION_LAYER] Arbitration resolution for conflict {conflict.conflict_id}")
            
            # Check if resolution has arbitrator validation
            arbitrator_validated = resolution.metadata.get("arbitrator_validated", False)
            
            if arbitrator_validated:
                logger.info(f"[COORDINATION_LAYER] Arbitration validated")
                return True
            else:
                logger.warning(f"[COORDINATION_LAYER] Arbitration not validated")
                return False
                
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Arbitration resolution failed: {e}")
            return False
    
    def initiate_knowledge_exchange(
        self,
        requesting_agent: str,
        target_agents: List[str],
        knowledge_type: str,
        knowledge_content: Dict[str, Any]
    ) -> KnowledgeExchangeRequest:
        """Initiate knowledge exchange between agents."""
        try:
            exchange_id = f"exchange_{int(datetime.utcnow().timestamp())}"
            
            request = KnowledgeExchangeRequest(
                exchange_id=exchange_id,
                requesting_agent=requesting_agent,
                target_agents=target_agents,
                knowledge_type=knowledge_type,
                knowledge_content=knowledge_content,
                status=CoordinationStatus.PENDING
            )
            
            # Store request
            self._knowledge_exchanges[exchange_id] = request
            
            # Update metrics
            self._metrics.knowledge_exchanges += 1
            
            logger.info(f"[COORDINATION_LAYER] Knowledge exchange initiated: {exchange_id}")
            
            return request
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to initiate knowledge exchange: {e}")
            return KnowledgeExchangeRequest(
                exchange_id=f"exchange_error_{int(datetime.utcnow().timestamp())}",
                requesting_agent=requesting_agent,
                target_agents=[],
                status=CoordinationStatus.FAILED,
                metadata={"error": str(e)}
            )
    
    def acknowledge_knowledge_exchange(
        self,
        exchange_id: str,
        agent_id: str
    ) -> bool:
        """Acknowledge receipt of knowledge exchange."""
        try:
            exchange = self._knowledge_exchanges.get(exchange_id)
            if not exchange:
                logger.warning(f"[COORDINATION_LAYER] Knowledge exchange {exchange_id} not found")
                return False
            
            if agent_id in exchange.target_agents:
                exchange.acknowledgments.append(agent_id)
                
                # Check if all agents have acknowledged
                if len(exchange.acknowledgments) == len(exchange.target_agents):
                    exchange.status = CoordinationStatus.COMPLETED
                    exchange.completion_timestamp = datetime.utcnow()
                    
                    # Update metrics
                    self._metrics.knowledge_shares_successful += 1
                
                logger.info(f"[COORDINATION_LAYER] Knowledge exchange acknowledged by {agent_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to acknowledge knowledge exchange: {e}")
            return False
    
    def allocate_resources(
        self,
        resource_type: str,
        agent_requests: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Allocate resources to agents based on demand and policies."""
        try:
            # Use cognitive economy manager if available
            if self._cognitive_economy:
                # Convert requests to format expected by cognitive economy
                demands = [
                    {
                        "operation_id": req.get("operation_id", f"op_{i}"),
                        "resource_type": resource_type,
                        "requested_amount": req.get("amount", 0.0),
                        "priority": req.get("priority", "medium"),
                        "expected_benefit": req.get("expected_benefit", 1.0)
                    }
                    for i, req in enumerate(agent_requests)
                ]
                
                resources = {"cpu": 100.0, "memory": 100.0}  # Default resources
                allocation = self._cognitive_economy.optimize_resource_allocation(resources, demands)
                
                # Update metrics
                self._metrics.allocation_requests += len(agent_requests)
                self._metrics.allocations_successful += len(allocation)
                
                logger.info(f"[COORDINATION_LAYER] Resources allocated: {len(allocation)} successful")
                
                return allocation
            
            # Fallback to simple allocation
            allocation = {}
            for req in agent_requests:
                agent_id = req.get("agent_id", f"agent_{len(allocation)}")
                allocation[agent_id] = req.get("amount", 0.0)
            
            logger.info(f"[COORDINATION_LAYER] Fallback resource allocation: {len(allocation)} allocations")
            
            return allocation
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to allocate resources: {e}")
            return {}
    
    def create_governance_policy(
        self,
        policy_name: str,
        policy_type: str,
        rules: List[str],
        constraints: List[str] = None,
        scope: List[str] = None
    ) -> GovernancePolicy:
        """Create a governance policy."""
        try:
            policy_id = f"policy_{int(datetime.utcnow().timestamp())}"
            
            policy = GovernancePolicy(
                policy_id=policy_id,
                policy_name=policy_name,
                policy_type=policy_type,
                policy_rules=rules,
                policy_constraints=constraints or [],
                scope=scope or [],
                enforcement_level="REQUIRED"
            )
            
            # Store policy
            self._governance_policies[policy_id] = policy
            
            logger.info(f"[COORDINATION_LAYER] Governance policy created: {policy_name}")
            
            return policy
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to create governance policy: {e}")
            return GovernancePolicy(
                policy_id=f"policy_error_{int(datetime.utcnow().timestamp())}",
                policy_name="error",
                policy_type="CUSTOM",
                active=False,
                metadata={"error": str(e)}
            )
    
    def handle_emergency(
        self,
        emergency_type: str,
        description: str,
        affected_agents: List[str] = None
    ) -> EmergencyCoordination:
        """Handle emergency coordination for system failures."""
        try:
            emergency_id = f"emergency_{int(datetime.utcnow().timestamp())}"
            
            emergency = EmergencyCoordination(
                emergency_id=emergency_id,
                emergency_type=emergency_type,
                description=description,
                affected_agents=affected_agents or [],
                status=CoordinationStatus.PENDING,
                severity="HIGH",
                detected_at=datetime.utcnow()
            )
            
            # Store emergency
            self._emergency_coordination[emergency_id] = emergency
            
            # Switch operating mode to emergency if available
            if self._operating_modes:
                try:
                    self._operating_modes.set_gate_state(
                        "EMERGENCY",
                        reason=f"Emergency: {emergency_type}"
                    )
                except Exception as e:
                    logger.warning(f"[COORDINATION_LAYER] Failed to set emergency mode: {e}")
            
            # Generate response actions
            response_actions = [
                f"Activate emergency protocols for {emergency_type}",
                "Pause non-essential operations",
                "Prioritize critical functions"
            ]
            
            emergency.response_actions = response_actions
            emergency.status = CoordinationStatus.PROCESSING
            emergency.response_started_at = datetime.utcnow()
            
            logger.warning(f"[COORDINATION_LAYER] Emergency coordination initiated: {emergency_type}")
            
            return emergency
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to handle emergency: {e}")
            return EmergencyCoordination(
                emergency_id=f"emergency_error_{int(datetime.utcnow().timestamp())}",
                emergency_type=emergency_type,
                status=CoordinationLayer.FAILED,
                metadata={"error": str(e)}
            )
    
    def resolve_emergency(self, emergency_id: str) -> bool:
        """Resolve an emergency situation."""
        try:
            emergency = self._emergency_coordination.get(emergency_id)
            if not emergency:
                logger.warning(f"[COORDINATION_LAYER] Emergency {emergency_id} not found")
                return False
            
            emergency.status = CoordinationStatus.COMPLETED
            emergency.resolved_at = datetime.utcnow()
            
            # Restore normal operating mode if available
            if self._operating_modes:
                try:
                    self._operating_modes.set_gate_state(
                        "ACTIVE",
                        reason=f"Emergency resolved: {emergency_id}"
                    )
                except Exception as e:
                    logger.warning(f"[COORDINATION_LAYER] Failed to restore active mode: {e}")
            
            logger.info(f"[COORDINATION_LAYER] Emergency resolved: {emergency_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to resolve emergency: {e}")
            return False
    
    def create_shared_mental_model(
        self,
        model_id: str,
        model_type: str,
        beliefs: Dict[str, Any],
        goals: List[str]
    ) -> SharedMentalModel:
        """Create a shared mental model for agent alignment."""
        try:
            model = SharedMentalModel(
                model_id=model_id,
                model_type=model_type,
                model_version="1.0",
                beliefs=beliefs,
                goals=goals,
                constraints=[],
                alignment_score=0.5,  # Initial alignment score
                last_updated=datetime.utcnow().isoformat()
            )
            
            # Store model
            self._shared_mental_models[model_id] = model
            
            logger.info(f"[COORDINATION_LAYER] Shared mental model created: {model_id}")
            
            return model
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to create shared mental model: {e}")
            return SharedMentalModel(
                model_id=f"model_error_{int(datetime.utcnow().timestamp())}",
                model_type="error",
                beliefs={},
                goals=[],
                metadata={"error": str(e)}
            )
    
    def update_mental_model_alignment(
        self,
        model_id: str,
        agent_id: str,
        alignment_feedback: Dict[str, Any]
    ) -> bool:
        """Update alignment score for a shared mental model."""
        try:
            model = self._shared_mental_models.get(model_id)
            if not model:
                logger.warning(f"[COORDINATION_LAYER] Mental model {model_id} not found")
                return False
            
            # Update alignment score (simplified)
            alignment_delta = alignment_feedback.get("alignment_delta", 0.0)
            model.alignment_score = max(0.0, min(1.0, model.alignment_score + alignment_delta))
            model.last_updated = datetime.utcnow().isoformat()
            
            # Update metrics
            model_id_pair = f"{agent_id}_{model_id}"
            self._metrics.alignment_scores[model_id_pair] = model.alignment_score
            
            logger.info(f"[COORDINATION_LAYER] Mental model alignment updated: {model_id} (score: {model.alignment_score:.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"[COORDINATION_LAYER] Failed to update mental model alignment: {e}")
            return False
    
    def get_coordination_report(self) -> Dict[str, Any]:
        """Get comprehensive coordination report."""
        with self._lock:
            return {
                "agent_status": {
                    "registered_agents": len(self._registered_agents),
                    "agents": list(self._registered_agents.keys())
                },
                "communication_metrics": {
                    "messages_sent": self._metrics.messages_sent,
                    "messages_received": self._metrics.messages_received,
                    "pending_messages": len(self._message_queue)
                },
                "conflict_status": {
                    "conflicts_detected": self._metrics.conflicts_detected,
                    "conflicts_resolved": self._metrics.conflicts_resolved,
                    "resolution_success_rate": self._metrics.resolution_success_rate,
                    "active_conflicts": [
                        {
                            "conflict_id": conflict.conflict_id,
                            "type": conflict.conflict_type.value,
                            "agents": [conflict.agent_a_id, conflict.agent_b_id],
                            "status": conflict.status.value
                        }
                        for conflict in self._conflicts.values()
                        if conflict.status == CoordinationStatus.CONFLICT
                    ]
                },
                "knowledge_exchange_status": {
                    "total_exchanges": self._metrics.knowledge_exchanges,
                    "successful_shares": self._metrics.knowledge_shares_successful,
                    "pending_exchanges": [
                        exchange.exchange_id
                        for exchange in self._knowledge_exchanges.values()
                        if exchange.status == CoordinationStatus.PENDING
                    ]
                },
                "resource_allocation_status": {
                    "allocation_requests": self._metrics.allocation_requests,
                    "allocations_successful": self._metrics.allocations_successful
                },
                "governance_status": {
                    "active_policies": len(self._governance_policies),
                    "policies": [
                        {
                            "policy_id": policy.policy_id,
                            "name": policy.policy_name,
                            "type": policy.policy_type,
                            "active": policy.active
                        }
                        for policy in self._governance_policies.values()
                    ]
                },
                "mental_model_status": {
                    "total_models": len(self._shared_mental_models),
                    "models": [
                        {
                            "model_id": model.model_id,
                            "type": model.model_type,
                            "alignment_score": model.alignment_score,
                            "agents": len(model.agent_access)
                        }
                        for model in self._shared_mental_models.values()
                    ]
                },
                "coordination_components": {
                    "cognitive_economy": self._cognitive_economy is not None,
                    "operating_modes": self._operating_modes is not None,
                    "learning_gate": self._learning_gate is not None
                }
            }


__all__ = [
    "ConcreteCoordinationLayer",
]