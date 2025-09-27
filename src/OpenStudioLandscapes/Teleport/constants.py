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
from OpenStudioLandscapes.engine.enums import (
    ComposeNetworkMode,
    FeatureVolumeType,
    OpenStudioLandscapesConfig,
)

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
        "HOSTNAME": "teleport",
        "TELEPORT_ENTRY_POINT_HOST": "{{HOSTNAME}}",  # Either a hardcoded str or a ref to a Variable (with double {{ }}!)
        "TELEPORT_ENTRY_POINT_PORT": "{{WEB_UI_PORT_HOST}}",  # Either a hardcoded str or a ref to a Variable (with double {{ }}!)
        "COMPOSE_NETWORK_MODE": ComposeNetworkMode.HOST,
        # Repository: https://gallery.ecr.aws/gravitational
        # "latest" tag does not exist
        "DOCKER_IMAGE": "public.ecr.aws/gravitational/teleport-distroless-debug:18",
        # https://goteleport.com/docs/reference/networking/#auth-service-ports
        # auth Service:
        "PROXY_SERVICE_TUNNEL_LISTEN_ADDRESS_PORT_HOST": "3024",
        "PROXY_SERVICE_TUNNEL_LISTEN_ADDRESS_PORT_CONTAINER": "3024",
        "PROXY_SERVICE_AGENTS_PORT_HOST": "3025",
        "PROXY_SERVICE_AGENTS_PORT_CONTAINER": "3025",
        # https://goteleport.com/docs/reference/networking/#ports-without-tls-routing
        "WEB_UI_PORT_HOST": [
            "443",
            "3080",
        ][0],
        "WEB_UI_PORT_CONTAINER": [
            "443",
            "3080",
        ][0],
        # proxy Service:
        "ALL_CLIENTS_PORT_HOST": "3023",
        "ALL_CLIENTS_PORT_CONTAINER": "3023",
        # ssh_service
        "LISTEN_ADDRESS_HOST": "3022",
        "LISTEN_ADDRESS_CONTAINER": "3022",
        "TELEPORT_CONFIG": {
            FeatureVolumeType.CONTAINED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                "{LANDSCAPE}",
                f"{GROUP}__{'__'.join(KEY)}",
                "volumes",
                "config",
            )
            .expanduser()
            .as_posix(),
            FeatureVolumeType.SHARED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                "{DOT_SHARED_VOLUMES}",
                f"{GROUP}__{'__'.join(KEY)}",
                "volumes",
                "config",
            )
            .expanduser()
            .as_posix(),
        }[FeatureVolumeType.CONTAINED],
        "TELEPORT_DATA": {
            FeatureVolumeType.CONTAINED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                "{LANDSCAPE}",
                f"{GROUP}__{'__'.join(KEY)}",
                "volumes",
                "data",
            )
            .expanduser()
            .as_posix(),
            FeatureVolumeType.SHARED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                ".shared_volumes",
                f"{GROUP}__{'__'.join(KEY)}",
                "volumes",
                "data",
            )
            .expanduser()
            .as_posix(),
        }[FeatureVolumeType.CONTAINED],
        "ACME_SH_DIR": {
            FeatureVolumeType.CONTAINED: None,
            FeatureVolumeType.SHARED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                ".acme.sh",
            )
            .expanduser()
            .as_posix(),
        }[FeatureVolumeType.SHARED],
        "TELEPORT_CERT": {
            #################################################################
            # Certificates directory
            #################################################################
            FeatureVolumeType.CONTAINED: None,
            FeatureVolumeType.SHARED: pathlib.Path(
                "{DOT_LANDSCAPES}",
                ".acme.sh",
                "certs",
            )
            .expanduser()
            .as_posix(),
        }[FeatureVolumeType.SHARED],
        # Todo:
        #  - [x] find a dynamic way to fetch all services with the correct ports etc.
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
