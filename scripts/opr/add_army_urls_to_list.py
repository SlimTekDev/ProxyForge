#!/usr/bin/env python3
"""
Add army books from API URLs to data/opr/army_forge_armies.json.
Parses each URL for armyId (path) and gameSystem (query), adds new entries with armyName "TBD"
(real name comes from API when fetching). Then run build_unified_army_list.py and fetch.
"""
import json
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
ARMIES_JSON = REPO_ROOT / "data" / "opr" / "army_forge_armies.json"


def parse_army_url(url: str) -> tuple[str, int] | None:
    """Return (army_id, game_system) or None."""
    url = url.strip()
    if not url or not url.startswith("http"):
        return None
    try:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        # .../army-books/ID
        match = re.search(r"/army-books/([^/]+)$", path)
        if not match:
            return None
        army_id = match.group(1)
        qs = parse_qs(parsed.query)
        gs = qs.get("gameSystem", [None])[0]
        if gs is None:
            return None
        game_system = int(gs)
        return (army_id, game_system)
    except (ValueError, IndexError):
        return None


def main():
    urls = """
https://army-forge.onepagerules.com/api/army-books/pEe3OdMBT2RjUCkK?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/kBNqpwRCrON316Xh?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/b-C24v_ZtAbPWjhh?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/K0Rw3xTwvYEEYtaE?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/su14GsZGn8ZJ2UpX?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/UJtPJALv67KhDr4c?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/ovdxmUNFykOZt5sn?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/ThPtNwfE_198CVjj?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/0nDuE4wakf6TJvpN?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/OFKEcmXt3DWLtuCv?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/kiK2WUN-VandYxaX?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/4OUH436aAAGKi434?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/aLJlapGjkQAQoFQF?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/84gm9NxqgVtmEjy8?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/qfj5V1obc_onilaf?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/oIMlrfX7Do1jI6QL?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/aCn5cizlLV8-qaYO?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/h7vWnQdSePFM_ba0?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/XPmCIDxlrieCYum6?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/q9pTeT_J8OBOqj2f?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/ICL2QYIIT42k_XBz?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/S8qGWiXA5KZdsHw_?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/QJTDIkYMAqV-Ciqq?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/AX0hEwHx5mwJp0OI?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/LjUE26Sl3HZ7rG7g?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Jmy7HZyW8WajGCCd?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/9JH4CK95QJUdI3Ep?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/5O1zb1Av5i2fEab9?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/vHwYMZ_1K1pAJhZN?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/o5Q8lHXLz0RozAw4?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/pbF2aWhZhiYcaw_J?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/tXlDML7Wojb2sAG3?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/lvDFnhlCv5qjAa3u?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Yha7xjXfTyWI3j_o?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/MeID3bfZxGzQga6m?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/E_pm0TWSrQYoIY2d?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/kBNqpwRCrON316Xh?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/pEe3OdMBT2RjUCkK?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/aLJlapGjkQAQoFQF?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/b-C24v_ZtAbPWjhh?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/K0Rw3xTwvYEEYtaE?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/13UQcqEOM9ufwm2k?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/su14GsZGn8ZJ2UpX?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/UJtPJALv67KhDr4c?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/0nDuE4wakf6TJvpN?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/OFKEcmXt3DWLtuCv?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/ovdxmUNFykOZt5sn?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/ThPtNwfE_198CVjj?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/kiK2WUN-VandYxaX?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/84gm9NxqgVtmEjy8?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/oIMlrfX7Do1jI6QL?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/QJTDIkYMAqV-Ciqq?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/NPZs51l4s0gTpw8L?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/6auQBa5TuDJAOKEG?gameSystem=2&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/AX0hEwHx5mwJp0OI?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/LjUE26Sl3HZ7rG7g?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Jmy7HZyW8WajGCCd?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/9JH4CK95QJUdI3Ep?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/5O1zb1Av5i2fEab9?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/vHwYMZ_1K1pAJhZN?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/o5Q8lHXLz0RozAw4?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/pbF2aWhZhiYcaw_J?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/tXlDML7Wojb2sAG3?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/lvDFnhlCv5qjAa3u?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Yha7xjXfTyWI3j_o?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/MeID3bfZxGzQga6m?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/E_pm0TWSrQYoIY2d?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/6auQBa5TuDJAOKEG?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/NPZs51l4s0gTpw8L?gameSystem=3&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/TciwNI3AOMXAM-dr?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/FF4UemWHh60T1VRq?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/IKT625BeGZtF67EA?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/L1zCkfmeAongLj1X?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Lo39Hss3bevFj44V?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/VU1EFPa2uODffW8D?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/RJDq2ZD7wjlAcUVB?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/-MrGWaleoZR7pxIn?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/mdT4HVzHUmxGevc_?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/q9BQlBp583ZuuOnQ?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/cF1dpwd4bhYsNhsf?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/T0CE9PUv4YDjbrjJ?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/ZORJcHSuqj4T4QP3?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/TngTE5FtTZNKEHuG?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/_6i8hfKF0YvVL2K4?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/n_YscnPzKx93ekFl?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/kQRIk8Zu_bQ58pnB?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/bNSIMUiXr93FhqJE?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/4ZMoS6P-3zRZUl51?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Bsir5TSffxMozeGY?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/4SBY8ONErd3HUxle?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/0EXXlzFwAk3q1n5e?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/8siLk9I6-H8lk78b?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/PGxKcq4R571OtwqD?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/CNOmkR5Q2C7Dc4Nm?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/zZ3RNHVtFJIZqzzN?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/upWNWC9UIXtQP2o_?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/TjNtGnCDVts3l3ER?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/bPAtRGFrpFfyAjLW?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/jZ02AVPLx_S48Mnb?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/RgHxqAlAXnUuF3ty?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/t-sIke2snonFSL6Q?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/lpRj9EBwROpO1um7?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/AQSDPFVL1DiNNnSU?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/a_HXTYv06IFtSs9G?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/tOWt5fgqK2nfpoBN?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/yxVDySKYQYRhdEgA?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/CuyCCyZTIHo5rc0Z?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/vJuokTQpJWj3_MrJ?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Q59-nh6A1AhRBrLR?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/BubhE1kUpgYbqZvW?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/gHTrjw-g76vfGCSt?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/AcDXPPXmWrgHChlS?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/qABIfXYbYxmA75yL?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Ir5XtqTM8JS3YEAJ?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/qtuyeoRfXKlNflK0?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/xQ7Md18lq2LHqydZ?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/WV4m7DSbSzwqZHXx?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/APPugMUeG4Weg40b?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/izHq50z2QjwQFP04?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/RDx9-OtzUmLTidmU?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Ga7ces41DBilEJGd?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/r3X6wqZWBZ-Bq07E?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/_V5fDX2W49nuJzT6?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/brKjxAcy7XvSr6Rw?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/NJChBLgD3vZuI6Ui?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/-9xUT6lHle3FJUq9?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/KWxFi8QsM1-yqOqL?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/dyJB70sM9H-eNt6f?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/1YnHlHHPWzsJB4-q?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/gV6d9bJeLrAo2pax?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/npKG2yzpKEilFMv0?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/cl3YXSzpTAeiqPpt?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/8jPo-bZTy3k28KjC?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/P0h69KdcUhciBiPA?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/jG4zrHn4eAsucIDr?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/hLQsnMoeaMti7Pp0?gameSystem=5&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/xQ7Md18lq2LHqydZ?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/WV4m7DSbSzwqZHXx?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/APPugMUeG4Weg40b?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/izHq50z2QjwQFP04?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/RDx9-OtzUmLTidmU?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/Ga7ces41DBilEJGd?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/r3X6wqZWBZ-Bq07E?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/_V5fDX2W49nuJzT6?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/NJChBLgD3vZuI6Ui?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/brKjxAcy7XvSr6Rw?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/-9xUT6lHle3FJUq9?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/KWxFi8QsM1-yqOqL?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/WijRGtjthDVmg_hx?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/dyJB70sM9H-eNt6f?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/1YnHlHHPWzsJB4-q?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/gV6d9bJeLrAo2pax?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/npKG2yzpKEilFMv0?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/cl3YXSzpTAeiqPpt?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/8jPo-bZTy3k28KjC?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/P0h69KdcUhciBiPA?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/jG4zrHn4eAsucIDr?gameSystem=4&simpleMode=false
https://army-forge.onepagerules.com/api/army-books/hLQsnMoeaMti7Pp0?gameSystem=4&simpleMode=false
"""
    pairs = set()
    for line in urls.strip().splitlines():
        parsed = parse_army_url(line)
        if parsed:
            pairs.add(parsed)

    with open(ARMIES_JSON, "r", encoding="utf-8") as f:
        armies = json.load(f)
    existing = {(a["armyId"], a["gameSystem"]) for a in armies}
    added = []
    for (army_id, game_system) in sorted(pairs, key=lambda x: (x[1], x[0])):
        if (army_id, game_system) not in existing:
            entry = {"armyId": army_id, "gameSystem": game_system, "armyName": "TBD"}
            armies.append(entry)
            added.append(entry)
            existing.add((army_id, game_system))

    with open(ARMIES_JSON, "w", encoding="utf-8") as f:
        json.dump(armies, f, indent=2, ensure_ascii=False)
    print(f"Updated {ARMIES_JSON}")
    print(f"  Total entries: {len(armies)}")
    print(f"  New entries added: {len(added)}")
    if added:
        for e in added[:20]:
            print(f"    {e['armyId']} gameSystem={e['gameSystem']}")
        if len(added) > 20:
            print(f"    ... and {len(added) - 20} more")


if __name__ == "__main__":
    main()
