"""DIX v42.2 — training harness for lightweight RL components.

Exercises:
  * ``intelligence_engine.learning.lightweight_rl.TradingEnv``
  * ``intelligence_engine.learning.lightweight_rl.PlaybookTrainer``

Usage:
    python scripts/train_rl.py [--episodes 128] [--window 32] [--seed 42]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))


def run(episodes: int = 64, window: int = 32, seed: int = 42) -> dict:
    from intelligence_engine.learning.lightweight_rl import PlaybookTrainer, TradingEnv

    env = TradingEnv(window=window, seed=seed)
    # Seed a few prices so the environment has history.
    base = 100.0
    for i in range(window):
        env.seed_price(base + (i % 5) * 0.1)

    trainer = PlaybookTrainer(env, episodes=episodes)
    result = trainer.train()
    return {
        "episodes": episodes,
        "window": window,
        "seed": seed,
        "avg_score": round(result.get("avg_score", 0.0), 6),
        "q_table_size": len(trainer._q),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Lightweight RL training harness")
    parser.add_argument("--episodes", type=int, default=64)
    parser.add_argument("--window", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    metrics = run(episodes=args.episodes, window=args.window, seed=args.seed)
    print(metrics)


if __name__ == "__main__":
    main()
