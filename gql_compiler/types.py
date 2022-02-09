from typing import Dict, TypedDict


ScalarConfig = TypedDict("ScalarConfig", {"import": str, "value": str})


class Config(TypedDict, total=True):
    output_path: str
    scalar_map: Dict[str, ScalarConfig]
    query_ext: str