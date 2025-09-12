import copy
import json
import pathlib
from typing import Any, Generator

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)
from OpenStudioLandscapes.engine.common_assets.compose import get_compose
from OpenStudioLandscapes.engine.common_assets.constants import get_constants
from OpenStudioLandscapes.engine.common_assets.docker_compose_graph import (
    get_docker_compose_graph,
)
from OpenStudioLandscapes.engine.common_assets.docker_config import get_docker_config
from OpenStudioLandscapes.engine.common_assets.docker_config_json import (
    get_docker_config_json,
)
from OpenStudioLandscapes.engine.common_assets.env import get_env
from OpenStudioLandscapes.engine.common_assets.feature_out import get_feature_out
from OpenStudioLandscapes.engine.common_assets.group_in import get_group_in
from OpenStudioLandscapes.engine.common_assets.group_out import get_group_out
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *

from OpenStudioLandscapes.Teleport.constants import *

constants = get_constants(
    ASSET_HEADER=ASSET_HEADER,
)


docker_config = get_docker_config(
    ASSET_HEADER=ASSET_HEADER,
)


group_in = get_group_in(
    ASSET_HEADER=ASSET_HEADER,
    ASSET_HEADER_PARENT=ASSET_HEADER_BASE,
    input_name=str(GroupIn.BASE_IN),
)


env = get_env(
    ASSET_HEADER=ASSET_HEADER,
)


group_out = get_group_out(
    ASSET_HEADER=ASSET_HEADER,
)


docker_compose_graph = get_docker_compose_graph(
    ASSET_HEADER=ASSET_HEADER,
)


compose = get_compose(
    ASSET_HEADER=ASSET_HEADER,
)


feature_out = get_feature_out(
    ASSET_HEADER=ASSET_HEADER,
    feature_out_ins={
        "env": dict,
        "compose": dict,
        "group_in": dict,
    },
)


