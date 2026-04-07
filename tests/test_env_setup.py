import importlib

def test_imports():
    """Verify that required libraries are installed."""
    required_libs = ["alpaca", "google.genai", "dotenv"]
    for lib in required_libs:
        try:
            importlib.import_module(lib)
        except ImportError:
            assert False, f"Library {lib} is not installed"
