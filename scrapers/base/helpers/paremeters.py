import inspect


def supports_param(cls: type, param_name: str) -> bool:
    """True jeśli __init__ klasy przyjmuje parametr o nazwie param_name lub **kwargs."""
    try:
        sig = inspect.signature(cls.__init__)
    except (TypeError, ValueError):
        return False

    params = sig.parameters
    if param_name in params:
        return True
    return any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params.values())
