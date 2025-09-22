__all__ = [
    "DOCKER_USE_CACHE",
    "ASSET_HEADER",
    "FEATURE_CONFIGS",
    "SERVICE_NAME",
]

import pathlib
from typing import Any, Generator

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
from OpenStudioLandscapes.engine.enums import OpenStudioLandscapesConfig, ComposeNetworkMode

DOCKER_USE_CACHE = DOCKER_USE_CACHE_GLOBAL or False


GROUP = "Teleport"
KEY = [GROUP]
FEATURE = f"OpenStudioLandscapes-{GROUP}".replace("_", "-")
SERVICE_NAME = GROUP.lower()

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
}

# @formatter:off
FEATURE_CONFIGS = {
    OpenStudioLandscapesConfig.DEFAULT: {
        "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
        "COMPOSE_NETWORK_MODE": ComposeNetworkMode.HOST,
        # :latest does not exist
        # https://gallery.ecr.aws/gravitational
        "DOCKER_IMAGE": "public.ecr.aws/gravitational/teleport-distroless-debug:18",
        # https://goteleport.com/docs/reference/networking/#auth-service-ports
        # auth Service:
        "PROXY_SERVICE_AGENTS_PORT_HOST": "3025",
        "PROXY_SERVICE_AGENTS_PORT_CONTAINER": "3025",
        # https://goteleport.com/docs/reference/networking/#ports-without-tls-routing
        "WEB_UI_PORT_HOST": "443",
        "WEB_UI_PORT_CONTAINER": "443",
        # proxy Service:
        "ALL_CLIENTS_PORT_HOST": "3023",
        "ALL_CLIENTS_PORT_CONTAINER": "3023",
        "TELEPORT_CONFIG": pathlib.Path(
            "{DOT_LANDSCAPES}",
            "{LANDSCAPE}",
            f"{GROUP}__{'__'.join(KEY)}",
            "volumes",
            "config",
        )
        .expanduser()
        .as_posix(),
        "ACME_SH_DIR": pathlib.Path(
            "{DOT_LANDSCAPES}",
            ".acme.sh",
        )
        .expanduser()
        .as_posix(),
        "TELEPORT_DATA": pathlib.Path(
            "{DOT_LANDSCAPES}",
            "{LANDSCAPE}",
            f"{GROUP}__{'__'.join(KEY)}",
            "volumes",
            "data",
        )
        .expanduser()
        .as_posix(),
        "TELEPORT_CERT": {
            #################################################################
            # Certificates directory
            #################################################################
            #################################################################
            # Inside Landscape:
            "default": pathlib.Path(
                "{DOT_LANDSCAPES}",
                "{LANDSCAPE}",
                ".acme.sh",
                "certs",
            )
            .expanduser()
            .as_posix(),
            #################################################################
            # In Landscapes root dir:
            "landscapes_root": pathlib.Path(
                "{DOT_LANDSCAPES}",
                ".acme.sh",
                "certs",
            )
            .expanduser()
            .as_posix(),
        }["landscapes_root"],
        # Todo:
        #  - [ ] find a dynamic way to fetch all services with the correct ports etc.
        #
        # Todo:
        #  - [x] Try with local IP (wlp0s20f3,  192.168.178.195:4545) and exposed port
        #        $ nc -vz 192.168.178.195 4545
        #        Connection to 192.168.178.195 4545 port [tcp/*] succeeded!
        #  - [x] Try with hostname (kitsu.farm.evil:80) and exposed port
        #        $ nc -vz kitsu.farm.evil 80
        #        Connection to kitsu.farm.evil (172.20.0.2) 80 port [tcp/http] succeeded!
        #  - [x] Try with loopback IP (127.0.0.1:80) and exposed port
        #        $ nc -vz 127.0.0.1 80
        #        Connection to 127.0.0.1 80 port [tcp/http] succeeded!
        #  - [x] Try with loopback IP (127.0.1.1:80) and exposed port
        #        $ nc -vz 127.0.1.1 80
        #        Connection to 127.0.1.1 80 port [tcp/http] succeeded!
        #  - [ ] make sure teleport start runs automatically somewhere
        "TELEPORT_WEB_APPS": [
            {
                "name": "ayon",
                # for ayon specifically, uri could be:
                # "uri": "http://localhost:5005/",
                # "uri": "http://server.farm.evil:5005/",
                # "uri": "192.168.178.195:5005/",
                "uri": "http://localhost:5005/",
                "insecure_skip_verify": False,
                "public_addr": "",
                "use_any_proxy_public_addr": False,
            },
            {
                "name": "dagster",
                "uri": "http://localhost:3003/",
                "insecure_skip_verify": False,
                "public_addr": "",
                "use_any_proxy_public_addr": False,
            },
            {
                "name": "kitsu",
                "uri": "http://localhost:4545/",
                "insecure_skip_verify": False,
                "public_addr": "",
                "use_any_proxy_public_addr": False,
            },
        ]
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
