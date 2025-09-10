__all__ = [
    "DOCKER_USE_CACHE",
    "ASSET_HEADER",
    "FEATURE_CONFIGS",
]

import pathlib
from typing import Any, Generator, MutableMapping

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    AssetOut,
    MetadataValue,
    Output,
    get_dagster_logger,
    multi_asset,
)

LOGGER = get_dagster_logger(__name__)

from OpenStudioLandscapes.engine.constants import DOCKER_USE_CACHE_GLOBAL
from OpenStudioLandscapes.engine.enums import OpenStudioLandscapesConfig

DOCKER_USE_CACHE = DOCKER_USE_CACHE_GLOBAL or False


GROUP = "Teleport"
KEY = [GROUP]
FEATURE = f"OpenStudioLandscapes-{GROUP}".replace("_", "-")

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
}

# @formatter:off
FEATURE_CONFIGS = {
    OpenStudioLandscapesConfig.DEFAULT: {
        "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
        "DOCKER_IMAGE": "public.ecr.aws/gravitational/teleport-distroless:latest",
        "PROXY_SERVICE_PORT_HOST": "443",
        "PROXY_SERVICE_PORT_CONTAINER": "443",
        # "PROXY_SERVICE_AGENTS_PORT_HOST": "3021",
        # "PROXY_SERVICE_AGENTS_PORT_CONTAINER": "3021",
        "PROXY_SERVICE_AGENTS_PORT_HOST": "3025",
        "PROXY_SERVICE_AGENTS_PORT_CONTAINER": "3025",
        "WEB_UI_PORT_HOST": "3080",
        "WEB_UI_PORT_CONTAINER": "3080",
        # "ENV_VAR_PORT_HOST": "1234",
        # "ENV_VAR_PORT_CONTAINER": "4321",
        f"TELEPORT_CONFIG": pathlib.Path(
            "{DOT_FEATURES}",
            FEATURE,
            "volumes",
            "config",
        )
        .expanduser()
        .as_posix(),
        f"TELEPORT_DATA": pathlib.Path(
            "{DOT_FEATURES}",
            FEATURE,
            "volumes",
            "data",
        )
        .expanduser()
        .as_posix(),
        f"TELEPORT_CERT": pathlib.Path(
            "{DOT_FEATURES}",
            FEATURE,
            "volumes",
            "crt",
        )
        .expanduser()
        .as_posix(),
    }
}
# @formatter:on


# Todo:
#  - [ ] move to common_assets
@multi_asset(
    name=f"constants_{ASSET_HEADER['group_name']}",
    outs={
        "NAME": AssetOut(
            **ASSET_HEADER,
            dagster_type=str,
            description="",
        ),
        "FEATURE_CONFIGS": AssetOut(
            **ASSET_HEADER,
            dagster_type=dict,
            description="",
        ),
        "DOCKER_COMPOSE": AssetOut(
            **ASSET_HEADER,
            dagster_type=pathlib.Path,
            description="",
        ),
    },
)
def constants_multi_asset(
    context: AssetExecutionContext,
) -> Generator[
    Output[dict[OpenStudioLandscapesConfig, dict[str | Any, bool | str | Any]]]
    | AssetMaterialization
    | Output[Any]
    | Output[pathlib.Path]
    | Any,
    None,
    None,
]:
    """ """

    yield Output(
        output_name="FEATURE_CONFIGS",
        value=FEATURE_CONFIGS,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("FEATURE_CONFIGS"),
        metadata={
            "__".join(
                context.asset_key_for_output("FEATURE_CONFIGS").path
            ): MetadataValue.json(FEATURE_CONFIGS),
        },
    )

    yield Output(
        output_name="NAME",
        value=__name__,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("NAME"),
        metadata={
            "__".join(context.asset_key_for_output("NAME").path): MetadataValue.path(
                __name__
            ),
        },
    )

    docker_compose = pathlib.Path(
        "{DOT_LANDSCAPES}",
        "{LANDSCAPE}",
        f"{ASSET_HEADER['group_name']}__{'_'.join(ASSET_HEADER['key_prefix'])}",
        "__".join(context.asset_key_for_output("DOCKER_COMPOSE").path),
        "docker_compose",
        "docker-compose.yml",
    )

    yield Output(
        output_name="DOCKER_COMPOSE",
        value=docker_compose,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("DOCKER_COMPOSE"),
        metadata={
            "__".join(
                context.asset_key_for_output("DOCKER_COMPOSE").path
            ): MetadataValue.path(docker_compose),
        },
    )
