"""Byzantine Fault Tolerant Manifold Consensus & Deterministic P2P FoxMQ Verifier.

Provides coordinate-wise median BFT consensus over 256D semantic vectors and
cryptographic monotonic-nonce gossip frame verification for leaderless P2P swarms.
"""

from __future__ import annotations

import hashlib
import hmac
import math
import statistics
import time
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PeerVote:
    """Individual autonomous peer node vote on a shared swarm action."""

    node_id: str
    action_hash: str
    manifold_vector: tuple[float, ...]
    stability_score: float = 0.50
    timestamp_ns: int = field(default_factory=time.time_ns)


@dataclass(frozen=True, slots=True)
class BFTVerdict:
    """Consensus certification across peer nodes with Byzantine disqualifications."""

    action_hash: str
    consensus_reached: bool
    honest_node_count: int
    byzantine_node_count: int
    aggregate_manifold_hash: str
    aggregate_stability: float
    disqualified_nodes: tuple[str, ...]
    latency_ms: float


class ManifoldBFTCoordinator:
    """Coordinate-wise median BFT consensus resilient up to < 1/3 Byzantine nodes."""

    def __init__(
        self,
        *,
        bft_threshold_ratio: float = 0.67,
        max_manifold_divergence: float = 0.35,
        hiho_target: float = 0.50,
        hiho_tolerance: float = 0.12,
    ) -> None:
        self.bft_threshold_ratio = bft_threshold_ratio
        self.max_manifold_divergence = max_manifold_divergence
        self.hiho_target = hiho_target
        self.hiho_tolerance = hiho_tolerance

    def evaluate_votes(self, action_hash: str, votes: list[PeerVote]) -> BFTVerdict:
        """Evaluate peer votes via HIHO quadrature and coordinate-wise median BFT filtering."""
        t0 = time.perf_counter()
        if not votes:
            return BFTVerdict(
                action_hash=action_hash,
                consensus_reached=False,
                honest_node_count=0,
                byzantine_node_count=0,
                aggregate_manifold_hash="",
                aggregate_stability=0.0,
                disqualified_nodes=(),
                latency_ms=0.0,
            )

        vector_dim = len(votes[0].manifold_vector)
        if vector_dim == 0 or any(len(v.manifold_vector) != vector_dim for v in votes):
            dt_ms = (time.perf_counter() - t0) * 1000.0
            return BFTVerdict(
                action_hash=action_hash,
                consensus_reached=False,
                honest_node_count=0,
                byzantine_node_count=len(votes),
                aggregate_manifold_hash="",
                aggregate_stability=0.0,
                disqualified_nodes=tuple(v.node_id for v in votes),
                latency_ms=round(dt_ms, 4),
            )

        hiho_candidates = [
            v for v in votes if abs(v.stability_score - self.hiho_target) <= self.hiho_tolerance
        ]
        ref_votes = hiho_candidates or votes
        centroid = [
            float(statistics.median(v.manifold_vector[i] for v in ref_votes))
            for i in range(vector_dim)
        ]

        honest: list[PeerVote] = []
        disqualified: list[str] = []
        for vote in votes:
            sq_sum = sum((a - b) ** 2 for a, b in zip(vote.manifold_vector, centroid, strict=True))
            rms_dist = math.sqrt(sq_sum / vector_dim)
            hiho_drift = abs(vote.stability_score - self.hiho_target)
            if (
                vote.action_hash != action_hash
                or rms_dist > self.max_manifold_divergence
                or hiho_drift > self.hiho_tolerance
            ):
                disqualified.append(vote.node_id)
            else:
                honest.append(vote)

        honest_count = len(honest)
        consensus = (honest_count / len(votes)) >= self.bft_threshold_ratio
        if honest:
            agg_stab = sum(v.stability_score for v in honest) / honest_count
            raw = "|".join(sorted(f"{v.node_id}:{v.action_hash}" for v in honest))
            agg_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        else:
            agg_stab = 0.0
            agg_hash = ""

        dt_ms = (time.perf_counter() - t0) * 1000.0
        return BFTVerdict(
            action_hash=action_hash,
            consensus_reached=consensus,
            honest_node_count=honest_count,
            byzantine_node_count=len(disqualified),
            aggregate_manifold_hash=agg_hash,
            aggregate_stability=round(agg_stab, 6),
            disqualified_nodes=tuple(disqualified),
            latency_ms=round(dt_ms, 4),
        )


@dataclass(frozen=True, slots=True)
class GossipFrame:
    """Authenticated P2P gossip frame exchanged over FoxMQ / libp2p."""

    sender_id: str
    seq_nonce: int
    payload: str
    hmac_hex: str


class FoxMQGossipVerifier:
    """Monotonic-nonce & HMAC-SHA256 P2P gossip verifier blocking replay/tampering."""

    def __init__(self, shared_secret: bytes) -> None:
        self._secret = shared_secret
        self._last_nonce_by_sender: dict[str, int] = {}

    def sign_frame(self, sender_id: str, seq_nonce: int, payload: str) -> GossipFrame:
        """Create a signed P2P gossip frame."""
        msg = f"{sender_id}:{seq_nonce}:{payload}".encode("utf-8")
        digest = hmac.new(self._secret, msg, hashlib.sha256).hexdigest()
        return GossipFrame(sender_id=sender_id, seq_nonce=seq_nonce, payload=payload, hmac_hex=digest)

    def verify_frame(self, frame: GossipFrame) -> tuple[bool, str]:
        """Verify frame HMAC integrity and strict monotonic sequence ordering."""
        last_seen = self._last_nonce_by_sender.get(frame.sender_id, 0)
        if frame.seq_nonce <= last_seen:
            return False, f"replay_nonce:{frame.seq_nonce}<={last_seen}"

        expected_msg = f"{frame.sender_id}:{frame.seq_nonce}:{frame.payload}".encode("utf-8")
        expected_hmac = hmac.new(self._secret, expected_msg, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected_hmac, frame.hmac_hex):
            return False, "invalid_hmac_signature"

        self._last_nonce_by_sender[frame.sender_id] = frame.seq_nonce
        return True, "ok"
