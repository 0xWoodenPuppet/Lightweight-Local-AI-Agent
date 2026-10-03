# agent package

def run_pipeline(*args, **kwargs):
    from .orchestrator import run_pipeline as _run
    return _run(*args, **kwargs)

