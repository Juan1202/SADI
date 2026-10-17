"""
Garantiza que 'app.X' y 'X' resuelvan al mismo módulo Python,
evitando instancias duplicadas de SQLAlchemy entre la app y los tests.
"""
import sys
import importlib.util
import os

_APP_DIR = os.path.dirname(os.path.abspath(__file__))


def _register_alias(bare_name: str) -> None:
    """Registra 'app.<bare_name>' como alias de '<bare_name>' en sys.modules."""
    qualified = f"app.{bare_name}"
    if qualified in sys.modules:
        return
    if bare_name in sys.modules:
        sys.modules[qualified] = sys.modules[bare_name]
        return
    fpath = os.path.join(_APP_DIR, f"{bare_name}.py")
    if not os.path.exists(fpath):
        return
    spec = importlib.util.spec_from_file_location(bare_name, fpath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[bare_name] = mod
    sys.modules[qualified] = mod
    spec.loader.exec_module(mod)


for _mod in ("models", "utils", "extensions"):
    _register_alias(_mod)

# Alias para el paquete routes (directorio)
_routes_dir = os.path.join(_APP_DIR, "routes")
if os.path.isdir(_routes_dir) and "routes" not in sys.modules:
    import importlib
    spec = importlib.util.spec_from_file_location(
        "routes",
        os.path.join(_routes_dir, "__init__.py"),
        submodule_search_locations=[_routes_dir]
    )
    if spec:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["routes"] = mod
        sys.modules["app.routes"] = mod
        if spec.loader:
            spec.loader.exec_module(mod)
