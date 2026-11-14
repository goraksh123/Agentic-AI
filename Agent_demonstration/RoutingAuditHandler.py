
import json
import logging
import time
import uuid
from datetime import datetime, timezone

from langchain_core.callbacks import BaseCallbackHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("routing_audit.log")
    ]
)

logger = logging.getLogger("routing_audit")


class RoutingAuditHandler(BaseCallbackHandler):

    def __init__(self, request_id):
        self.request_id = request_id
        self.started = {}
        self.run_info = {}

    def log_event(self, event, **fields):
        record = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "request_id": self.request_id,
            "event": event,
            **fields
        }
        logger.info(json.dumps(record, default=str))

    def on_chain_start(
        self,
        serialized,
        inputs,
        *,
        run_id,
        parent_run_id=None,
        tags=None,
        metadata=None,
        **kwargs
    ):
        self.started[run_id] = time.perf_counter()

        info = {
            "run_id": str(run_id),
            "parent_run_id": (
                str(parent_run_id)
                if parent_run_id else None
            ),
            "tags": tags or [],
            "metadata": metadata or {}
        }

        self.run_info[run_id] = info

        self.log_event(
            "CHAIN_STARTED",
            **info
        )

    def on_chain_end(
        self,
        outputs,
        *,
        run_id,
        **kwargs
    ):
        elapsed = (
            time.perf_counter()
            - self.started.get(
                run_id,
                time.perf_counter()
            )
        ) * 1000

        info = self.run_info.get(run_id, {})

        self.log_event(
            "CHAIN_COMPLETED",
            run_id=str(run_id),
            latency_ms=round(elapsed, 2),
            metadata=info.get("metadata", {})
        )

        if isinstance(outputs, dict):
            if "destination" in outputs:
                self.log_event(
                    "ROUTER_DECISION",
                    run_id=str(run_id),
                    destination=outputs["destination"],
                    metadata=info.get("metadata", {})
                )

    def on_llm_start(
        self,
        serialized,
        prompts,
        *,
        run_id,
        parent_run_id=None,
        **kwargs
    ):
        self.started[run_id] = time.perf_counter()
        self.log_event(
            "LLM_STARTED",
            run_id=str(run_id),
            parent_run_id=str(parent_run_id)
        )

    def on_chat_model_start(
        self,
        serialized,
        messages,
        *,
        run_id,
        parent_run_id=None,
        **kwargs
    ):
        self.started[run_id] = time.perf_counter()
        self.log_event(
            "CHAT_MODEL_STARTED",
            run_id=str(run_id),
            parent_run_id=str(parent_run_id)
        )

    def on_llm_end(
        self,
        response,
        *,
        run_id,
        **kwargs
    ):
        start = self.started.get(run_id)
        elapsed = (
            (time.perf_counter() - start) * 1000
            if start is not None else None
        )

        self.log_event(
            "LLM_COMPLETED",
            run_id=str(run_id),
            latency_ms=(
                round(elapsed, 2)
                if elapsed is not None else None
            )
        )

    def on_llm_error(
        self,
        error,
        *,
        run_id,
        **kwargs
    ):
        self.log_event(
            "LLM_ERROR",
            run_id=str(run_id),
            error_type=type(error).__name__,
            error=str(error)
        )

    def on_chain_error(
        self,
        error,
        *,
        run_id,
        **kwargs
    ):
        self.log_event(
            "CHAIN_ERROR",
            run_id=str(run_id),
            error_type=type(error).__name__,
            error=str(error)
        )
