"""Inline data/*.json into demo/template.html and write demo/index.html.

Run from the repo root:  python demo/build_demo.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TEMPLATE = ROOT / "demo" / "template.html"
OUT = ROOT / "demo" / "index.html"


def load(name: str) -> list[dict]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main() -> None:
    payload = {
        "products": load("products.json"),
        "promotions": load("promotions.json"),
        "policies": load("policies.json"),
    }
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = TEMPLATE.read_text(encoding="utf-8")
    if "__DATA_JSON__" not in html:
        raise SystemExit("placeholder __DATA_JSON__ not found in template")
    OUT.write_text(html.replace("__DATA_JSON__", blob), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(payload['products'])} products, "
          f"{len(payload['promotions'])} promotions, {len(payload['policies'])} policies)")


if __name__ == "__main__":
    main()
