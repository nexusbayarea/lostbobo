# System Architecture: Entity Graph Core

## Overview
As of May 2026, the Entity Graph has been promoted to a **first-class runtime primitive** (previously plugin-specific under GraphRAG). It is now fully integrated with the State Registry, Temporal Engine, and Event Fabric.

## Key Components

### 1. Schema (`backend/core/runtime/entity_graph/schema.py`)
- **`EntityNode`**: Core runtime entity, linked to `WorldState.entities`.
- **`RelationshipEdge`**: Probabilistic, temporally decaying relationship between entities (using half-life decay).
- **`StateMutation`**: Atomic graph mutation tied to a `SimHPCEvent`.

### 2. EntityGraphService (`backend/core/runtime/entity_graph/service.py`)
- **`mutate(mutation: StateMutation, event: SimHPCEvent)`**: Kernel-mediated, temporally-aware graph mutation. Plugins must route all mutations through this service.
- **`traverse(...)`**: BFS-based traversal with probabilistic weighting and temporal decay.
- **Integration**: All mutations are linked back to `StateRegistryService`, triggering temporal propagation.

### 3. Core Integration
- **Temporal Engine**: Every edge now decays via `TemporalEngine.propagate()` (weight and uncertainty).
- **State Registry**: WorldState entities link bidirectionally to graph nodes via `state_key`.
- **Event Fabric**: Mutations are event-driven and logged via the system's event fabric.
- **Kernel Commands**: All graph mutations are processed via the `ENTITY_GRAPH_MUTATE` command handler registered on the Kernel Command Bus.

## Migration & Plugins
- Plugins (e.g., `graphrag`) are no longer permitted to perform direct Supabase writes. They must use the `EntityGraphService.mutate()` interface.
- Database schema and core indexes for runtime performance are managed via `deploy/supabase/migrations/20260508_entity_graph_core.sql`.
