# -*- coding: utf-8 -*-
"""
瘥?摮?嚗? repo ?桀?????銝???嚗蕭? attestations.jsonl??
??賢?隞暻?------------
摰???GitHub ?撩?銝?蝣唬??啁??亦?撘Ⅳ嚗?蝣唬???TradingView ?臬嚗??隞亙?**銝??啣?鈭斗?**???芾??????嚗???隞暻潭見??
閬??輯姥??皝?璇撌脣像??蝑???唬?蝑?????
?箔?暻潮???------------
摰?蝝??????冽??遘銝?閮剜敺?鈭箏 12 ??瑁?銝蝑?神??9 ??鈭斗?嚗?10 ?蝑?霅?憿舐內?嗆? closed_total ????詨? ?????嚗??亙停蝛踹鼠??摮??舀??函? GitHub ?漱??銝??璈??隞仿??鈭斗??銝?芸楛隤芯?蝞?
append-only
-----------
?芾蕭??靽格?Ｘ?銵遙雿???????敺? commit ??皝?冽霈?
?冽?
----
    python attest.py            # 餈賢?銝蝑???撌脣??典?頝喲?嚗?    python attest.py --force    # 撘瑕餈賢?嚗葫閰衣嚗?"""
import argparse
import json
import pathlib
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).parent          # ?撠望??repo ?寧??LEDGER = ROOT / "attestations.jsonl"


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
    return [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="??撌脫?摮?銋璅?蕭??)
    args = ap.parse_args()

    now = datetime.now(timezone.utc)
    rows = existing()
    period = now.strftime("%Y-%m")

    if not args.force and any(r.get("period") == period for r in rows):
        print(f"{period} 撌脫?摮?嚗歲??閬撥?嗉蕭? --force嚗?)
        return 0

    spec_hash = read_spec_hash()
    if not spec_hash:
        raise SystemExit("?曆???spec.sha256 ??瘝?閬??輯姥撠望???霅??儔??)

    entry = {
        "seq": len(rows) + 1,
        "period": period,
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "spec_sha256": spec_hash,
        "legs": read_legs(),
        "note": "???霅?閮?甇文?祇?蝝??璅?????啣?鈭斗?嚗?????????,
    }

    with LEDGER.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, separators=(",", ":")) + "\n")

    print(f"撌脰蕭?洵 {entry['seq']} 蝑?霅? ({entry['as_of']})")
    print(f"  閬??輯姥 {spec_hash[:16]}...")
    for leg, v in entry["legs"].items():
        print(f"  {leg:4} 撌脣像??{v['closed_total']:3} 蝑? ???{v['latest_exit']}  "
              f"蝻箄? {v['seq_gaps'] or '??}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


