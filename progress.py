# Pure level-progression and best-time helpers (no badge globals).


def next_level(i, n):
    return (i + 1) % n


def migrate(save):
    """Upgrade a legacy {"best": x} save to per-level {"bests": {...}} in place."""
    bests = save.get("bests")
    if not isinstance(bests, dict):
        bests = {}
    legacy = save.pop("best", 0)
    if legacy and "0" not in bests:
        bests["0"] = legacy
    save["bests"] = bests
    return save


def best_for(save, idx):
    return save.get("bests", {}).get(str(idx), 0)


def record_best(save, idx, elapsed):
    """Store elapsed as the level's best if it beats the old one. Returns True if so."""
    bests = save.setdefault("bests", {})
    best = bests.get(str(idx), 0)
    if best == 0 or elapsed < best:
        bests[str(idx)] = round(elapsed, 1)
        return True
    return False
