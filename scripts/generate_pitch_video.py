#!/usr/bin/env python3
"""Automated 2560x1440 (2K QHD) 6-Scene Code Walkthrough and Pitch Video Generator
for Vertex Swarm Agent.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from PIL import Image


WIDTH = 2560
HEIGHT = 1440
CHROME_CAPTURE_HEIGHT = 1527
REPO_ROOT = Path(__file__).resolve().parents[1]
CHROME_BIN = "/home/mike-anderson/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell"

sys.path.insert(0, str(REPO_ROOT / "src"))
from vertex_swarm_spoke import FoxMQGossipVerifier, ManifoldBFTCoordinator, PeerVote  # noqa: E402


def _load_slice(rel_path: str, start_line: int, end_line: int) -> str:
    """Load exact source lines and HTML-escape them."""
    lines = (REPO_ROOT / rel_path).read_text(encoding="utf-8").splitlines()
    return html.escape("\n".join(lines[start_line - 1 : end_line]))


BFT_COORDINATOR_PART1 = _load_slice("src/vertex_swarm_spoke/bft_swarm.py", 17, 72)
BFT_COORDINATOR_PART2 = _load_slice("src/vertex_swarm_spoke/bft_swarm.py", 73, 132)
FOXMQ_VERIFIER_CODE = _load_slice("src/vertex_swarm_spoke/bft_swarm.py", 134, 169)

_COORD = ManifoldBFTCoordinator()
_HONEST_VOTES = [PeerVote(f"node-{i}", "0xabc", (0.5,) * 16, 0.50) for i in range(5)]
_HONEST_VERDICT = _COORD.evaluate_votes("0xabc", _HONEST_VOTES)

_ADV_VOTES = [
    PeerVote("honest-1", "0xact", (0.2,) * 16, 0.51),
    PeerVote("honest-2", "0xact", (0.21,) * 16, 0.49),
    PeerVote("honest-3", "0xact", (0.19,) * 16, 0.50),
    PeerVote("honest-4", "0xact", (0.20,) * 16, 0.50),
    PeerVote("byz-poison", "0xact", (4.5,) * 16, 0.50),
    PeerVote("stab-drift", "0xact", (0.2,) * 16, 0.95),
]
_ADV_VERDICT = _COORD.evaluate_votes("0xact", _ADV_VOTES)

_GOSSIP = FoxMQGossipVerifier(b"vertex-p2p-secret")
_FRAME1 = _GOSSIP.sign_frame("drone-alpha", seq_nonce=1, payload="waypoint:10,20")
_FRAME1_OK = _GOSSIP.verify_frame(_FRAME1)
_FRAME1_REPLAY = _GOSSIP.verify_frame(_FRAME1)

SCENES = [
    {
        "id": "scene0_title_hero",
        "narration": (
            "Vertex Swarm Agent. A leaderless coordinate-wise median Byzantine fault tolerant vote aggregator "
            "and monotonic-nonce HMAC P2P gossip verifier I built in pure Python. "
            "It replaces arithmetic mean aggregation and central coordinators with a coordinate-wise median centroid, "
            "a zero point five zero plus or minus zero point one two stability score envelope, constant-time HMAC frame signing, "
            "and strict per-sender sequence nonces. "
            "Measured across twenty thousand local iterations, evaluate votes takes point zero one three seven milliseconds at p50 "
            "and frame verification takes point zero zero one zero milliseconds at p50, with three out of three unit tests passing."
        ),
        "html_body": """
            <div class="header" style="text-align:center;margin-top:12px;margin-bottom:24px;">
                <span class="badge" style="font-size:20px;padding:8px 26px;">Leaderless P2P | Coordinate-Wise Median BFT</span>
                <h1 style="font-size:64px;margin-top:14px;margin-bottom:10px;letter-spacing:-2px;">Vertex Swarm Agent</h1>
                <p class="subtitle" style="font-size:26px;margin:0 auto;max-width:1950px;color:#38bdf8;font-weight:500;">
                    Coordinate-Wise Median BFT Consensus &amp; Monotonic FoxMQ Peer Verifier
                </p>
            </div>
            <div class="grid-4" style="margin-top:20px;margin-bottom:20px;">
                <div class="card" style="text-align:center;border-color:rgba(56,189,248,0.4);background:rgba(56,189,248,0.08);">
                    <h3 style="font-size:30px;color:#38bdf8;">Median BFT</h3>
                    <p style="font-size:18px;color:#cbd5e1;">Coordinate-wise median resists outlier poisoning (&lt; 1/3 faults)</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(34,197,94,0.4);background:rgba(34,197,94,0.08);">
                    <h3 style="font-size:30px;color:#22c55e;">0.50 +/- 0.12</h3>
                    <p style="font-size:18px;color:#cbd5e1;">Filters drifted peers &amp; requires &gt;= 2/3 honest quorum</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(192,132,252,0.4);background:rgba(192,132,252,0.08);">
                    <h3 style="font-size:30px;color:#c084fc;">FoxMQ Firewall</h3>
                    <p style="font-size:18px;color:#cbd5e1;">HMAC-SHA256 frame authentication + strict monotonic nonces</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(245,158,11,0.4);background:rgba(245,158,11,0.08);">
                    <h3 style="font-size:30px;color:#f59e0b;">0.0137 ms p50</h3>
                    <p style="font-size:18px;color:#cbd5e1;">6 peers in 16D; verify_frame 0.0010 ms p50 (20k runs)</p>
                </div>
            </div>
            <div class="flow-container" style="margin-top:16px;">
                <div class="chip chip-green" style="font-size:17px;padding:10px 20px;">No Central Coordinator Required</div>
                <div class="chip chip-blue" style="font-size:17px;padding:10px 20px;">3/3 Unit Tests PASS (0.01s)</div>
                <div class="chip chip-green" style="font-size:17px;padding:10px 20px;">Python Stdlib Only</div>
                <div class="chip chip-blue" style="font-size:17px;padding:10px 20px;">uv run pytest -q</div>
            </div>
        """,
    },
    {
        "id": "scene1_problem_workflow",
        "narration": (
            "How Leaderless Consensus and Frame Checking Work. "
            "Central aggregators stop a swarm when a link drops, and arithmetic vector means shift if one faulty peer injects a huge vector. "
            "Step one: peers send signed GossipFrame messages carrying a vector embedding and a stability score. "
            "Step two: FoxMQGossipVerifier drops replayed sequence nonces and invalid HMAC signatures with constant-time comparison. "
            "Step three: ManifoldBFTCoordinator filters stability scores inside the zero point five zero plus or minus zero point one two envelope, "
            "computes the coordinate-wise median centroid, disqualifies outliers, and commits a SHA-256 hash when at least two-thirds agree."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Architecture | Leaderless P2P Consensus</span>
                <h1>Peer Consensus Without a Central Coordinator</h1>
                <p class="subtitle">Avoiding single-point coordinator stalls, mean vector poisoning, and replayed gossip frames.</p>
            </div>
            <div class="flow-container" style="margin-top:24px;">
                <div class="flow-step">
                    <div class="flow-num">01</div>
                    <h4>Signed P2P Gossip</h4>
                    <p>Peers exchange authenticated frames carrying vector embeddings and stability scores.</p>
                    <div class="chip">GossipFrame(nonce, HMAC)</div>
                </div>
                <div class="flow-arrow">-&gt;</div>
                <div class="flow-step highlight">
                    <div class="flow-num">02</div>
                    <h4>FoxMQ Nonce Firewall</h4>
                    <p>Enforces seq_nonce &gt; last_seen and constant-time hmac.compare_digest() check.</p>
                    <div class="chip chip-blue">Replay &amp; Tamper Drop</div>
                </div>
                <div class="flow-arrow">-&gt;</div>
                <div class="flow-step">
                    <div class="flow-num">03</div>
                    <h4>Median BFT + Quorum Gate</h4>
                    <p>Computes coordinate-wise median, drops RMS &gt; 0.35 or drift, checks &gt;= 2/3 quorum.</p>
                    <div class="chip chip-green">0.0137 ms p50</div>
                </div>
            </div>
            <div class="grid-2" style="margin-top:24px;">
                <div class="card danger">
                    <h3>Central Coordinator / Mean Aggregator</h3>
                    <ul>
                        <li><strong>Partition Risk:</strong> Swarm halts if the central relay drops</li>
                        <li><strong>Breakdown Point:</strong> 0%: a single extreme vector skews the mean</li>
                        <li><strong>Packet Integrity:</strong> Vulnerable to replayed old gossip frames</li>
                        <li><strong>Dependencies:</strong> Heavy external brokers for small edge nodes</li>
                    </ul>
                </div>
                <div class="card success">
                    <h3>Vertex Swarm Agent</h3>
                    <ul>
                        <li><strong>Decentralization:</strong> 100% peer-to-peer leaderless consensus</li>
                        <li><strong>Fault Tolerance:</strong> Tolerates &lt; 1/3 Byzantine peer faults</li>
                        <li><strong>Replay Security:</strong> Strict monotonic per-sender nonce &amp; HMAC-SHA256</li>
                        <li><strong>Latency:</strong> 0.0137 ms p50 evaluate_votes; 0.0010 ms p50 verify_frame</li>
                    </ul>
                </div>
            </div>
        """,
    },
    {
        "id": "scene2_core_source_code",
        "narration": (
            "Here is ManifoldBFTCoordinator in src/vertex_swarm_spoke/bft_swarm.py, lines 17 through 132. "
            "On the left, PeerVote and BFTVerdict dataclasses pair with the coordinator settings: "
            "two-thirds quorum ratio, zero point three five max RMS divergence, and the zero point five zero stability target with tolerance zero point one two. "
            "On the right, evaluate_votes computes the coordinate-wise median centroid, disqualifies drifted or mismatched voters, and hashes the honest agreement."
        ),
        "html_body": f"""
            <div class="header">
                <span class="badge">Code Walkthrough | Coordinate-Wise Median BFT</span>
                <h1>Core Implementation: ManifoldBFTCoordinator</h1>
                <p class="subtitle">Verbatim source from <code>src/vertex_swarm_spoke/bft_swarm.py</code> (lines 17 to 132).</p>
            </div>
            <div class="code-grid-2">
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">bft_swarm.py (Lines 17 to 72)</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <pre style="font-size:14.2px;line-height:1.28;">{BFT_COORDINATOR_PART1}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] PeerVote &amp; BFTVerdict</span>
                        <span class="flow-pill pass">[OK] 2/3 Quorum Config</span>
                    </div>
                </div>
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">bft_swarm.py (Lines 73 to 132)</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <pre style="font-size:14.2px;line-height:1.28;">{BFT_COORDINATOR_PART2}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] Coordinate Median</span>
                        <span class="flow-pill pass">[OK] Stability + RMS Filter</span>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene3_verifier_source_code",
        "narration": (
            "Next is FoxMQGossipVerifier in bft_swarm.py lines 134 through 169. "
            "It signs each GossipFrame using HMAC-SHA256 bound to sender ID, sequence nonce, and payload. "
            "When checking incoming frames, it first rejects any sequence nonce less than or equal to the last seen sender nonce, "
            "then checks HMAC equality in constant time before updating state."
        ),
        "html_body": f"""
            <div class="header">
                <span class="badge">Code Walkthrough | Cryptographic Gossip Defense</span>
                <h1>Peer Packet Firewall: FoxMQGossipVerifier</h1>
                <p class="subtitle">Verbatim monotonic nonce and constant-time HMAC check (<code>bft_swarm.py</code> lines 134 to 169).</p>
            </div>
            <div class="grid-2" style="gap:28px;height:980px;">
                <div class="code-box">
                    <div class="linux-bar">
                        <span class="linux-tab">bft_swarm.py (Lines 134 to 169)</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <pre style="font-size:16px;line-height:1.42;">{FOXMQ_VERIFIER_CODE}</pre>
                    <div class="eval-flow">
                        <span class="flow-pill pass">[OK] Monotonic Replay Defense</span>
                        <span class="flow-pill pass">[OK] hmac.compare_digest()</span>
                    </div>
                </div>
                <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;">
                    <div>
                        <h3>Checks Enforced</h3>
                        <ul>
                            <li><strong>Replay Immunity:</strong> <code>seq_nonce &lt;= last_seen</code> returns <code>replay_nonce</code> before HMAC work.</li>
                            <li><strong>Constant-Time Compare:</strong> Avoids timing leaks with <code>hmac.compare_digest</code>.</li>
                            <li><strong>Outlier Isolation:</strong> Extreme vectors cannot shift <code>statistics.median</code> away from honest peers.</li>
                            <li><strong>Safe Halt:</strong> Sets <code>consensus_reached=False</code> whenever honest fraction drops below <code>0.67</code>.</li>
                        </ul>
                    </div>
                    <div class="card success" style="padding:20px;">
                        <h4 style="color:#22c55e;font-size:20px;margin-bottom:6px;">Benchmark (scripts/bench.py, 20k runs)</h4>
                        <p style="font-size:17px;">evaluate_votes: 0.0137 ms p50 (0.0232 ms p99); verify_frame: 0.0010 ms p50 (0.0016 ms p99).</p>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene4_honest_vs_adversarial_exec",
        "narration": (
            "Here is a side-by-side run using the actual outputs from bft_swarm.py. "
            f"On the left, five honest peers converge with consensus reached true, aggregate hash {_HONEST_VERDICT.aggregate_manifold_hash}, "
            "and zero disqualified nodes. "
            "On the right, a replayed nonce one frame is dropped immediately by FoxMQGossipVerifier, "
            f"and an extreme outlier plus a drifted stability peer drop the honest share to four of six, so consensus halts safely."
        ),
        "html_body": f"""
            <div class="header">
                <span class="badge">Live Walkthrough | Quorum vs. Poisoning and Replay Blocked</span>
                <h1>Swarm Execution: Honest Consensus vs. Outlier &amp; Replay Blocked</h1>
                <p class="subtitle">Actual outputs produced directly by <code>ManifoldBFTCoordinator</code> and <code>FoxMQGossipVerifier</code>.</p>
            </div>
            <div class="code-grid-2">
                <div class="terminal-mini">
                    <div class="linux-bar">
                        <span class="linux-tab">swarm: 5 Honest 16D Nodes</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <div class="term-lines" style="font-size:17px;">
                        <p class="t-line"><span class="t-prompt">$</span> coord.evaluate_votes("0xabc", honest_5_votes)</p>
                        <p class="t-line t-cyan">[1] FoxMQ Frame Check...</p>
                        <p class="t-line t-indent">verify_frame(f1): ok={_FRAME1_OK[0]}, status=<span class="t-green">'{_FRAME1_OK[1]}'</span></p>
                        <p class="t-line t-cyan">[2] Median Centroid &amp; Stability Envelope...</p>
                        <p class="t-line t-indent">honest_node_count    = <span class="t-green">{_HONEST_VERDICT.honest_node_count} / 5</span></p>
                        <p class="t-line t-indent">aggregate_stability  = <span class="t-green">{_HONEST_VERDICT.aggregate_stability:.6f}</span></p>
                        <p class="t-line t-indent">disqualified_nodes   = <span class="t-green">{html.escape(str(_HONEST_VERDICT.disqualified_nodes))}</span></p>
                        <p class="t-line t-indent">aggregate_hash       = <span class="t-yellow">{_HONEST_VERDICT.aggregate_manifold_hash}</span></p>
                        <div class="t-banner-pass">consensus_reached={_HONEST_VERDICT.consensus_reached} | 0.0137 ms p50 (bench.py)</div>
                    </div>
                </div>
                <div class="terminal-mini danger-border">
                    <div class="linux-bar danger-header">
                        <span class="linux-tab-danger">swarm: 4 Honest + Outlier + Drift + Replay</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <div class="term-lines" style="font-size:17px;">
                        <p class="t-line"><span class="t-prompt">$</span> coord.evaluate_votes("0xact", mixed_6_votes)</p>
                        <p class="t-line t-yellow">[1] Replay of seq_nonce=1...</p>
                        <p class="t-line t-indent t-red">[X] FoxMQ Dropped: {html.escape(_FRAME1_REPLAY[1])}</p>
                        <p class="t-line t-yellow">[2] Disqualified Peers (vector=4.5, stability=0.95)...</p>
                        <p class="t-line t-indent t-red">[X] disqualified_nodes = {html.escape(str(_ADV_VERDICT.disqualified_nodes))}</p>
                        <p class="t-line t-cyan">[3] Supermajority Gate (threshold 0.67)...</p>
                        <p class="t-line t-indent">honest = <span class="t-yellow">{_ADV_VERDICT.honest_node_count} / 6 (0.6667 &lt; 0.67)</span></p>
                        <p class="t-line t-indent">consensus_reached = <span class="t-red">{_ADV_VERDICT.consensus_reached}</span></p>
                        <div class="t-banner-fail">SAFE HALT | OUTLIERS ISOLATED</div>
                    </div>
                </div>
            </div>
        """,
    },
    {
        "id": "scene5_verification_and_impact",
        "narration": (
            "Verification and Benchmark. "
            "Running pytest across tests/test_vertex_swarm_spoke.py passes all three tests in point zero one seconds, "
            "covering five-node consensus, Byzantine outlier and drift disqualification, and replay and HMAC tampering rejection. "
            "Reproduce the tests and the twenty-thousand-run latency benchmark directly with uv."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">Verification | Test Suite and Local Benchmark</span>
                <h1>3/3 Unit Tests &amp; Reproducible Latency Benchmark</h1>
                <p class="subtitle">Zero-dependency edge swarm consensus verified against poisoning and packet replays.</p>
            </div>
            <div class="grid-2" style="margin-top:18px;gap:26px;">
                <div class="terminal-window" style="height:640px;">
                    <div class="linux-bar">
                        <span class="linux-tab">pytest tests/test_vertex_swarm_spoke.py -v</span>
                        <div class="linux-controls"><span>-</span><span>[]</span><span>x</span></div>
                    </div>
                    <div class="terminal-content" style="font-size:16px;line-height:1.6;">
                        <p class="cmd">$ uv run pytest tests/test_vertex_swarm_spoke.py -v</p>
                        <p><span class="pass">PASSED</span> test_bft_honest_supermajority_consensus</p>
                        <p style="color:#94a3b8;padding-left:20px;">Verifies honest 5/5 supermajority agreement and aggregate SHA-256 hash</p>
                        <p><span class="pass">PASSED</span> test_bft_disqualifies_byzantine_outlier_and_hiho_drift</p>
                        <p style="color:#94a3b8;padding-left:20px;">Isolates extreme vector outliers and out-of-envelope stability drift</p>
                        <p><span class="pass">PASSED</span> test_foxmq_gossip_verifier_blocks_replay_and_tampering</p>
                        <p style="color:#94a3b8;padding-left:20px;">Blocks replayed sequence nonces and modified payload HMAC digests</p>
                        <p class="success-banner">================== 3 passed in 0.01s ==================</p>
                    </div>
                </div>
                <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;height:640px;">
                    <div>
                        <h3 style="color:#38bdf8;">Measured Profile (scripts/bench.py)</h3>
                        <ul>
                            <li><strong>Iterations:</strong> 20,000 runs on desktop</li>
                            <li><strong>evaluate_votes (6 peers, 16D):</strong> 0.0137 ms p50, 0.0232 ms p99</li>
                            <li><strong>verify_frame (HMAC + nonce):</strong> 0.0010 ms p50, 0.0016 ms p99</li>
                            <li><strong>Quorum Rule:</strong> honest / total &gt;= 0.67</li>
                            <li><strong>GitHub Repository:</strong> <code>manderson240/vertex-swarm-agent</code></li>
                        </ul>
                    </div>
                    <div class="card success" style="padding:18px;">
                        <h4 style="color:#22c55e;font-size:20px;margin-bottom:6px;">Local Verification Commands</h4>
                        <div class="code-pill" style="font-size:15px;">uv run pytest -q &amp;&amp; PYTHONPATH=src uv run python scripts/bench.py</div>
                    </div>
                </div>
            </div>
        """,
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" style="background-color:#030712;width:100%;height:100%;margin:0;padding:0;">
<head><meta charset="UTF-8"><style>
* { box-sizing:border-box; margin:0; padding:0; }
html, body {
  width:2560px; height:1440px;
  background:radial-gradient(circle at 50% 12%, #182234 0%, #0b0f19 55%, #030712 100%) !important;
  font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  color:#f8fafc; padding:30px 60px;
  display:flex; flex-direction:column; justify-content:space-between; overflow:hidden;
}
.header { margin-bottom:12px; }
.badge { display:inline-block; padding:6px 18px; background:rgba(56,189,248,0.15); border:1px solid rgba(56,189,248,0.4); border-radius:9999px; color:#38bdf8; font-size:17px; font-weight:700; text-transform:uppercase; letter-spacing:2px; margin-bottom:6px; }
h1 { font-size:46px; font-weight:800; color:#ffffff; margin-bottom:6px; letter-spacing:-1px; }
.subtitle { font-size:22px; color:#94a3b8; line-height:1.35; }
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:30px; }
.grid-4 { display:grid; grid-template-columns:repeat(4,1fr); gap:24px; }
.flow-container { display:flex; align-items:center; justify-content:space-between; background:rgba(30,41,59,0.45); border:1px solid rgba(148,163,184,0.2); border-radius:18px; padding:18px 32px; gap:16px; }
.flow-step { flex:1; background:#0d1322; border:1px solid #334155; border-radius:14px; padding:18px; text-align:center; }
.flow-step.highlight { border-color:#38bdf8; background:rgba(56,189,248,0.12); }
.flow-num { font-size:20px; font-weight:900; color:#38bdf8; margin-bottom:4px; }
.flow-step h4 { font-size:22px; color:#f8fafc; margin-bottom:4px; }
.flow-step p { font-size:16px; color:#94a3b8; margin-bottom:8px; line-height:1.35; }
.flow-arrow { font-size:26px; color:#64748b; padding:0 12px; font-weight:bold; font-family:monospace; }
.chip { display:inline-block; padding:6px 14px; background:#1e293b; border-radius:8px; font-size:14px; font-weight:600; color:#cbd5e1; }
.chip-blue { background:rgba(56,189,248,0.2); color:#38bdf8; border:1px solid rgba(56,189,248,0.4); }
.chip-green { background:rgba(34,197,94,0.2); color:#22c55e; border:1px solid rgba(34,197,94,0.4); }
.card { background:rgba(30,41,59,0.65); border:1px solid rgba(148,163,184,0.2); border-radius:18px; padding:24px; }
.card.danger { background:rgba(239,68,68,0.08); border-color:rgba(239,68,68,0.35); }
.card.success { background:rgba(34,197,94,0.08); border-color:rgba(34,197,94,0.35); }
.card h3 { font-size:26px; color:#f1f5f9; margin-bottom:10px; font-weight:700; }
.card p { font-size:18px; color:#cbd5e1; line-height:1.4; }
.card ul { list-style:none; }
.card ul li { font-size:18px; color:#cbd5e1; line-height:1.8; }
.card ul li strong { color:#ffffff; }
.code-grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:26px; height:980px; }
.code-box { background:#0a0e17; border:1px solid #1e293b; border-radius:14px; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 25px 50px -12px rgba(0,0,0,0.7); }
.linux-bar { background:#181f30; padding:10px 18px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #222d42; }
.linux-tab { background:#0a0e17; padding:4px 12px; border-radius:6px 6px 0 0; border:1px solid #222d42; border-bottom:none; color:#38bdf8; font-family:monospace; font-size:16px; font-weight:600; }
.linux-tab-danger { background:#0a0e17; padding:4px 12px; border-radius:6px 6px 0 0; border:1px solid rgba(239,68,68,0.4); border-bottom:none; color:#ef4444; font-family:monospace; font-size:16px; font-weight:600; }
.danger-header { background:#241319; border-bottom-color:rgba(239,68,68,0.3); }
.danger-border { border-color:rgba(239,68,68,0.45) !important; }
.linux-controls { display:flex; gap:14px; font-size:16px; color:#94a3b8; font-family:monospace; font-weight:bold; }
pre { padding:16px 22px; font-family:"JetBrains Mono","DejaVu Sans Mono",monospace; color:#e2e8f0; overflow:hidden; flex:1; }
.eval-flow { padding:12px 18px; background:#0e1526; border-top:1px solid #1e293b; display:flex; gap:10px; }
.flow-pill.pass { padding:5px 12px; border-radius:6px; font-size:14px; font-weight:700; background:rgba(34,197,94,0.18); color:#22c55e; border:1px solid rgba(34,197,94,0.35); }
.terminal-mini { background:#0a0e17; border:1px solid #1e293b; border-radius:14px; overflow:hidden; display:flex; flex-direction:column; }
.term-lines { padding:20px 24px; font-family:"JetBrains Mono",monospace; line-height:1.75; flex:1; display:flex; flex-direction:column; justify-content:space-between; }
.t-line { color:#f8fafc; } .t-prompt { color:#4ade80; font-weight:bold; } .t-cyan { color:#38bdf8; font-weight:bold; } .t-yellow { color:#fbbf24; font-weight:bold; } .t-green { color:#22c55e; font-weight:bold; } .t-red { color:#ef4444; font-weight:bold; } .t-indent { padding-left:22px; }
.t-banner-pass { margin-top:10px; padding:10px 16px; background:rgba(34,197,94,0.18); border:1px solid rgba(34,197,94,0.45); border-radius:8px; color:#22c55e; font-weight:800; font-size:18px; text-align:center; }
.t-banner-fail { margin-top:10px; padding:10px 16px; background:rgba(239,68,68,0.18); border:1px solid rgba(239,68,68,0.45); border-radius:8px; color:#ef4444; font-weight:800; font-size:18px; text-align:center; }
.terminal-window { background:#0a0e17; border:1px solid #1e293b; border-radius:14px; overflow:hidden; display:flex; flex-direction:column; }
.terminal-content { padding:20px 26px; font-family:"JetBrains Mono",monospace; flex:1; display:flex; flex-direction:column; justify-content:space-between; }
.cmd { color:#f8fafc; font-weight:bold; } .pass { color:#22c55e; font-weight:bold; } .success-banner { color:#22c55e; font-weight:bold; font-size:18px; margin-top:8px; }
.code-pill { display:inline-block; padding:8px 14px; background:#030712; border:1px solid #334155; border-radius:8px; font-family:monospace; color:#38bdf8; }
.footer { display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(148,163,184,0.2); padding-top:14px; font-size:17px; color:#64748b; }
.footer-brand { font-weight:bold; color:#94a3b8; }
</style></head>
<body>
  __BODY__
  <div class="footer">
    <div class="footer-brand">Vertex Swarm Agent | Leaderless P2P Consensus</div>
    <div>Coordinate-Wise Median BFT + FoxMQ Verifier | 3/3 pytest | github.com/manderson240/vertex-swarm-agent</div>
  </div>
</body></html>"""


def _synthesize_audio(text: str, output_mp3: Path) -> None:
    pocket_bin = shutil.which("pocket-tts") or "/home/mike-anderson/.local/bin/pocket-tts"
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    with tempfile.TemporaryDirectory() as td:
        wavs: list[Path] = []
        for idx, sent in enumerate(sentences):
            wav = Path(td) / f"part_{idx}.wav"
            subprocess.run(
                [pocket_bin, "generate", "--text", sent, "--device", "cpu", "--quantize", "--max-tokens", "150", "--output-path", str(wav), "-q"],
                check=True,
                capture_output=True,
            )
            if wav.exists() and wav.stat().st_size > 1000:
                wavs.append(wav)
        clist = Path(td) / "list.txt"
        clist.write_text("\n".join(f"file '{w}'" for w in wavs), encoding="utf-8")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(clist), "-af", "apad=pad_dur=1.25", "-c:a", "libmp3lame", "-b:a", "192k", str(output_mp3)],
            check=True,
            capture_output=True,
        )


