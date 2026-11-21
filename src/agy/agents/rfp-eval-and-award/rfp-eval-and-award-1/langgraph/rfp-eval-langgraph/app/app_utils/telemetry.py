# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""OpenTelemetry setup for the LangChain agent.

Exports traces to Cloud Trace and GenAI prompt/response logs to Cloud Logging +
GCS. ``generate_content`` spans come from the google-genai instrumentor; graph,
agent, and tool spans from the LangChain instrumentor. With no GCP credentials
the Cloud exporters are skipped and only in-process instrumentation runs.
"""

from __future__ import annotations

import logging
import os

_initialized = False


def _configure_genai_capture() -> None:
    """Set the GenAI prompt/response capture env vars (no-op without a bucket)."""
    bucket = os.environ.get("LOGS_BUCKET_NAME")
    capture = os.environ.get(
        "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "false"
    )
    if not (bucket and capture != "false"):
        logging.info(
            "Prompt-response logging disabled (set LOGS_BUCKET_NAME and "
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT to enable)."
        )
        return
    os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "NO_CONTENT"
    os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_UPLOAD_FORMAT", "jsonl")
    os.environ.setdefault("OTEL_INSTRUMENTATION_GENAI_COMPLETION_HOOK", "upload")
    os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental")
    path = os.environ.get("GENAI_TELEMETRY_PATH", "completions")
    os.environ.setdefault(
        "OTEL_INSTRUMENTATION_GENAI_UPLOAD_BASE_PATH", f"gs://{bucket}/{path}"
    )


def _build_resource():
    """Build the trace/log Resource: service identity + GCP resource attributes."""
    from opentelemetry.sdk.resources import OTELResourceDetector, Resource

    resource = Resource.create(
        {
            "service.name": os.environ.get("OTEL_SERVICE_NAME", "langchain-agent"),
            "service.version": os.environ.get("COMMIT_SHA", "dev"),
        }
    )
    resource = resource.merge(OTELResourceDetector().detect())
    try:
        from opentelemetry.resourcedetector.gcp_resource_detector import (
            GoogleCloudResourceDetector,
        )

        resource = resource.merge(
            GoogleCloudResourceDetector(raise_on_error=False).detect()
        )
    except Exception as e:  # best-effort; unavailable off-GCP
        logging.debug("GCP resource detection skipped: %s", e)
    return resource


def _setup_cloud_exporters() -> None:
    """Export traces to Cloud Trace and GenAI event logs to Cloud Logging."""
    import google.auth
    from opentelemetry import _logs, trace
    from opentelemetry.exporter.cloud_logging import CloudLoggingExporter
    from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
    from opentelemetry.sdk._logs import LoggerProvider
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    _, project_id = google.auth.default()
    resource = _build_resource()

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(CloudTraceSpanExporter(project_id=project_id))
    )
    trace.set_tracer_provider(tracer_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(CloudLoggingExporter(project_id=project_id))
    )
    _logs.set_logger_provider(logger_provider)


def _install_instrumentation() -> None:
    """Instrument the google-genai SDK and LangChain/LangGraph execution."""
    try:
        from opentelemetry.instrumentation.google_genai import (
            GoogleGenAiSdkInstrumentor,
        )

        GoogleGenAiSdkInstrumentor().instrument()
    except Exception as e:  # pragma: no cover - optional dependency
        logging.warning("google-genai instrumentation unavailable: %s", e)
    try:
        from opentelemetry.instrumentation.genai.langchain import (
            LangChainInstrumentor,
        )

        LangChainInstrumentor().instrument()
    except Exception as e:  # pragma: no cover - optional dependency
        logging.warning("LangChain instrumentation unavailable: %s", e)


def _cloud_export_enabled() -> bool:
    """Honour the switch ADK reads, so both frameworks turn off the same way.

    Agent Runtime sets it at deploy time; elsewhere it is absent and export is
    on, which is what the ADK templates do for Cloud Run and GKE.
    """
    value = os.environ.get("GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY")
    return value is None or value.lower() in ("true", "1")


def setup_telemetry() -> None:
    """Configure tracing, GenAI logging, and instrumentation (idempotent)."""
    global _initialized
    if _initialized:
        return
    _initialized = True

    # gen_ai spans require this experimental semconv opt-in.
    os.environ.setdefault("OTEL_SEMCONV_STABILITY_OPT_IN", "gen_ai_latest_experimental")
    _configure_genai_capture()
    if not _cloud_export_enabled():
        logging.info(
            "Cloud telemetry export disabled by "
            "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY."
        )
    else:
        try:
            _setup_cloud_exporters()
        except Exception as e:  # no GCP creds (local dev): keep instrumentation
            logging.warning("Cloud telemetry export not configured: %s", e)
    _install_instrumentation()
