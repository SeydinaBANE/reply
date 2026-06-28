import logging

logger = logging.getLogger(__name__)


def build_custom_job_spec(
    project: str,
    location: str,
    base_model: str,
    staging_bucket: str,
) -> dict[str, object]:
    return {
        "project": project,
        "location": location,
        "base_model": base_model,
        "staging_bucket": staging_bucket,
        "machine_spec": {"machine_type": "a2-highgpu-1g", "accelerator": "NVIDIA_TESLA_A100"},
    }
