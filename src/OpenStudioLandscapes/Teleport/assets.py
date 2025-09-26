import copy
import json
import operator
import pathlib
import shlex
import shutil
from typing import Any, Generator, List, MutableMapping

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    EnvVar,
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
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.features import FEATURES
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
                "acmesh": {
                    "name": "network_acmesh",
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


ins, feature_ins = get_dynamic_ins(
    compose_scope_filter=FEATURES["OpenStudioLandscapes-Teleport"]["compose_scope"],
    imported_features=IMPORTED_FEATURES,
    operator=operator.ne,
)


@asset(
    **ASSET_HEADER,
    ins={
        **feature_ins,
    },
)
def fetch_services(
    context: AssetExecutionContext,
    **kwargs,
) -> Generator[
    Output[MutableMapping[str, List[MutableMapping[str, List]]]] | AssetMaterialization,
    None,
    None,
]:
    """ """

    context.log.info(kwargs)

    envs_feature = {}

    for k, v in kwargs.items():
        # remove
        # - env_base
        # - constants_base
        # - features
        # - docker_config
        # - docker_config_json
        # - compose
        # - compose_yaml
        # - group_in
        # from kwargs dicts
        for d in [
            "env_base",
            "constants_base",
            "features",
            "docker_config",
            "docker_config_json",
            "compose",
            "compose_yaml",
            "group_in",
        ]:
            kwargs[k].pop(d)

        teleport = {
            "teleport_host": v.get("env", {}).get("TELEPORT_ENTRY_POINT_HOST", ""),
            "teleport_port": v.get("env", {}).get("TELEPORT_ENTRY_POINT_PORT", ""),
            "teleport_domain_lan": v.get("env", {}).get(
                "OPENSTUDIOLANDSCAPES__DOMAIN_LAN", ""
            ),
            "teleport_domain_wan": v.get("env", {}).get(
                "OPENSTUDIOLANDSCAPES__DOMAIN_WAN", ""
            ),
        }

        if not all(
            [
                bool(teleport["teleport_host"]),
                bool(teleport["teleport_port"]),
            ]
        ):
            # only add the service to the teleport.yaml if
            # both teleport_host and teleport_port are specified
            # Todo: for now ok
            continue

        teleport_expanded = expand_dict_vars(
            dict_to_expand=teleport,
            kv=v["env"],
        )

        envs_feature[k] = copy.deepcopy(teleport_expanded)

    yield Output(envs_feature)

    kwargs_serialized = copy.deepcopy(kwargs)

    serialize_dict(
        context=context,
        d=kwargs_serialized,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(envs_feature),
            **metadatavalues_from_dict(
                context=context,
                d_serialized=kwargs_serialized,
            ),
        },
    )


# @asset(
#     **ASSET_HEADER,
#     ins={
#         "env": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
#         ),
#     },
# )
# def letsencrypt(
#     context: AssetExecutionContext,
#     env: dict,  # pylint: disable=redefined-outer-name
# ) -> Generator[
#     Output[dict[str, dict[str, dict[str, str]]]] | AssetMaterialization, None, None
# ]:
#
#     compose_network_mode = ComposeNetworkMode(env["COMPOSE_NETWORK_MODE"])
#
#     if compose_network_mode == ComposeNetworkMode.DEFAULT:
#         docker_dict = {
#             "networks": {
#                 "teleport": {
#                     "name": "network_teleport",
#                 },
#             },
#         }
#
#     else:
#         docker_dict = {
#             "network_mode": compose_network_mode.value,
#         }
#
#     docker_yaml = yaml.dump(docker_dict)
#
#     yield Output(docker_dict)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
#             "compose_network_mode": MetadataValue.text(compose_network_mode.value),
#             "docker_dict": MetadataValue.md(
#                 f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
#             ),
#             "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
#         },
#     )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
    },
)
def certificates(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[list[dict]] | AssetMaterialization, None, None]:

    acme_sh_dir = pathlib.Path(env["ACME_SH_DIR"])
    cert_dirs = []

    for cert_dir in acme_sh_dir.iterdir():
        tld = cert_dir.name
        context.log.warning(tld)
        dir_ = pathlib.Path("certs", f"{tld}_ecc")
        fullchain = "fullchain.cer"
        key = f"{tld}.key"
        cert_dir_dict = {
            "certs_root": cert_dir.as_posix(),
            "tld": tld,
            "certs_subdir": dir_.as_posix(),
            "fullchain": fullchain,  # aka cert_file
            "key": key,  # aka key_file
        }
        context.log.warning(cert_dir)
        cert_dirs.append(cert_dir_dict)

    yield Output(cert_dirs)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(cert_dirs),
        },
    )


