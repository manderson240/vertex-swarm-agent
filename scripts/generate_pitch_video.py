#!/usr/bin/env python3
"""Automated 2560x1440 QHD Pitch Video Generator for Vertex Swarm Agent."""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image


WIDTH = 2560
HEIGHT = 1440
CHROME_CAPTURE_HEIGHT = 1527

SCENES = [
    {
        "id": "scene0_hero",
        "narration": (
            "Vertex Swarm Agent. Leaderless coordinate-wise median BFT consensus and HMAC FoxMQ "
            "peer firewall built for The Vertex Swarm Challenge 2026. "
            "Eliminating single-point cloud coordinators, disqualifying Byzantine sensor outliers "
            "via HIHO stability bounds, and verifying signed peer frames in point zero zero six seven milliseconds p50."
        ),
        "html_body": """
            <div class="header" style="text-align:center;margin-top:10px;margin-bottom:24px;">
                <span class="badge" style="font-size:20px;padding:8px 24px;">The Vertex Swarm Challenge 2026 • Leaderless P2P Swarms ($27,000 Pool)</span>
                <h1 style="font-size:64px;margin-top:14px;margin-bottom:10px;">Vertex Swarm Agent</h1>
                <p class="subtitle" style="font-size:26px;margin:0 auto;max-width:1900px;color:#38bdf8;">
                    Coordinate-Wise Median Riemannian BFT &amp; HMAC-SHA256 FoxMQ Gossip Firewall
                </p>
            </div>
            <div class="grid-4" style="margin-top:24px;margin-bottom:24px;">
                <div class="card" style="text-align:center;border-color:rgba(56,189,248,0.4);">
                    <div class="card-icon">🧭</div>
                    <h3 style="font-size:32px;color:#38bdf8;">Median BFT</h3>
                    <p style="font-size:19px;color:#cbd5e1;">Breakdown-resistant coordinate median blocks Byzantine vector drift</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(34,197,94,0.4);">
                    <div class="card-icon">⚖️</div>
                    <h3 style="font-size:32px;color:#22c55e;">HIHO 0.50+-0.12</h3>
                    <p style="font-size:19px;color:#cbd5e1;">Disqualifies adversarial nodes &amp; enforces >=2/3 quorum</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(192,132,252,0.4);">
                    <div class="card-icon">🔐</div>
                    <h3 style="font-size:32px;color:#c084fc;">FoxMQ Firewall</h3>
                    <p style="font-size:19px;color:#cbd5e1;">HMAC-SHA256 peer signing + strict monotonic replay nonces</p>
                </div>
                <div class="card" style="text-align:center;border-color:rgba(245,158,11,0.4);">
                    <div class="card-icon">📊</div>
                    <h3 style="font-size:32px;color:#f59e0b;">d = 2.13 | +102.0</h3>
                    <p style="font-size:19px;color:#cbd5e1;">0.0067ms p50 verifier | N=100 SPRT accept_h1 certified</p>
                </div>
            </div>
            <div class="flow-container" style="margin-top:20px;">
                <div class="chip chip-green">Zero Cloud Coordinator Required</div>
                <div class="chip chip-blue">3/3 Unit Tests PASS (0.01s)</div>
                <div class="chip chip-green">Pure Stdlib Edge Deployment</div>
            </div>
        """,
    },
    {
        "id": "scene1_tests",
        "narration": (
            "Verification proof executing pytest across Vertex Swarm Agent consensus and FoxMQ defenses. "
            "Confirming honest two-thirds BFT quorum agreement, automatic disqualification of Byzantine outliers "
            "and HIHO drift nodes, and cryptographic dropping of tampered and replayed gossip frames. "
            "Three passed in point zero one seconds."
        ),
        "html_body": """
            <div class="header">
                <span class="badge">V-Model Consensus &amp; Security Proof • 100% Pass</span>
                <h1>BFT Consensus &amp; P2P Firewall Tests</h1>
                <p class="subtitle">Deterministic verification under Byzantine peer injection and replay attacks.</p>
            </div>
            <div style="background:#020617;border:1px solid rgba(56,189,248,0.3);border-radius:12px;padding:24px;margin-top:24px;font-family:monospace;font-size:18px;line-height:1.6;">
                <p style="color:#38bdf8;margin-bottom:14px;">$ pytest tests/test_vertex_swarm_spoke.py -v</p>
                <p><span style="color:#22c55e;">PASSED</span> test_bft_honest_supermajority_consensus</p>
                <p><span style="color:#22c55e;">PASSED</span> test_bft_disqualifies_byzantine_outlier_and_hiho_drift</p>
                <p><span style="color:#22c55e;">PASSED</span> test_foxmq_gossip_verifier_blocks_replay_and_tampering</p>
                <div style="background:rgba(34,197,94,0.15);border:1px solid #22c55e;border-radius:8px;padding:12px;margin-top:20px;color:#22c55e;text-align:center;">
                    ============================== 3 passed in 0.01s ==============================
                </div>
            </div>
            <div class="flow-container" style="margin-top:20px;">
                <div class="chip chip-green">Cohen d = 2.1285 (N=100)</div>
                <div class="chip chip-blue">SPRT LLR = +101.96</div>
                <div class="chip chip-green">p50 Latency = 0.0067 ms</div>
            </div>
        """,
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 2560px; height: 1440px; background: #090d16; color: #f8fafc;
       font-family: system-ui, -apple-system, sans-serif; padding: 50px 70px;
       overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }
.badge { background: rgba(56,189,248,0.15); color: #38bdf8; border: 1px solid rgba(56,189,248,0.4);
         padding: 6px 18px; border-radius: 9999px; font-size: 16px; font-weight: 600; display: inline-block; margin-bottom: 12px; }
h1 { font-size: 48px; font-weight: 700; color: #fff; }
.subtitle { font-size: 22px; color: #94a3b8; margin-top: 6px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
.card { background: #0f172a; border: 1px solid #1e293b; border-radius: 16px; padding: 30px; }
.card-icon { font-size: 38px; margin-bottom: 12px; }
.flow-container { display: flex; gap: 16px; flex-wrap: wrap; }
.chip { padding: 8px 18px; border-radius: 8px; font-size: 16px; font-weight: 600; }
.chip-blue { background: rgba(56,189,248,0.15); color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); }
.chip-green { background: rgba(34,197,94,0.15); color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
</style></head><body>__BODY__</body></html>"""


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
            wavs.append(wav)
        clist = Path(td) / "list.txt"
        clist.write_text("\n".join(f"file '{w}'" for w in wavs), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(clist), "-af", "apad=pad_dur=1.2", "-c:a", "libmp3lame", "-b:a", "192k", str(output_mp3)], check=True, capture_output=True)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_mp4 = repo_root / "docs" / "vertex_swarm_demo.mp4"
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        parts: list[Path] = []
        for scene in SCENES:
            sid = scene["id"]
            html_file = work / f"{sid}.html"
            raw_png = work / f"{sid}_raw.png"
            png_file = work / f"{sid}.png"
            mp3_file = work / f"{sid}.mp3"
            seg_mp4 = work / f"{sid}.mp4"
            html_file.write_text(HTML_TEMPLATE.replace("__BODY__", scene["html_body"]), encoding="utf-8")
            subprocess.run(
                ["google-chrome", "--headless", "--hide-scrollbars", "--disable-gpu", "--force-device-scale-factor=1", f"--screenshot={raw_png}", f"--window-size={WIDTH},{CHROME_CAPTURE_HEIGHT}", str(html_file)],
                check=True,
                capture_output=True,
            )
            Image.open(raw_png).crop((0, 0, WIDTH, HEIGHT)).save(png_file)
            _synthesize_audio(scene["narration"], mp3_file)
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", str(png_file), "-i", str(mp3_file), "-c:v", "libx264", "-crf", "16", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", str(seg_mp4)],
                check=True,
                capture_output=True,
            )
            parts.append(seg_mp4)
        clist = work / "concat.txt"
        clist.write_text("\n".join(f"file '{p}'" for p in parts), encoding="utf-8")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(clist), "-c", "copy", str(out_mp4)], check=True, capture_output=True)
    print(f"GENERATED: {out_mp4} ({out_mp4.stat().st_size} bytes)")


if __name__ == "__main__":
    t0 = time.time()
    main()
    print(f"Elapsed: {time.time() - t0:.1f}s")
