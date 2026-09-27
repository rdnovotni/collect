"""Scaffold a minimal valid Collect record for `collect init`."""
from __future__ import annotations

from . import resources as R

LAYERS = ["work", "catalog", "variant", "instance", "collection"]


def scaffold_record(layer: str, category: str | None = None, id_: str = "local:0001") -> dict:
    """Build the smallest record that validates cleanly (no errors) for the given layer.

    A 'variant' record's 'variantOf' is left as an obvious placeholder id the user must
    replace; validating it alone produces an unresolved-reference warning, not an error.
    """
    if layer not in LAYERS:
        raise ValueError(f"unknown layer '{layer}' (expected one of: {', '.join(LAYERS)})")
    record: dict = {"collect": "0.1", "id": id_, "layer": layer}
    if layer == "variant":
        record["variantOf"] = "local:REPLACE_WITH_CATALOG_ID"
    elif layer == "collection":
        record["entries"] = []
    if category:
        record["category"] = category
    return record


def profile_fields_for(layer: str, category: str) -> list[str]:
    """Namespaced 'profileId:fieldName' keys the category's profile (if any) allows on this layer."""
    prof = R.profiles().get(category)
    if not prof:
        return []
    return [f"{prof['id']}:{name}" for name, spec in prof["fields"].items() if layer in spec["layers"]]
