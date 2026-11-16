"""Unit tests for leaderless BFT manifold consensus and FoxMQ P2P replay defense."""

from __future__ import annotations

from dataclasses import replace

from vertex_swarm_spoke import FoxMQGossipVerifier, ManifoldBFTCoordinator, PeerVote


def test_bft_honest_supermajority_consensus() -> None:
    """Honest peer supermajority converges around 0.50 HIHO stability target."""
    coord = ManifoldBFTCoordinator()
    votes = [
        PeerVote(node_id=f"node-{i}", action_hash="0xabc", manifold_vector=(0.5,) * 16, stability_score=0.50)
        for i in range(5)
    ]
    verdict = coord.evaluate_votes("0xabc", votes)
    assert verdict.consensus_reached is True
    assert verdict.honest_node_count == 5
    assert verdict.byzantine_node_count == 0
    assert verdict.disqualified_nodes == ()
    assert len(verdict.aggregate_manifold_hash) == 16


def test_bft_disqualifies_byzantine_outlier_and_hiho_drift() -> None:
    """Byzantine divergence >0.35 or HIHO instability fails quorum disqualification."""
    coord = ManifoldBFTCoordinator()
    votes = [
        PeerVote("honest-1", "0xact", (0.2,) * 16, stability_score=0.51),
        PeerVote("honest-2", "0xact", (0.21,) * 16, stability_score=0.49),
        PeerVote("honest-3", "0xact", (0.19,) * 16, stability_score=0.50),
        PeerVote("honest-4", "0xact", (0.20,) * 16, stability_score=0.50),
        PeerVote("byz-poison", "0xact", (4.5,) * 16, stability_score=0.50),
        PeerVote("hiho-drift", "0xact", (0.2,) * 16, stability_score=0.95),
    ]
    verdict = coord.evaluate_votes("0xact", votes)
    assert verdict.consensus_reached is False  # 4/6 = 0.6667 < 0.67
    assert verdict.honest_node_count == 4
    assert set(verdict.disqualified_nodes) == {"byz-poison", "hiho-drift"}

    # With 5 honest and 1 Byzantine (5/6 = 0.833 >= 0.67), supermajority holds cleanly
    verdict_ok = coord.evaluate_votes("0xact", [*votes[:4], PeerVote("honest-5", "0xact", (0.20,) * 16, 0.50), votes[4]])
    assert verdict_ok.consensus_reached is True
    assert verdict_ok.disqualified_nodes == ("byz-poison",)


def test_foxmq_gossip_verifier_blocks_replay_and_tampering() -> None:
    """FoxMQ verifier accepts sequential signed frames and rejects replays or bad HMACs."""
    verifier = FoxMQGossipVerifier(b"vertex-p2p-secret")
    f1 = verifier.sign_frame("drone-alpha", seq_nonce=1, payload="waypoint:10,20")
    f2 = verifier.sign_frame("drone-alpha", seq_nonce=2, payload="waypoint:15,25")

    ok1, msg1 = verifier.verify_frame(f1)
    assert ok1 is True and msg1 == "ok"

    # Replay of sequence nonce 1 rejected
    ok_replay, msg_replay = verifier.verify_frame(f1)
    assert ok_replay is False and "replay_nonce" in msg_replay

    # Tampered payload rejected
    tampered = replace(f2, payload="waypoint:999,999")
    ok_tamper, msg_tamper = verifier.verify_frame(tampered)
    assert ok_tamper is False and msg_tamper == "invalid_hmac_signature"

    # Original valid frame 2 still succeeds because failed frames never bump nonce watermark
    ok2, msg2 = verifier.verify_frame(f2)
    assert ok2 is True and msg2 == "ok"
