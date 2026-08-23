"""
Helper utilities for services.
"""


def to_dict(data):
    """Convert data to dict, handling both Pydantic models and plain dicts."""
    if isinstance(data, dict):
        return data
    if hasattr(data, "dict"):
        return data.dict()
    if hasattr(data, "model_dump"):
        return data.model_dump()
    return dict(data)


def get_attr(data, key, default=None):
    """Get attribute from data, handling both dicts and objects."""
    if isinstance(data, dict):
        return data.get(key, default)
    return getattr(data, key, default)