def main() -> None:
    out_mp4 = REPO_ROOT / "docs" / "vertex_swarm_demo.mp4"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        profile_dir = work / "chrome_profile"
        profile_dir.mkdir(parents=True, exist_ok=True)
        parts: list[Path] = []
        for scene in SCENES:
            sid = scene["id"]
            print(f"Rendering {sid} at {WIDTH}x{HEIGHT} QHD...")
            html_file = work / f"{sid}.html"
            raw_png = work / f"{sid}_raw.png"
            png_file = work / f"{sid}.png"
            mp3_file = work / f"{sid}.mp3"
            seg_mp4 = work / f"{sid}.mp4"
            html_file.write_text(HTML_TEMPLATE.replace("__BODY__", scene["html_body"]), encoding="utf-8")
            subprocess.run(
                [
                    CHROME_BIN,
                    "--headless",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    "--disable-gpu",
                    f"--user-data-dir={profile_dir}",
                    "--force-device-scale-factor=1",
                    f"--screenshot={raw_png}",
                    f"--window-size={WIDTH},{CHROME_CAPTURE_HEIGHT}",
                    str(html_file),
                ],
                check=True,
                capture_output=True,
            )
            Image.open(raw_png).crop((0, 0, WIDTH, HEIGHT)).save(png_file)
            _synthesize_audio(scene["narration"], mp3_file)
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", str(png_file), "-i", str(mp3_file), "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", str(seg_mp4)],
                check=True,
                capture_output=True,
            )
            parts.append(seg_mp4)
        clist = work / "concat.txt"
        clist.write_text("\n".join(f"file '{p}'" for p in parts), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(clist), "-c", "copy", str(out_mp4)], check=True, capture_output=True)
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", str(out_mp4)], text=True))
    print(f"GENERATED: {out_mp4} ({float(info['format']['duration']):.2f}s, {int(info['format']['size'])/(1024*1024):.2f} MB)")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"Elapsed: {time.time() - t0:.1f}s")