@asset(
    **ASSET_HEADER,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        ),
        "certificates": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "certificates"]),
        ),
        "fetch_services": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "fetch_services"]),
        ),
    },
    description="",
)
def teleport_yaml(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    certificates: list[dict],  # pylint: disable=redefined-outer-name
    fetch_services: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
    """ """

    service_name = SERVICE_NAME
    # container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
    host_name_lan = ".".join([service_name, env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]])
    host_name_wan = ".".join([service_name, env["OPENSTUDIOLANDSCAPES__DOMAIN_WAN"]])

    host_names = [
        # Todo
        #  - [ ] separate lan domain(s) and wan domain(s)
        # the order matters here.
        # first: wan, secondary wan etc.
        # then: lan
        host_name_wan,
        host_name_lan,
    ]

    host_name = host_names[0]

    app_default_dict: dict = {
        "name": "",
        # for ayon specifically, uri could be:
        # "uri": "http://localhost:5005/",
        # "uri": "http://server.farm.evil:5005/",
        # "uri": "192.168.178.195:5005/",
        "uri": "",
        "insecure_skip_verify": False,
        "public_addr": "",
        "use_any_proxy_public_addr": False,
        "rewrite": {
            "redirect": [
                "localhost",
            ],
        },
    }

    apps: list[dict] = []

    for feature, settings_teleport in fetch_services.items():
        app_ = copy.deepcopy(app_default_dict)
        app_["name"] = settings_teleport["teleport_host"]
        app_["uri"] = f"http://localhost:{settings_teleport['teleport_port']}/"
        app_[
            "public_addr"
        ] = f"{settings_teleport['teleport_host']}.{service_name}.{settings_teleport['teleport_domain_wan']}"
        app_["rewrite"]["redirect"].append(
            f"{settings_teleport['teleport_host']}.{settings_teleport['teleport_domain_lan']}"
        )

        apps.append(app_)

    publish_openstudiolandscapes_dagster = True

    if publish_openstudiolandscapes_dagster:
        service = "openstudiolandscapes-dagster"
        app_ = copy.deepcopy(app_default_dict)
        app_["name"] = service
        app_["uri"] = f"http://localhost:3000/"
        app_["public_addr"] = f"{service}.{service_name}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}"
        app_["rewrite"]["redirect"].append(f"{service}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_LAN').get_value()}")

        apps.append(app_)

    publish_openstudiolandscapes_harbor = True

    if publish_openstudiolandscapes_harbor:
        service = "openstudiolandscapes-harbor"
        app_ = copy.deepcopy(app_default_dict)
        app_["name"] = service
        app_["uri"] = f"http://localhost:80/"
        app_["public_addr"] = f"{service}.{service_name}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}"
        app_["rewrite"]["redirect"].append(f"{service}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_LAN').get_value()}")

        apps.append(app_)

    # publish_openstudiolandscapes_pihole = False
    #
    # if publish_openstudiolandscapes_pihole:
    #     service = "openstudiolandscapes-pihole"
    #     app_ = copy.deepcopy(app_default_dict)
    #     app_["name"] = service
    #     app_["uri"] = f"http://localhost:80/"
    #     app_["public_addr"] = f"{service}.{service_name}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}"
    #     app_["rewrite"]["redirect"].append(f"{service}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_LAN').get_value()}")
    #
    #     apps.append(app_)

    # publish_openstudiolandscapes_jellyfin = False
    #
    # if publish_openstudiolandscapes_jellyfin:
    #     service = "openstudiolandscapes-jellyfin"
    #     app_ = copy.deepcopy(app_default_dict)
    #     app_["name"] = service
    #     app_["uri"] = f"http://pi-hole.farm.evil:80/"
    #     app_["public_addr"] = f"{service}.{service_name}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}"
    #     app_["rewrite"]["redirect"].append(f"{service}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_LAN').get_value()}")
    #
    #     apps.append(app_)

    # publish_openstudiolandscapes_transmission = False
    #
    # if publish_openstudiolandscapes_transmission:
    #     service = "openstudiolandscapes-transmission"
    #     app_ = copy.deepcopy(app_default_dict)
    #     app_["name"] = service
    #     app_["uri"] = f"http://transmission.farm.evil:9091/"
    #     app_["public_addr"] = f"{service}.{service_name}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}"
    #     app_["rewrite"]["redirect"].append(f"{service}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_LAN').get_value()}")
    #
    #     apps.append(app_)

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

    # Base prep:
    # Create Kitsu (for example) web service
    # go to kitsu and enter container
    #
    # Visit https://goteleport.com/docs/installation/linux/#package-repositories
    # and perform "Teleport Community Edition" Setup
    #
    # sudo apt install -y nano netcat
    #
    # go to Enroll a New Resource: Web Application
    # copy/paste (make sure to specify correct port in --app-uri
    # --app-name must be lower case)
    # i.e.
    # # using exposed port is not working yet...
    # # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=http://localhost:4545/ --roles=app --token=b7bfd56f9fc56bc8a7c0a2a336ba7d47 --proxy=teleport.evil-farmer.cloud-ip.cc:443 --data-dir=$HOME/.config/teleport
    # # But using the direct docker IP: BAM!
    # Todo:
    #  - [x] Try with local IP (wlp0s20f3,  192.168.178.195:4545) and exposed port
    #        $ nc -vz 192.168.178.195 4545
    #        Connection to 192.168.178.195 4545 port [tcp/*] succeeded!
    #  - [x] Try with hostname (kitsu.farm.evil:80) and exposed port
    #        $ nc -vz kitsu.farm.evil 80
    #        Connection to kitsu.farm.evil (172.20.0.2) 80 port [tcp/http] succeeded!
    #  - [x] Try with loopback IP (127.0.0.1:4545) and exposed port
    #        $ nc -vz 127.0.0.1 80
    #        Connection to 127.0.0.1 80 port [tcp/http] succeeded!
    #  - [x] Try with loopback IP (127.0.1.1:4545) and exposed port
    #        $ nc -vz 127.0.1.1 80
    #        Connection to 127.0.1.1 80 port [tcp/http] succeeded!
    #  - [ ] make sure teleport start runs automatically somewhere
    # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=http://172.25.0.2/ --roles=app --token=b7bfd56f9fc56bc8a7c0a2a336ba7d47 --proxy=teleport.evil-farmer.cloud-ip.cc:443 --data-dir=$HOME/.config/teleport
    # teleport start --config=$HOME/.config/teleport/app_config.yaml
    #
    # Teleport app service can run on any machine on the same network as kitsu, it seems.
    # That would mean that we can just run one single docker container where the teleport start service is running on
    # with multiple app_services
    # [x] works!
    # app_service:
    #   enabled: "yes"
    #   debug_app: false
    #   mcp_demo_server: false
    #   apps:
    #   - name: ayon
    #     uri: http://localhost:5005/
    #     public_addr: ""
    #     insecure_skip_verify: false
    #     use_any_proxy_public_addr: false
    #   - name: dagster
    #     uri: http://localhost:3003/
    #     public_addr: ""
    #     insecure_skip_verify: false
    #     use_any_proxy_public_addr: false
    #   - name: kitsu
    #     uri: http://localhost:4545/
    #     public_addr: ""
    #     insecure_skip_verify: false
    #     use_any_proxy_public_addr: false
    #
    # Can the service also run on the same container like the proxy itself?
    # Same config?
    # [x] works!
    #
    # /etc/hosts is currently not empty.
    # Todo:
    #  - [ ] verify that it also works without hosts file
    #
    # Start over:
    # rm -rf ${HOME}/.config/teleport

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

    # next attempt
    # teleport configure --output=$HOME/.config/teleport/app_config.yaml --app-name=kitsu --app-uri=kitsu.evil-farmer.cloud-ip.cc:4545 --roles=app --token=37f06a14531de8b783ca7110b2483cab --proxy=teleport.evil-farmer.cloud-ip.cc:443 --data-dir=$HOME/.config/teleport
    # $ cat /root/.config/teleport/app_config.yaml
    # version: v3
    # teleport:
    #   nodename: kitsu.farm.evil
    #   data_dir: /root/.config/teleport
    #   join_params:
    #     token_name: 37f06a14531de8b783ca7110b2483cab
    #     method: token
    #   proxy_server: teleport.evil-farmer.cloud-ip.cc:443
    #   log:
    #     output: stderr
    #     severity: INFO
    #     format:
    #       output: text
    #   ca_pin: ""
    #   diag_addr: ""
    # auth_service:
    #   enabled: "no"
    # ssh_service:
    #   enabled: "no"
    # proxy_service:
    #   enabled: "no"
    #   https_keypairs: []
    #   https_keypairs_reload_interval: 0s
    #   acme: {}
    # app_service:
    #   enabled: "yes"
    #   debug_app: false
    #   mcp_demo_server: false
    #   apps:
    #   - name: kitsu
    #     uri: http://kitsu.farm.evil:4545
    #     public_addr: "kitsu.evil-farmer.cloud-ip.cc"
    #     insecure_skip_verify: false
    #     use_any_proxy_public_addr: false
    #
    # teleport start --config="/root/.config/teleport/app_config.yaml" --insecure

    https_keypairs = []

    for cert_dict in certificates:
        https_keypairs.append(
            {
                "cert_file": f"/{cert_dict['certs_subdir']}/{cert_dict['fullchain']}",
                "key_file": f"/{cert_dict['certs_subdir']}/{cert_dict['key']}",
            }
        )

    teleport_yaml_dict = {
        "version": "v3",
        # https://github.com/gravitational/teleport/discussions/25318
        "teleport": {
            # https://goteleport.com/docs/reference/deployment/config/#instance-wide-settings
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
                "format": {"output": "text"},
            },
            "ca_pin": "",
            "diag_addr": "",
        },
        "auth_service": {
            # https://goteleport.com/docs/reference/deployment/config/#auth-service
            "enabled": "yes",
            # "listen_addr": f"0.0.0.0:{env['PROXY_SERVICE_AGENTS_PORT_CONTAINER']}",
            "listen_addr": f"0.0.0.0:3025",
            "proxy_listener_mode": "multiplex",
        },
        # Server Access
        # https://goteleport.com/docs/enroll-resources/server-access/getting-started/
        "ssh_service": {
            # https://goteleport.com/docs/reference/deployment/config/#ssh-service
            "enabled": False,
            # "listen_addr": f"0.0.0.0:{env['LISTEN_ADDRESS_HOST']}",
            # # "listen_addr": f"192.168.178.195:22",
            # "public_addr": [
            #     # https://goteleport.com/docs/zero-trust-access/deploy-a-cluster/separate-proxy-service-endpoints/
            #     # External FQDN(s)
            #     *[f"{i}:{env['LISTEN_ADDRESS_HOST']}" for i in host_names]
            #     # f"{service_name}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}:{env['WEB_UI_PORT_CONTAINER']}",
            #     # f"{service_name}.openstudiolandscapes.cloud-ip.cc:{env['WEB_UI_PORT_CONTAINER']}",
            #     # Internal FQDN
            #     # f"{host_name}:{env['WEB_UI_PORT_CONTAINER']}",
            # ],
            # "ssh_file_copy": True,
        },
        "proxy_service": {
            # https://goteleport.com/docs/reference/deployment/config/#proxy-service
            "enabled": True,
            # Basic structure of https_keypairs:
            # [{
            #     "key_file": "/certs/evil-farmer.cloud-ip.cc_ecc/evil-farmer.cloud-ip.cc.key",
            #     "cert_file": "/certs/evil-farmer.cloud-ip.cc_ecc/fullchain.cer",
            # }],
            "https_keypairs": https_keypairs,
            "https_keypairs_reload_interval": "120s",
            # acme uses TLS_ALPN-01 challenge and does not seem to be able to handle
            # DNS-01 challenges nor can we specify custom domains manually so this
            # is a bit crippled.
            # https://letsencrypt.org/docs/challenge-types/
            # We use nox for now and specify the mounted https_keypairs.
            # "acme": {
            #     # Get an automatic certificate from Letsencrypt.org using ACME via
            #     # TLS_ALPN-01 challenge.
            #     # When using ACME, the 'proxy_service' must be publicly accessible over
            #     # port 443.
            #     # Also set using the CLI command:
            #     # 'teleport configure --acme --acme-email=email@example.com \
            #     # --cluster-name=tele.example.com -o file'
            #     # This should NOT be enabled in a highly available Teleport deployment
            #     # Using in HA can lead to too many failed authorizations and a lock-up
            #     # of the ACME process (https://letsencrypt.org/docs/failed-validation-limit/)
            #     "enabled": "yes",
            #     "email": EnvVar("OPENSTUDIOLANDSCAPES__DOMAIN_EMAIL").get_value()
            # },
            "listen_addr": f"0.0.0.0:{env['ALL_CLIENTS_PORT_CONTAINER']}",
            "web_listen_addr": f"0.0.0.0:{env['WEB_UI_PORT_CONTAINER']}",
            "tunnel_listen_addr": "0.0.0.0:3024",
            "public_addr": [
                # https://goteleport.com/docs/zero-trust-access/deploy-a-cluster/separate-proxy-service-endpoints/
                # External FQDN(s)
                *[f"{i}:{env['WEB_UI_PORT_CONTAINER']}" for i in host_names]
                # f"{service_name}.{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}:{env['WEB_UI_PORT_CONTAINER']}",
                # f"{service_name}.openstudiolandscapes.cloud-ip.cc:{env['WEB_UI_PORT_CONTAINER']}",
                # Internal FQDN
                # f"{host_name}:{env['WEB_UI_PORT_CONTAINER']}",
            ],
        },
        "app_service": {
            # https://goteleport.com/docs/reference/deployment/config/#application-service
            "enabled": bool(apps),
            "debug_app": False,
            "mcp_demo_server": False,
            "apps": apps,
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
            "__".join(context.asset_key.path): MetadataValue.path(teleport_yaml_script),
            "teleport_yaml_dict": MetadataValue.md(
                f"```shell\n{teleport_yaml_dict}\n```"
            ),
            "teleport_yaml_": MetadataValue.md(f"```yaml\n{teleport_yaml_}\n```"),
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
        "certificates": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "certificates"]),
        ),
    },
)
def compose_teleport(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    compose_networks: dict,  # pylint: disable=redefined-outer-name
    teleport_yaml: pathlib.Path,  # pylint: disable=redefined-outer-name
    certificates: list[dict],  # pylint: disable=redefined-outer-name
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

    for cert_dict in certificates:
        volumes_dict["volumes"].extend(
            [
                f"{cert_dict['certs_root']}/{cert_dict['certs_subdir']}/{cert_dict['fullchain']}:/{cert_dict['certs_subdir']}/{cert_dict['fullchain']}:ro",
                f"{cert_dict['certs_root']}/{cert_dict['certs_subdir']}/{cert_dict['key']}:/{cert_dict['certs_subdir']}/{cert_dict['key']}:ro",
            ]
        )

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

    service_name = SERVICE_NAME
    container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
    host_name = ".".join([service_name, env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]])

    docker_dict = {
        "services": {
            service_name: {
                "container_name": container_name,
                "hostname": host_name,
                "domainname": env.get("OPENSTUDIOLANDSCAPES__DOMAIN_LAN"),
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
                # "extra_hosts":[
                #     "teleport.cloud-ip.cc:host-gateway",
                # ],
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
                    # "--insecure",
                ],
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


# @asset(
#     **ASSET_HEADER,
#     ins={
#         "env": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
#         ),
#         "compose_networks": AssetIn(
#             AssetKey([*ASSET_HEADER["key_prefix"], "compose_networks"]),
#         ),
#         # "teleport_yaml": AssetIn(
#         #     AssetKey([*ASSET_HEADER["key_prefix"], "teleport_yaml"]),
#         # ),
#     },
# )
# def compose_acmesh(
#     context: AssetExecutionContext,
#     env: dict,  # pylint: disable=redefined-outer-name
#     compose_networks: dict,  # pylint: disable=redefined-outer-name
#     # teleport_yaml: pathlib.Path,  # pylint: disable=redefined-outer-name
# ) -> Generator[Output[dict] | AssetMaterialization, None, None]:
#     """
#     https://github.com/acmesh-official/acme.sh/wiki/Run-acme.sh-in-docker#3-run-acmesh-as-a-docker-daemon
#     ```
#     docker exec acme.sh --help
#     # Register account
#     acme.sh --register-account -m michimussato@gmail.com
#     # validation type http-01:
#     acme.sh --issue -d openstudiolandscapes.mywire.org -d teleport.openstudiolandscapes.mywire.org --standalone
#     # Todo:
#     # validation type dns-01:
#     acme.sh --issue -d openstudiolandscapes.mywire.org -d *.openstudiolandscapes.mywire.org --standalone
#     ```
#
#     ```
#     # acme.sh --help
#     https://github.com/acmesh-official/acme.sh
#     v3.1.2
#     Usage: acme.sh <command> ... [parameters ...]
#     Commands:
#       -h, --help               Show this help message.
#       -v, --version            Show version info.
#       --install                Install acme.sh to your system.
#       --uninstall              Uninstall acme.sh, and uninstall the cron job.
#       --upgrade                Upgrade acme.sh to the latest code from https://github.com/acmesh-official/acme.sh.
#       --issue                  Issue a cert.
#       --deploy                 Deploy the cert to your server.
#       -i, --install-cert       Install the issued cert to Apache/nginx or any other server.
#       -r, --renew              Renew a cert.
#       --renew-all              Renew all the certs.
#       --revoke                 Revoke a cert.
#       --remove                 Remove the cert from list of certs known to acme.sh.
#       --list                   List all the certs.
#       --info                   Show the acme.sh configs, or the configs for a domain with [-d domain] parameter.
#       --to-pkcs12              Export the certificate and key to a pfx file.
#       --to-pkcs8               Convert to pkcs8 format.
#       --sign-csr               Issue a cert from an existing csr.
#       --show-csr               Show the content of a csr.
#       -ccr, --create-csr       Create CSR, professional use.
#       --create-domain-key      Create an domain private key, professional use.
#       --update-account         Update account info.
#       --register-account       Register account key.
#       --deactivate-account     Deactivate the account.
#       --create-account-key     Create an account private key, professional use.
#       --install-cronjob        Install the cron job to renew certs, you don't need to call this. The 'install' command can automatically install the cron job.
#       --uninstall-cronjob      Uninstall the cron job. The 'uninstall' command can do this automatically.
#       --cron                   Run cron job to renew all the certs.
#       --set-notify             Set the cron notification hook, level or mode.
#       --deactivate             Deactivate the domain authz, professional use.
#       --set-default-ca         Used with '--server', Set the default CA to use.
#                                See: https://github.com/acmesh-official/acme.sh/wiki/Server
#       --set-default-chain      Set the default preferred chain for a CA.
#                                See: https://github.com/acmesh-official/acme.sh/wiki/Preferred-Chain
#
#
#     Parameters:
#       -d, --domain <domain.tld>         Specifies a domain, used to issue, renew or revoke etc.
#       --challenge-alias <domain.tld>    The challenge domain alias for DNS alias mode.
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/DNS-alias-mode
#
#       --domain-alias <domain.tld>       The domain alias for DNS alias mode.
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/DNS-alias-mode
#
#       --preferred-chain <chain>         If the CA offers multiple certificate chains, prefer the chain with an issuer matching this Subject Common Name.
#                                           If no match, the default offered chain will be used. (default: empty)
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/Preferred-Chain
#
#       --valid-to    <date-time>         Request the NotAfter field of the cert.
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/Validity
#       --valid-from  <date-time>         Request the NotBefore field of the cert.
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/Validity
#
#       -f, --force                       Force install, force cert renewal or override sudo restrictions.
#       --staging, --test                 Use staging server, for testing.
#       --debug [0|1|2|3]                 Output debug info. Defaults to 2 if argument is omitted.
#       --output-insecure                 Output all the sensitive messages.
#                                           By default all the credentials/sensitive messages are hidden from the output/debug/log for security.
#       -w, --webroot <directory>         Specifies the web root folder for web root mode.
#       --standalone                      Use standalone mode.
#       --alpn                            Use standalone alpn mode.
#       --stateless                       Use stateless mode.
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/Stateless-Mode
#
#       --apache                          Use Apache mode.
#       --dns [dns_hook]                  Use dns manual mode or dns api. Defaults to manual mode when argument is omitted.
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/dnsapi
#
#       --dnssleep <seconds>              The time in seconds to wait for all the txt records to propagate in dns api mode.
#                                           It's not necessary to use this by default, acme.sh polls dns status by DOH automatically.
#       -k, --keylength <bits>            Specifies the domain key length: 2048, 3072, 4096, 8192 or ec-256, ec-384, ec-521.
#       -ak, --accountkeylength <bits>    Specifies the account key length: 2048, 3072, 4096
#       --log [file]                      Specifies the log file. Defaults to "/acme.sh/acme.sh.log" if argument is omitted.
#       --log-level <1|2>                 Specifies the log level, default is 2.
#       --syslog <0|3|6|7>                Syslog level, 0: disable syslog, 3: error, 6: info, 7: debug.
#       --eab-kid <eab_key_id>            Key Identifier for External Account Binding.
#       --eab-hmac-key <eab_hmac_key>     HMAC key for External Account Binding.
#
#
#       These parameters are to install the cert to nginx/Apache or any other server after issue/renew a cert:
#
#       --cert-file <file>                Path to copy the cert file to after issue/renew.
#       --key-file <file>                 Path to copy the key file to after issue/renew.
#       --ca-file <file>                  Path to copy the intermediate cert file to after issue/renew.
#       --fullchain-file <file>           Path to copy the fullchain cert file to after issue/renew.
#       --reloadcmd <command>             Command to execute after issue/renew to reload the server.
#
#       --server <server_uri>             ACME Directory Resource URI. (default: https://acme.zerossl.com/v2/DV90)
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/Server
#
#       --accountconf <file>              Specifies a customized account config file.
#       --home <directory>                Specifies the home dir for acme.sh.
#       --cert-home <directory>           Specifies the home dir to save all the certs.
#       --config-home <directory>         Specifies the home dir to save all the configurations.
#       --useragent <string>              Specifies the user agent string. it will be saved for future use too.
#       -m, --email <email>               Specifies the account email, only valid for the '--install' and '--update-account' command.
#       --accountkey <file>               Specifies the account key path, only valid for the '--install' command.
#       --days <ndays>                    Specifies the days to renew the cert when using '--issue' command. The default value is 60 days.
#       --httpport <port>                 Specifies the standalone listening port. Only valid if the server is behind a reverse proxy or load balancer.
#       --tlsport <port>                  Specifies the standalone tls listening port. Only valid if the server is behind a reverse proxy or load balancer.
#       --local-address <ip>              Specifies the standalone/tls server listening address, in case you have multiple ip addresses.
#       --listraw                         Only used for '--list' command, list the certs in raw format.
#       -se, --stop-renew-on-error        Only valid for '--renew-all' command. Stop if one cert has error in renewal.
#       --insecure                        Do not check the server certificate, in some devices, the api server's certificate may not be trusted.
#       --ca-bundle <file>                Specifies the path to the CA certificate bundle to verify api server's certificate.
#       --ca-path <directory>             Specifies directory containing CA certificates in PEM format, used by wget or curl.
#       --no-cron                         Only valid for '--install' command, which means: do not install the default cron job.
#                                           In this case, the certs will not be renewed automatically.
#       --no-profile                      Only valid for '--install' command, which means: do not install aliases to user profile.
#       --no-color                        Do not output color text.
#       --force-color                     Force output of color text. Useful for non-interactive use with the aha tool for HTML E-Mails.
#       --ecc                             Specifies use of the ECC cert. Only valid for '--install-cert', '--renew', '--remove ', '--revoke',
#                                           '--deploy', '--to-pkcs8', '--to-pkcs12' and '--create-csr'.
#       --csr <file>                      Specifies the input csr.
#       --pre-hook <command>              Command to be run before obtaining any certificates.
#       --post-hook <command>             Command to be run after attempting to obtain/renew certificates. Runs regardless of whether obtain/renew succeeded or failed.
#       --renew-hook <command>            Command to be run after each successfully renewed certificate.
#       --deploy-hook <hookname>          The hook file to deploy cert
#       --extended-key-usage <string>     Manually define the CSR extended key usage value. The default is serverAuth,clientAuth.
#       --ocsp, --ocsp-must-staple        Generate OCSP-Must-Staple extension.
#       --always-force-new-domain-key     Generate new domain key on renewal. Otherwise, the domain key is not changed by default.
#       --auto-upgrade [0|1]              Valid for '--upgrade' command, indicating whether to upgrade automatically in future. Defaults to 1 if argument is omitted.
#       --listen-v4                       Force standalone/tls server to listen at ipv4.
#       --listen-v6                       Force standalone/tls server to listen at ipv6.
#       --openssl-bin <file>              Specifies a custom openssl bin location.
#       --use-wget                        Force to use wget, if you have both curl and wget installed.
#       --yes-I-know-dns-manual-mode-enough-go-ahead-please  Force use of dns manual mode.
#                                           See:  https://github.com/acmesh-official/acme.sh/wiki/dns-manual-mode
#
#       -b, --branch <branch>             Only valid for '--upgrade' command, specifies the branch name to upgrade to.
#       --notify-level <0|1|2|3>          Set the notification level:  Default value is 2.
#                                           0: disabled, no notification will be sent.
#                                           1: send notifications only when there is an error.
#                                           2: send notifications when a cert is successfully renewed, or there is an error.
#                                           3: send notifications when a cert is skipped, renewed, or error.
#       --notify-mode <0|1>               Set notification mode. Default value is 0.
#                                           0: Bulk mode. Send all the domain's notifications in one message(mail).
#                                           1: Cert mode. Send a message for every single cert.
#       --notify-hook <hookname>          Set the notify hook
#       --notify-source <server name>     Set the server name in the notification message
#       --revoke-reason <0-10>            The reason for revocation, can be used in conjunction with the '--revoke' command.
#                                           See: https://github.com/acmesh-official/acme.sh/wiki/revokecert
#
#       --password <password>             Add a password to exported pfx file. Use with --to-pkcs12.
#     ```
#     """
#
#     # shlex.join escapes $, so this won't work
#     # out of the box:
#     # acme_exe = "$(which acme.sh)"
#     acme_exe = "acme.sh"
#
#     cmd_register_account = [
#         acme_exe,
#         "--register-account",
#         "-m",
#         "michimussato@gmail.com"  # Todo: OPENSTUDIOLANDSCAPES__DOMAIN_EMAIL
#     ]
#
#     subdomains = [
#         "",  # for the top level domain
#         # each subdomain terminates with .
#         # for now, only http-01 challenge is supported
#         # but hopefully we can implement dns-1 challenge
#         # too for wildcards as in:
#         # "*.",
#         # "*.teleport.",
#         # etc.
#         "teleport.",
#     ]
#
#     all_domains = list(chain.from_iterable((j, f"{i}{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}") for i, j in zip_longest(subdomains, [], fillvalue="-d")))
#
#     # This command will only succeed on port 80
#     cmd_issue_certificate_http01 = [
#         acme_exe,
#         "--issue",
#         *all_domains,
#         "--standalone",
#     ]
#
#     network_dict = {}
#     ports_dict = {}
#
#     if "networks" in compose_networks:
#         network_dict = {"networks": list(compose_networks.get("networks", {}).keys())}
#         ports_dict = {
#             "ports": [
#                 # # # f"{env['ALL_CLIENTS_PORT_HOST']}:{env['ALL_CLIENTS_PORT_CONTAINER']}",
#                 # # f"{env['PROXY_SERVICE_AGENTS_PORT_HOST']}:{env['PROXY_SERVICE_AGENTS_PORT_CONTAINER']}",
#                 # # f"{env['WEB_UI_PORT_HOST']}:{env['WEB_UI_PORT_CONTAINER']}",
#                 # "3025:3025",
#                 # "3023:3023",
#                 # "3080:3080",
#                 # "3024:3024",
#                 "88:80"
#             ]
#         }
#     elif "network_mode" in compose_networks:
#         network_dict = {"network_mode": compose_networks.get("network_mode")}
#
#     teleport_certs = pathlib.Path(env["TELEPORT_CERT"])
#     teleport_certs.mkdir(
#         parents=True,
#         exist_ok=True,
#     )
#
#     volumes_dict = {
#         "volumes": [
#             f"{teleport_certs.as_posix()}:/acme.sh:rw",
#         ],
#     }
#
#     # For portability, convert absolute volume paths to relative paths
#
#     _volume_relative = []
#
#     for v in volumes_dict["volumes"]:
#
#         host, container = v.split(":", maxsplit=1)
#
#         volume_dir_host_rel_path = get_relative_path_via_common_root(
#             context=context,
#             path_src=pathlib.Path(env["DOCKER_COMPOSE"]),
#             path_dst=pathlib.Path(host),
#             path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
#         )
#
#         _volume_relative.append(
#             f"{volume_dir_host_rel_path.as_posix()}:{container}",
#         )
#
#     volumes_dict = {
#         "volumes": [
#             *_volume_relative,
#         ],
#     }
#
#     command = [
#         "daemon",
#     ]
#
#     service_name = "acme-sh"
#     container_name = "--".join([service_name, env.get("LANDSCAPE", "default")])
#     host_name = ".".join([service_name, env["OPENSTUDIOLANDSCAPES__DOMAIN_LAN"]])
#
#     docker_dict = {
#         "services": {
#             service_name: {
#                 "container_name": container_name,
#                 "hostname": host_name,
#                 "domainname": env.get("OPENSTUDIOLANDSCAPES__DOMAIN_LAN"),
#                 # "mac_address": ":".join(re.findall(r"..", env["HOST_ID"])),
#                 "restart": "no",
#                 "image": "docker.io/neilpang/acme.sh",
#                 "stdin_open": True,
#                 "tty": True,
#                 # https://docs.docker.com/reference/compose-file/services/#extra_hosts
#                 # docker exec ${TELEPORT_CONTAINER_ID_OR_NAME} cat /etc/hosts
#                 # 127.0.0.1       localhost
#                 # ::1     localhost ip6-localhost ip6-loopback
#                 # fe00::  ip6-localnet
#                 # ff00::  ip6-mcastprefix
#                 # ff02::1 ip6-allnodes
#                 # ff02::2 ip6-allrouters
#                 # 172.17.0.1      teleport.cloud-ip.cc
#                 # "extra_hosts":[
#                 #     "teleport.cloud-ip.cc:host-gateway",
#                 # ],
#                 **copy.deepcopy(volumes_dict),
#                 **copy.deepcopy(network_dict),
#                 **copy.deepcopy(ports_dict),
#                 # "environment": {
#                 # },
#                 # "healthcheck": {
#                 # },
#                 "command": command,
#                 # "entrypoint": [
#                 # #      - "/usr/bin/dumb-init"
#                 # #      - "--help"
#                 #     "/usr/bin/dumb-init",
#                 #     "/usr/local/bin/teleport",
#                 #     "start",
#                 #     "-c",
#                 #     "/etc/teleport/teleport.yaml",
#                 #     "--insecure",
#                 # ]
#             },
#         },
#     }
#
#     docker_yaml = yaml.dump(docker_dict)
#
#     yield Output(docker_dict)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
#             "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
#             # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
#             "cmd_register_account": MetadataValue.path(
#                 shlex.join(cmd_register_account)
#             ),
#             "cmd_issue_certificate_http01": MetadataValue.path(
#                 shlex.join(cmd_issue_certificate_http01)
#             ),
#             "certs_dir": MetadataValue.path(
#                 teleport_certs / f"{EnvVar('OPENSTUDIOLANDSCAPES__DOMAIN_WAN').get_value()}_ecc"
#             ),
#         },
#     )


@asset(
    **ASSET_HEADER,
    ins={
        "compose_teleport": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_teleport"]),
        ),
        # "compose_acmesh": AssetIn(
        #     AssetKey([*ASSET_HEADER["key_prefix"], "compose_acmesh"]),
        # ),
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


@asset(
    **ASSET_HEADER,
    ins={
        "compose_teleport": AssetIn(
            AssetKey([*ASSET_HEADER["key_prefix"], "compose_teleport"]),
        ),
    },
)
def cmd_create_teleport_admin(
    context: AssetExecutionContext,
    compose_teleport: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, list[Any]]] | AssetMaterialization | Any, Any, None]:
    """
    A fresh Teleport Docker instance comes with no admin user pre-configured.
    This command needs to be executed one time once the container is up.
    An invitation link will be printed which you'll have to follow.

    More info here (section "User Setup"):

    https://tomerklein.dev/setting-up-teleport-for-secure-server-access-d4d317c1c4ca
    """

    context.log.info(compose_teleport.keys())

    container_name = compose_teleport["services"]["teleport"]["container_name"]

    teleport_create_admin_cmd = [
        # i.e.: https://tomerklein.dev/setting-up-teleport-for-secure-server-access-d4d317c1c4ca
        shutil.which("docker"),
        "exec",
        container_name,
        "tctl",
        "users",
        "add",
        "admin",
        "--roles=editor,access",
        "--logins=root,ubuntu,ec2-user",
    ]

    yield Output(teleport_create_admin_cmd)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(
                shlex.join(teleport_create_admin_cmd)
            ),
        },
    )
