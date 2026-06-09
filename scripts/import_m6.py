"""Batch import all M6 xlsx files into Supabase.

Run from project root:
    python scripts/import_m6.py
"""
import os
import sys
from pathlib import Path

# Allow importing app/lib when run from scripts/
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "app"))

# Load secrets manually (tiny TOML parser for our flat format)
import re

SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"
secrets = {}
for line in SECRETS_PATH.read_text().splitlines():
    m = re.match(r'(\w+)\s*=\s*"([^"]+)"', line)
    if m:
        secrets[m.group(1)] = m.group(2)

os.environ["SUPABASE_URL"] = secrets["SUPABASE_URL"]
os.environ["SUPABASE_KEY"] = secrets["SUPABASE_KEY"]

# Patch streamlit secrets shim
class _SecretsShim:
    def get(self, k, default=None):
        return os.environ.get(k, default)
    def __getitem__(self, k):
        return os.environ[k]

import streamlit as st
st.secrets = _SecretsShim()
st.cache_resource = lambda f: f  # no-op decorator outside Streamlit

from lib import etl, parsers  # noqa: E402


def main():
    base = Path("/Users/admin/Downloads/Zelt/M6")
    if not base.exists():
        print(f"ERROR: {base} not found")
        sys.exit(1)

    # 1) Creator List
    print("\n=== Creator List ===")
    for f in sorted((base / "Creator").glob("*.xlsx")):
        r = etl.process_file(f)
        etl.log_upload(f.name, r)
        print(f"  {f.name}: {r['status']} ({r['notes']})")

    # 2) Video List
    print("\n=== Videos ===")
    for f in sorted((base / "VideoallCreator").glob("*.xlsx")):
        r = etl.process_file(f)
        etl.log_upload(f.name, r)
        print(f"  {f.name}: {r['status']} ({r['notes']})")

    # 3) Live List
    print("\n=== Lives ===")
    for f in sorted((base / "Live").glob("*.xlsx")):
        r = etl.process_file(f)
        etl.log_upload(f.name, r)
        print(f"  {f.name}: {r['status']} ({r['notes']})")

    # 4) Product (root-level)
    print("\n=== Product Daily ===")
    for f in sorted((base / "Product").glob("ListProducts_*.xlsx")):
        r = etl.process_file(f)
        etl.log_upload(f.name, r)
        print(f"  {f.name}: {r['status']} ({r['notes']})")

    # 5) Product x Creator (in subfolders)
    print("\n=== Product x Creator ===")
    for pdir in sorted((base / "Product").iterdir()):
        if not pdir.is_dir():
            continue
        pid = pdir.name
        if not (pid.isdigit() and len(pid) >= 15):
            continue
        for f in sorted(pdir.glob("ListCreators_*.xlsx")):
            r = etl.process_file(f, product_id_hint=pid)
            etl.log_upload(f.name, r)
            print(f"  [{pid}] {f.name}: {r['status']} ({r['notes']})")

    print("\n✓ Done")


if __name__ == "__main__":
    main()
