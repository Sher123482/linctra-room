# -*- coding: utf-8 -*-
"""
每月存證：對 repo 目前的狀態蓋一個時間戳，追加到 attestations.jsonl。

這支能做什麼
------------
它跑在 GitHub 的伺服器上，碰不到策略程式碼，也碰不到 TradingView 匯出，
所以它不會新增交易。它只記錄「在這個時間點，公開紀錄長什麼樣」：
規則承諾的雜湊、每條腿已平倉的筆數、最新一筆的時間。

為什麼這有用
------------
它把紀錄的狀態釘在時間軸上。假設日後有人在 12 月偷偷補一筆日期寫成 9 月的交易，
10 月那筆存證會顯示當時 closed_total 還是舊的數字 —— 前後矛盾，一查就穿幫。
存證由 GitHub 產生並提交，不經過本機，所以連提交時間都不是自己說了算。

append-only
-----------
只追加、不修改既有行。任何對舊行的改動都會讓後續 commit 的雜湊全部改變。

這支刻意放在 repo 根目錄而不是 tools/：它必須公開才能在 CI 上執行，
而 tools/ 的原則是「一律不公開」。公開的程式放公開區，界線才不會被開洞。

用法
----
    python attest.py            # 追加一筆（同月已存在則跳過）
    python attest.py --force    # 強制追加（測試用）
"""
import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).parent          # 這支就放在 repo 根目錄
LEDGER = ROOT / "attestations.jsonl"


def read_spec_hash():
    p = ROOT / "spec.sha256"
    return p.read_text(encoding="utf-8").splitlines()[0].strip() if p.exists() else None


def read_legs():
    legs = {}
    for f in sorted((ROOT / "signals").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        trades = d.get("trades", [])
        legs[d.get("leg", f.stem)] = {
            "closed_total": len(trades),
            "seq_max": max((t["seq"] for t in trades), default=0),
            "seq_gaps": d.get("counts", {}).get("seq_gaps", []),
            "latest_exit": trades[-1]["exit"] if trades else None,
        }
    return legs


def existing():
    if not LEDGER.exists():
        return []
    return [json.loads(line) for line in
            LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true",
                    help="append even if this month already has one")
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    rows = existing()
    period = now.strftime("%Y-%m")

    if not args.force and any(r.get("period") == period for r in rows):
        print(f"{period} already attested, skipping. (use --force to append anyway)")
        return 0

    spec_hash = read_spec_hash()
    if not spec_hash:
        raise SystemExit("spec.sha256 not found - no rule commitment, nothing to attest.")

    entry = {
        "seq": len(rows) + 1,
        "period": period,
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "spec_sha256": spec_hash,
        "legs": read_legs(),
        "note": "State attestation: records how the public record looked at this moment. "
                "Adds no trades; pins state and time.",
    }

    with LEDGER.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"appended attestation #{entry['seq']}  ({entry['as_of']})")
    print(f"  commitment {spec_hash[:16]}...")
    for leg, v in entry["legs"].items():
        print(f"  {leg:4} closed {v['closed_total']:3}  latest {v['latest_exit']}  "
              f"gaps {v['seq_gaps'] or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
