import pytest

pytest.importorskip("testcontainers")

import hvac
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from inference.vault_client import HvacSecretReader, VaultClient

pytestmark = pytest.mark.integration

_ROOT_TOKEN = "root-token"


def test_read_secret_against_real_vault() -> None:
    container = (
        DockerContainer("hashicorp/vault:1.15")
        .with_env("VAULT_DEV_ROOT_TOKEN_ID", _ROOT_TOKEN)
        .with_env("VAULT_DEV_LISTEN_ADDRESS", "0.0.0.0:8200")
        .with_exposed_ports(8200)
    )
    with container:
        wait_for_logs(container, "Vault server started")
        addr = f"http://{container.get_container_host_ip()}:{container.get_exposed_port(8200)}"
        admin = hvac.Client(url=addr, token=_ROOT_TOKEN)
        admin.secrets.kv.v2.create_or_update_secret(path="llm", secret={"api_keys": "a,b"})

        vault = VaultClient(HvacSecretReader(addr, _ROOT_TOKEN))
        assert vault.read_secret("llm", "api_keys") == "a,b"