docker_config_json = get_docker_config_json(
    ASSET_HEADER=ASSET_HEADER,
)


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
    },
)
def compose_networks(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[dict[str, dict[str, dict[str, str]]]] | AssetMaterialization, None, None
]:

    compose_network_mode = ComposeNetworkMode(env["COMPOSE_NETWORK_MODE"])

    if compose_network_mode == ComposeNetworkMode.DEFAULT:
        docker_dict = {
            "networks": {
                "teleport": {
                    "name": "network_teleport",
                },
            },
        }

    else:
        docker_dict = {
            "network_mode": compose_network_mode.value,
        }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "compose_network_mode": MetadataValue.text(compose_network_mode.value),
            "docker_dict": MetadataValue.md(
                f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
            ),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
    },
    description="",
)
def teleport_yaml(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
    """
    """

    service_name = "teleport"
    # container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
    host_name = ".".join([service_name, env["ROOT_DOMAIN"]])

    # Reference:
    # #
    # # A Sample Teleport configuration file.
    # #
    # # Things to update:
    # #  1. license.pem: Retrieve a license from your Teleport account https://teleport.sh
    # #     if you are an Enterprise customer.
    # #
    # version: v3
    # teleport:
    #   nodename: teleport.farm.evil
    #   data_dir: /var/lib/teleport
    #   join_params:
    #     token_name: ""
    #     method: token
    #   log:
    #     output: stderr
    #     severity: INFO
    #     format:
    #       output: text
    #   ca_pin: ""
    #   diag_addr: ""
    # auth_service:
    #   enabled: "yes"
    #   listen_addr: 0.0.0.0:3025
    #   proxy_listener_mode: multiplex
    # ssh_service:
    #   enabled: "no"
    # proxy_service:
    #   enabled: "yes"
    #   https_keypairs: []
    #   https_keypairs_reload_interval: 0s
    #   acme: {}

    # Helpful commands:
    # - docker exec teleport--<landscape_id> tctl --help
    # - docker exec teleport--<landscape_id> teleport --help
    # - docker exec -ti teleport--<landscape_id> busybox sh

    # Create User:
    # docker ps
    # TELEPORT_CONTAINER_ID_OR_NAME="a3a99558b9bb0a63cadf6da64e1ff8d24a7bbf5d50883e18dbb312afc13e07bc"
    # docker exec ${TELEPORT_CONTAINER_ID_OR_NAME} tctl users add admin --roles=editor,access --logins=root,ubuntu,ec2-user

    # Invite requires phone with camera for 2FA

    # Create Kitsu (for example) web service
    # go to kitsu and enter container
    # https://goteleport.com/docs/installation/linux/#package-repositories
    # sudo apt get install -y nano
    # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=http://192.168.178.195:4545/ --roles=app --token=<token> --proxy=192.168.178.195:3080 --data-dir=$HOME/.config/teleport
    # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=http://kitsu.farm.evil:4545/ --roles=app --token=<token> --proxy=teleport.farm.evil:3080 --data-dir=$HOME/.config/teleport
    # teleport start --insecure --config="/root/.config/teleport/app_config.yaml"

    # Maybe:
    # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=http://kitsu.farm.evil:4545/ --roles=app --token=2820bac86abcb41d37878c88c82bbea8 --proxy=192.168.178.195:3080 --data-dir=$HOME/.config/teleport
    # teleport start --config="/root/.config/teleport/app_config.yaml" --insecure
    # maybe kitsu needs to be inside

    # OK:
    # Kitsu__Kitsu/Kitsu__DOCKER_COMPOSE/docker_compose/docker-compose.yml
    #     networks:
    #     - kitsu
    #     - teleport
    # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=http://kitsu.farm.evil/ --roles=app --token=002fdc78bf747a4d26c6f5c47627e86c --proxy=teleport.farm.evil:3080 --data-dir=$HOME/.config/teleport
    # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=http://kitsu.farm.evil:4545 --roles=app --token=bc705a5dfaa7cfcac15399c2abb554ce --proxy=teleport.farm.evil:3080 --data-dir=$HOME/.config/teleport
    # teleport start --config="/root/.config/teleport/app_config.yaml" --insecure
    # 127.0.0.1       teleport.farm.evil
    # 127.0.0.1       kitsu.farm.evil
    # 127.0.0.1       kitsu.teleport.farm.evil

    teleport_yaml_dict = {
        "version": "v3",
        # https://github.com/gravitational/teleport/discussions/25318
        "teleport": {
            "nodename": host_name,
            "data_dir": "/var/lib/teleport",
            "join_params": {
                "token_name": "",
                "method": [
                    "token",
                    "github",
                ][1],
            },
            "log": {
                "output": "stderr",
                "severity": "INFO",
                "format": {
                    "output": "text"
                }
            },
            "ca_pin": "",
            "diag_addr": ""
        },
        "auth_service": {
            "enabled": "yes",
            # "listen_addr": f"0.0.0.0:{env['PROXY_SERVICE_AGENTS_PORT_CONTAINER']}",
            "listen_addr": "0.0.0.0:3025",
            "proxy_listener_mode": "multiplex"
        },
        "ssh_service": {
            "enabled": "no"
        },
        "proxy_service": {
            "enabled": "yes",
            "https_keypairs": [],
            "https_keypairs_reload_interval": "0s",
            "acme": {},
            "listen_addr": "0.0.0.0:3023",
            "web_listen_addr": "0.0.0.0:3080",
            "tunnel_listen_addr": "0.0.0.0:3024",
            "public_addr": "teleport.farm.evil:3080",
        },
    }

    teleport_yaml_script = pathlib.Path(env["TELEPORT_CONFIG"], "teleport.yaml")
    teleport_yaml_script.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    teleport_yaml_script.parent.mkdir(parents=True, exist_ok=True)

    teleport_yaml_ = yaml.dump(teleport_yaml_dict)

    with open(
        file=teleport_yaml_script,
        mode="w",
        encoding="utf-8",
    ) as fo:
        fo.write(teleport_yaml_)

    yield Output(teleport_yaml_script)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(
                teleport_yaml_script
            ),
            "teleport_yaml_dict": MetadataValue.md(
                f"```shell\n{teleport_yaml_dict}\n```"
            ),
            "teleport_yaml_": MetadataValue.md(
                f"```yaml\n{teleport_yaml_}\n```"
            )
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
        "compose_networks": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_networks"]),
        ),
        "teleport_yaml": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "teleport_yaml"]),
        ),
    },
)
def compose_teleport(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    compose_networks: dict,  # pylint: disable=redefined-outer-name
    teleport_yaml: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
    """ """

    network_dict = {}
    ports_dict = {}

    if "networks" in compose_networks:
        network_dict = {"networks": list(compose_networks.get("networks", {}).keys())}
        ports_dict = {
            "ports": [
                # # f"{env['ALL_CLIENTS_PORT_HOST']}:{env['ALL_CLIENTS_PORT_CONTAINER']}",
                # f"{env['PROXY_SERVICE_AGENTS_PORT_HOST']}:{env['PROXY_SERVICE_AGENTS_PORT_CONTAINER']}",
                # f"{env['WEB_UI_PORT_HOST']}:{env['WEB_UI_PORT_CONTAINER']}",
                "3025:3025",
                "3023:3023",
                "3080:3080",
                "3024:3024",
            ]
        }
    elif "network_mode" in compose_networks:
        network_dict = {"network_mode": compose_networks.get("network_mode")}

    teleport_data = pathlib.Path(env["TELEPORT_DATA"])
    teleport_data.mkdir(
        parents=True,
        exist_ok=True,
    )

    volumes_dict = {
        "volumes": [
            f"{teleport_yaml.parent.as_posix()}:/etc/teleport:rw",
            f"{teleport_data.as_posix()}:/var/lib/teleport:rw",
        ],
    }

    # For portability, convert absolute volume paths to relative paths

    _volume_relative = []

    for v in volumes_dict["volumes"]:

        host, container = v.split(":", maxsplit=1)

        volume_dir_host_rel_path = get_relative_path_via_common_root(
            context=context,
            path_src=pathlib.Path(env["DOCKER_COMPOSE"]),
            path_dst=pathlib.Path(host),
            path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
        )

        _volume_relative.append(
            f"{volume_dir_host_rel_path.as_posix()}:{container}",
        )

    volumes_dict = {
        "volumes": [
            *_volume_relative,
        ],
    }

    command = []

    service_name = "teleport"
    container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
    host_name = ".".join([service_name, env["ROOT_DOMAIN"]])

    docker_dict = {
        "services": {
            service_name: {
                "container_name": container_name,
                "hostname": host_name,
                "domainname": env.get("ROOT_DOMAIN"),
                # "mac_address": ":".join(re.findall(r"..", env["HOST_ID"])),
                "restart": "always",
                "image": env["DOCKER_IMAGE"],
                # https://docs.docker.com/reference/compose-file/services/#extra_hosts
                # docker exec ${TELEPORT_CONTAINER_ID_OR_NAME} cat /etc/hosts
                # 127.0.0.1       localhost
                # ::1     localhost ip6-localhost ip6-loopback
                # fe00::  ip6-localnet
                # ff00::  ip6-mcastprefix
                # ff02::1 ip6-allnodes
                # ff02::2 ip6-allrouters
                # 172.17.0.1      teleport.cloud-ip.cc
                "extra_hosts":[
                    "teleport.cloud-ip.cc:host-gateway",
                ],
                **copy.deepcopy(volumes_dict),
                **copy.deepcopy(network_dict),
                **copy.deepcopy(ports_dict),
                # "environment": {
                # },
                # "healthcheck": {
                # },
                # "command": command,
                "entrypoint": [
                #      - "/usr/bin/dumb-init"
                #      - "--help"
                    "/usr/bin/dumb-init",
                    "/usr/local/bin/teleport",
                    "start",
                    "-c",
                    "/etc/teleport/teleport.yaml",
                    "--insecure",
                ]
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "compose_teleport": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_teleport"]),
        ),
    },
)
def compose_maps(
    context: AssetExecutionContext,
    **kwargs,  # pylint: disable=redefined-outer-name
) -> Generator[Output[list[dict]] | AssetMaterialization, None, None]:

    ret = list(kwargs.values())

    context.log.info(ret)

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={},
)
def cmd_extend(
    context: AssetExecutionContext,
) -> Generator[Output[list[Any]] | AssetMaterialization | Any, Any, None]:

    ret = []

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={},
)
def cmd_append(
    context: AssetExecutionContext,
) -> Generator[Output[dict[str, list[Any]]] | AssetMaterialization | Any, Any, None]:

    ret = {"cmd": [], "exclude_from_quote": []}

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )
