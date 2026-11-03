from langgraph.config import get_stream_writer

def emit(step_id: str, label: str, status: str='running', **extra):
    get_stream_writer()({"stage": step_id, "id": step_id, "label": label, "status": status, **extra})