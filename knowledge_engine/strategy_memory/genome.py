"""Strategy genome — genetic representation of evolved strategies.

Supports:
    - mutate: Parameter drift, atom substitution
    - combine: Crossover between successful strategies
    - evolve: Generational improvement
    - retire: Remove underperforming strategies
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass

from knowledge_engine.strategy_memory.store import StrategyMemory


@dataclass(frozen=True, slots=True)
class Gene:
    name: str
    value: float
    min_value: float
    max_value: float
    mutation_rate: float = 0.1

    def mutate(self, rng: random.Random | None = None) -> Gene:
        r = rng or random.Random()
        if r.random() < self.mutation_rate:
            delta = (self.max_value - self.min_value) * 0.1 * (r.random() - 0.5)
            new_value = max(self.min_value, min(self.max_value, self.value + delta))
            return Gene(name=self.name, value=new_value, min_value=self.min_value,
                       max_value=self.max_value, mutation_rate=self.mutation_rate)
        return self


@dataclass(frozen=True, slots=True)
class StrategyGenome:
    """Genome representation of a strategy.

    Can mutate, combine with other genomes, and evolve over generations.
    """

    genome_id: str
    strategy_id: str
    genes: tuple[Gene, ...] = ()
    atom_ids: tuple[str, ...] = ()
    fitness: float = 0.0
    generation: int = 0
    parent_ids: tuple[str, ...] = ()

    @property
    def gene_count(self) -> int:
        return len(self.genes)

    def get_gene(self, name: str) -> Gene | None:
        for g in self.genes:
            if g.name == name:
                return g
        return None

    def mutate(self, rng: random.Random | None = None) -> StrategyGenome:
        r = rng or random.Random()
        new_genes = tuple(g.mutate(r) for g in self.genes)
        return StrategyGenome(
            genome_id=uuid.uuid4().hex[:12],
            strategy_id=self.strategy_id,
            genes=new_genes,
            atom_ids=self.atom_ids,
            fitness=0.0,
            generation=self.generation + 1,
            parent_ids=(self.genome_id,),
        )

    def combine(self, other: StrategyGenome, rng: random.Random | None = None) -> StrategyGenome:
        r = rng or random.Random()
        gene_map = {g.name: g for g in other.genes}
        combined = []
        for g in self.genes:
            if r.random() < 0.5 and g.name in gene_map:
                combined.append(gene_map[g.name])
            else:
                combined.append(g)
        return StrategyGenome(
            genome_id=uuid.uuid4().hex[:12],
            strategy_id=f"{self.strategy_id}+{other.strategy_id}",
            genes=tuple(combined),
            atom_ids=(self.atom_ids[:len(self.atom_ids)//2] +
                     other.atom_ids[len(other.atom_ids)//2:]),
            fitness=0.0,
            generation=max(self.generation, other.generation) + 1,
            parent_ids=(self.genome_id, other.genome_id),
        )

    def to_memory(self) -> StrategyMemory:
        return StrategyMemory(
            strategy_id=self.strategy_id,
            genome_id=self.genome_id,
            name=f"genome_{self.genome_id[:8]}",
            confidence=min(1.0, self.fitness),
            performance_score=self.fitness,
            metadata={"generation": self.generation, "parents": list(self.parent_ids)},
        )


def evolve_genome(genome: StrategyGenome, population: list[StrategyGenome],
                  population_size: int, rng: random.Random | None = None) -> list[StrategyGenome]:
    """Evolve a genome through mutation and crossover with the population."""
    r = rng or random.Random()
    evolved = []

    top_performers = sorted(
        population, key=lambda g: g.fitness, reverse=True
    )[:population_size // 4]

    for _ in range(population_size // 4):
        evolved.append(genome.mutate(r))

    for i in range(len(top_performers)):
        for j in range(i + 1, len(top_performers)):
            if len(evolved) < population_size:
                evolved.append(top_performers[i].combine(top_performers[j], r))

    return evolved