"""Spec-drift check: the served /openapi.json must not drift from the committed
contract.

Not byte-equality — FastAPI's generated document differs structurally from the
hand-authored spec — but a normalized subset that catches real drift:

- the set of paths + methods must match exactly (no undocumented endpoints,
  no unimplemented ones);
- every served response code must be documented in the contract;
- the GET /colours limit bounds must match;
- the colour enum must match.
"""
import requests
import yaml

SPEC_PATH = "domain/contracts/api/behaviour-service.openapi.yaml"
SERVED_URL = "http://behaviour-service:8000/openapi.json"

METHODS = {"get", "put", "post", "delete", "patch", "head", "options", "trace"}


def _operations(spec: dict) -> dict:
    ops = {}
    for path, item in spec.get("paths", {}).items():
        for method, op in item.items():
            if method in METHODS:
                ops[(path, method)] = op
    return ops


def _resolve(schema: dict, spec: dict) -> dict:
    """Shallow $ref/allOf resolution — enough to reach an enum or scalar."""
    while True:
        if "$ref" in schema:
            name = schema["$ref"].rsplit("/", 1)[-1]
            schema = spec["components"]["schemas"][name]
        elif "allOf" in schema and len(schema["allOf"]) == 1:
            schema = schema["allOf"][0]
        else:
            return schema


def _colour_enum(spec: dict) -> list:
    event = spec["components"]["schemas"]["ColourEvent"]
    colour = _resolve(event["properties"]["colour"], spec)
    return sorted(colour["enum"])


def _limit_bounds(op: dict) -> dict:
    (param,) = [p for p in op.get("parameters", []) if p["name"] == "limit"]
    schema = param["schema"]
    return {
        "minimum": schema.get("minimum"),
        "maximum": schema.get("maximum"),
        "default": schema.get("default"),
    }


def test_spec_drift():
    with open(SPEC_PATH) as f:
        contract = yaml.safe_load(f)
    served = requests.get(SERVED_URL, timeout=5).json()

    contract_ops = _operations(contract)
    served_ops = _operations(served)

    assert set(served_ops) == set(contract_ops), (
        f"paths/methods drift: served-only={set(served_ops) - set(contract_ops)}, "
        f"contract-only={set(contract_ops) - set(served_ops)}"
    )

    for key, served_op in served_ops.items():
        served_codes = set(served_op.get("responses", {}))
        contract_codes = set(contract_ops[key].get("responses", {}))
        assert served_codes <= contract_codes, (
            f"{key} serves undocumented response codes: {served_codes - contract_codes}"
        )

    assert _limit_bounds(served_ops[("/colours", "get")]) == _limit_bounds(
        contract_ops[("/colours", "get")]
    ), "GET /colours limit bounds drifted"

    assert _colour_enum(served) == _colour_enum(contract), "colour enum drifted"

    print("Served OpenAPI matches the committed contract!")


if __name__ == "__main__":
    test_spec_drift()
