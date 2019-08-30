from pydoc import locate


def get_backend(path, backend):
    """
    Path Example: bothub_backend.bothub.BothubBackend
    Backend Example: https://api.bothub.it
    """
    return locate(path)(backend=backend)