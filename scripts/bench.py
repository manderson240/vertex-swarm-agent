"""Measure evaluate_votes and verify_frame latency.

Run with: PYTHONPATH=src uv run python scripts/bench.py
"""

from __future__ import annotations

import statistics
import time

from vertex_swarm_spoke import FoxMQGossipVerifier, ManifoldBFTCoordinator, PeerVote


def _time(fn, runs: int) -> list[float]:
    out = []
    for _ in range(runs):
        t0 = time.perf_counter()
        fn()
        out.append((time.perf_counter() - t0) * 1000.0)
    out.sort()
    return out


def main(runs: int = 20000) -> None:
    coord = ManifoldBFTCoordinator()
    votes = [PeerVote(f"node-{i}", "0xact", (0.2,) * 16, 0.50) for i in range(5)]
    votes.append(PeerVote("byz", "0xact", (4.5,) * 16, 0.50))
    bft = _time(lambda: coord.evaluate_votes("0xact", votes), runs)

    verifier = FoxMQGossipVerifier(b"bench-secret")
    frames = [verifier.sign_frame("peer", i + 1, "payload") for i in range(runs)]
    it = iter(frames)
    gossip = _time(lambda: verifier.verify_frame(next(it)), runs)

    print(f"runs={runs}")
    print(f"evaluate_votes_6_peers_16d p50_ms={statistics.median(bft):.4f} p99_ms={bft[int(runs * 0.99)]:.4f}")
    print(f"verify_frame p50_ms={statistics.median(gossip):.4f} p99_ms={gossip[int(runs * 0.99)]:.4f}")


if __name__ == "__main__":
    main()
