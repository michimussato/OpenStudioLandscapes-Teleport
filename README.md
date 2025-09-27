[![ Logo OpenStudioLandscapes ](https://github.com/michimussato/OpenStudioLandscapes/raw/main/media/images/logo128.png)](https://github.com/michimussato/OpenStudioLandscapes)

***

1. [Feature: OpenStudioLandscapes-Teleport](#feature-openstudiolandscapes-teleport)
   1. [Brief](#brief)
   2. [Requirements](#requirements)
   3. [Install](#install)
      1. [This Feature](#this-feature)
   4. [Add to OpenStudioLandscapes](#add-to-openstudiolandscapes)
   5. [Testing](#testing)
      1. [pre-commit](#pre-commit)
      2. [nox](#nox)
   6. [Variables](#variables)
      1. [Feature Configs](#feature-configs)
2. [Community](#community)
3. [Official Resources](#official-resources)
   1. [Teleport](#teleport)
      1. [Feature Matrix](#feature-matrix)
      2. [Requirements](#requirements)
      3. [Configuration](#configuration)
      4. [Usage](#usage)

***

This `README.md` was dynamically created with [OpenStudioLandscapesUtil-ReadmeGenerator](https://github.com/michimussato/OpenStudioLandscapesUtil-ReadmeGenerator).

***

# Feature: OpenStudioLandscapes-Teleport

## Brief

This is an extension to the OpenStudioLandscapes ecosystem. The full documentation of OpenStudioLandscapes is available [here](https://github.com/michimussato/OpenStudioLandscapes).

You feel like writing your own Feature? Go and check out the [OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template).

## Requirements

- `python-3.11`
- `OpenStudioLandscapes`

## Install

### This Feature

Clone this repository into `OpenStudioLandscapes/.features`:

```shell
# cd .features
git clone https://github.com/michimussato/OpenStudioLandscapes-Teleport.git
```

Create `venv`:

```shell
# cd .features/OpenStudioLandscapes-Teleport
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
```

Configure `venv`:

```shell
# cd .features/OpenStudioLandscapes-Teleport
pip install -e "../../[dev]"
pip install -e ".[dev]"
```

For more info see [VCS Support of pip](https://pip.pypa.io/en/stable/topics/vcs-support/).

## Add to OpenStudioLandscapes

Add the following code to `OpenStudioLandscapes.engine.features.FEATURES`:

```python
FEATURES.update(
    "OpenStudioLandscapes-Teleport": {
        "enabled": True|False,
        # - from ENVIRONMENT VARIABLE (.env):
        #   "enabled": get_bool_env("ENV_VAR")
        # - combined:
        #   "enabled": True|False or get_bool_env(
        #       "OPENSTUDIOLANDSCAPES__ENABLE_FEATURE_OPENSTUDIOLANDSCAPES_TELEPORT"
        #   )
        "module": "OpenStudioLandscapes.Teleport.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    }
)
```

## Testing

### pre-commit

- https://pre-commit.com
- https://pre-commit.com/hooks.html

```shell
pre-commit install
```

### nox

#### Generate Report

```shell
nox --no-error-on-missing-interpreters --report .nox/nox-report.json
```

#### Re-Generate this README

```shell
nox -v --add-timestamp --session readme
```

#### Generate Sphinx Documentation

```shell
nox -v --add-timestamp --session docs
```

#### pylint

```shell
nox -v --add-timestamp --session lint
```

##### pylint: disable=redefined-outer-name

- [`W0621`](https://pylint.pycqa.org/en/latest/user_guide/messages/warning/redefined-outer-name.html): Due to Dagsters way of piping arguments into assets.

#### SBOM

Acronym for Software Bill of Materials

```shell
nox -v --add-timestamp --session sbom
```

We create the following SBOMs:

- [`cyclonedx-bom`](https://pypi.org/project/cyclonedx-bom/)
- [`pipdeptree`](https://pypi.org/project/pipdeptree/) (Dot)
- [`pipdeptree`](https://pypi.org/project/pipdeptree/) (Mermaid)

SBOMs for the different Python interpreters defined in [`.noxfile.VERSIONS`](https://github.com/michimussato/OpenStudioLandscapes-Teleport/tree/main/noxfile.py) will be created in the [`.sbom`](https://github.com/michimussato/OpenStudioLandscapes-Teleport/tree/main/.sbom) directory of this repository.

- `cyclone-dx`
- `pipdeptree` (Dot)
- `pipdeptree` (Mermaid)

Currently, the following Python interpreters are enabled for testing:

- `python3.11`

## Variables

The following variables are being declared in `OpenStudioLandscapes.Teleport.constants` and are accessible throughout the [`OpenStudioLandscapes-Teleport`](https://github.com/michimussato/OpenStudioLandscapes-Teleport/tree/main/src/OpenStudioLandscapes/Teleport/constants.py) package.

| Variable           | Type   |
| :----------------- | :----- |
| `DOCKER_USE_CACHE` | `bool` |
| `ASSET_HEADER`     | `dict` |
| `FEATURE_CONFIGS`  | `dict` |
| `SERVICE_NAME`     | `str`  |

### Feature Configs

#### Feature Config: default

| Variable                                             | Type                 | Value                                                                   |
| :--------------------------------------------------- | :------------------- | :---------------------------------------------------------------------- |
| `DOCKER_USE_CACHE`                                   | `bool`               | `False`                                                                 |
| `HOSTNAME`                                           | `str`                | `teleport`                                                              |
| `TELEPORT_ENTRY_POINT_HOST`                          | `str`                | `{{HOSTNAME}}`                                                          |
| `TELEPORT_ENTRY_POINT_PORT`                          | `str`                | `{{WEB_UI_PORT_HOST}}`                                                  |
| `COMPOSE_NETWORK_MODE`                               | `ComposeNetworkMode` | `host`                                                                  |
| `DOCKER_IMAGE`                                       | `str`                | `public.ecr.aws/gravitational/teleport-distroless-debug:18`             |
| `PROXY_SERVICE_TUNNEL_LISTEN_ADDRESS_PORT_HOST`      | `str`                | `3024`                                                                  |
| `PROXY_SERVICE_TUNNEL_LISTEN_ADDRESS_PORT_CONTAINER` | `str`                | `3024`                                                                  |
| `PROXY_SERVICE_AGENTS_PORT_HOST`                     | `str`                | `3025`                                                                  |
| `PROXY_SERVICE_AGENTS_PORT_CONTAINER`                | `str`                | `3025`                                                                  |
| `WEB_UI_PORT_HOST`                                   | `str`                | `443`                                                                   |
| `WEB_UI_PORT_CONTAINER`                              | `str`                | `443`                                                                   |
| `ALL_CLIENTS_PORT_HOST`                              | `str`                | `3023`                                                                  |
| `ALL_CLIENTS_PORT_CONTAINER`                         | `str`                | `3023`                                                                  |
| `LISTEN_ADDRESS_HOST`                                | `str`                | `3022`                                                                  |
| `LISTEN_ADDRESS_CONTAINER`                           | `str`                | `3022`                                                                  |
| `TELEPORT_CONFIG`                                    | `str`                | `{DOT_LANDSCAPES}/{LANDSCAPE}/Teleport__Teleport/volumes/config`        |
| `TELEPORT_DATA`                                      | `str`                | `{DOT_LANDSCAPES}/{DOT_SHARED_VOLUMES}/Teleport__Teleport/volumes/data` |
| `ACME_SH_DIR`                                        | `str`                | `{DOT_LANDSCAPES}/.acme.sh`                                             |
| `TELEPORT_CERT`                                      | `str`                | `{DOT_LANDSCAPES}/.acme.sh/certs`                                       |

# Community

| Feature                             | GitHub                                                                                                                                     | Discord                                                                |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| OpenStudioLandscapes                | [https://github.com/michimussato/OpenStudioLandscapes](https://github.com/michimussato/OpenStudioLandscapes)                               | [# openstudiolandscapes-general](https://discord.gg/F6bDRWsHac)        |
| OpenStudioLandscapes-Ayon           | [https://github.com/michimussato/OpenStudioLandscapes-Ayon](https://github.com/michimussato/OpenStudioLandscapes-Ayon)                     | [# openstudiolandscapes-ayon](https://discord.gg/gd6etWAF3v)           |
| OpenStudioLandscapes-Dagster        | [https://github.com/michimussato/OpenStudioLandscapes-Dagster](https://github.com/michimussato/OpenStudioLandscapes-Dagster)               | [# openstudiolandscapes-dagster](https://discord.gg/jwB3DwmKvs)        |
| OpenStudioLandscapes-Kitsu          | [https://github.com/michimussato/OpenStudioLandscapes-Kitsu](https://github.com/michimussato/OpenStudioLandscapes-Kitsu)                   | [# openstudiolandscapes-kitsu](https://discord.gg/6cc6mkReJ7)          |
| OpenStudioLandscapes-RustDeskServer | [https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer](https://github.com/michimussato/OpenStudioLandscapes-RustDeskServer) | [# openstudiolandscapes-rustdeskserver](https://discord.gg/nJ8Ffd2xY3) |
| OpenStudioLandscapes-Teleport       | [https://github.com/michimussato/OpenStudioLandscapes-Teleport](https://github.com/michimussato/OpenStudioLandscapes-Teleport)             | [# openstudiolandscapes-teleport](https://discord.gg/SNMCw5aDfm)       |
| OpenStudioLandscapes-Template       | [https://github.com/michimussato/OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template)             | [# openstudiolandscapes-template](https://discord.gg/J59GYp3Wpy)       |
| OpenStudioLandscapes-Twingate       | [https://github.com/michimussato/OpenStudioLandscapes-Twingate](https://github.com/michimussato/OpenStudioLandscapes-Twingate)             | [# openstudiolandscapes-twingate](https://discord.gg/tREYa6UNJf)       |

To follow up on the previous LinkedIn publications, visit:

- [OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/company/106731439/).
- [Search for tag #OpenStudioLandscapes on LinkedIn](https://www.linkedin.com/search/results/all/?keywords=%23openstudiolandscapes).

***

# Official Resources

[![ Logo Teleport ](https://website.goteleport.com/_uploads/full_20logo_20color_f886ff21bc.svg)](https://www.url.com)

## Teleport

### Feature Matrix

`OpenStudioLandscapes-Teleport` is based on the *Teleport Community Edition*.

[Teleport Feature Matrix](https://goteleport.com/docs/feature-matrix/)

Here you can find some [basic user guides](https://goteleport.com/docs/connect-your-client/).

### Requirements

- [`tctl`](https://goteleport.com/docs/reference/cli/tctl/)
- [`tsh`](https://goteleport.com/docs/reference/cli/tsh/)
- [`teleport`](https://goteleport.com/docs/reference/cli/teleport/)

### Configuration

Here you can find out more about the [`teleport.yaml`](https://goteleport.com/docs/reference/deployment/config/) configuration file.

### Usage

#### Create a User

Teleport does *NOT* come with a preconfigured user. This step *MUST* be performed before a user can access resources via the Web UI or the CLI.

```shell
# Run command:
# $ docker ps -a --no-trunc --filter name=^/teleport$
#
# Which results in something like:
# CONTAINER ID                                                       IMAGE                                                           COMMAND                                                                             CREATED       STATUS                   PORTS     NAMES
# 3e4105e329a532718759903cca3df7ccb0d38cf8b7c6c5659ad5c3fe72d7d76a   public.ecr.aws/gravitational/teleport-distroless-debug:18.2.0   "/usr/bin/dumb-init /usr/local/bin/teleport start -c /etc/teleport/teleport.yaml"   2 weeks ago   Exited (0) 2 weeks ago             teleport
DOCKER_CONTAINER_ID=<teleport_docker_container_id>
/usr/local/bin/docker exec ${DOCKER_CONTAINER_ID} tctl users add admin --roles=editor,access --logins=root,ubuntu,ec2-user
```

For convenience, if a Landscape has been configured with OpenStudioLandscapes (with `OpenStudioLandscapes-Teleport` enabled), the command above can be copied from the `Teleport__cmd_create_teleport_admin` metadata in the `cmd_create_teleport_admin` Dagster asset.

[http://127.0.0.1:3000/assets/Teleport/cmd_create_teleport_admin](http://127.0.0.1:3000/assets/Teleport/cmd_create_teleport_admin)

The command will return something like:

```generic
User "admin" has been created but requires a password. Share this URL with the user to complete user setup, link is valid for 1h:
https://teleport.yourdomain.com:443/web/invite/f25e44d67778cd48a39db3afe87f5174

NOTE: Make sure teleport.yourdomain.com:443 points at a Teleport proxy which users can access.
```

Go ahead and visit the link you're presented with and register your mobile device for Multi-Factor Authentication.

After a user has been created, you can proceed with the following steps.

All subsequent steps are being performed from your local machine.

#### Guides

##### Generate SSL Certificates

SSL, certificates and the web can cause headaches. I'm not an expert in web technology to say the least. For my own sanity (and yours too, hopefully) I have integrated SSL certificate creation into `OpenStudioLandscapes` by packing the most necessary tools and commands into `nox` sessions. We make use of the ready made `acme.sh` Docker image and interact with it directly.

Something important to keep in mind while doing so: the CA (Certificate Authority, i. e. Let's Encrypt) relies on port 80 to be open on your firewall and that `acme.sh`'s `nignx` is reachable on this port. Otherwise, your domain ownership can not be verified.

`OpenStudioLandscapes` Harbor also listens on port 80 which will conflict with `nginx` from `acme.sh`. So, while setting up the certificates with `nox` and `acme.sh`, make sure that Harbor (all `OpenStudioLandscapes` ideally) are shut down. See the [Guide](https://github.com/michimussato/OpenStudioLandscapes/blob/main/wiki/run_openstudiolandscapes/from_manual.md#with-harbor) for more information.

```generic
$ nox --list-sessions
[...]
- acme_sh_prepare -> Create acme.sh docker-compose.yml.
- acme_sh_clear -> Clear acme.sh with `sudo`. WARNING: DATA LOSS!
- acme_sh_up_detach -> Start acme.sh container in detached mode
- acme_sh_print_help -> Print acme.sh help inside running container
- acme_sh_down -> Stop acme.sh container
- acme_sh_register_account -> Register account inside running container
- acme_sh_create_certificate -> Register account inside running container
[...]
```

The following example domain with associated sub-domains have to be registered and the DNS records have to point to the (WAN) IP where `nginx` is listening.

The DNS hoster has to support wildcards for now for everything to work properly. Besides that, the automated certificate creation process requires API access to the DNS server. Both features _can_ be paid features. I, for my part, decided to continue with [ClouDNS.net](https://www.cloudns.net). I subscribed to the [Premium S Model](https://www.cloudns.net/premium/) which is very affordable. Going this extra mile easily compensates for the headache caused by other (free or not) approaches.

My DNS records look as follows:

```generic
mydomain.cloud-ip.cc                    A       <MY ROUTERS IP>
teleport.mydomain.cloud-ip.cc           CNAME   mydomain.cloud-ip.cc
*.teleport.mydomain.cloud-ip.cc         CNAME   teleport.mydomain.cloud-ip.cc
```

API access can be granted in the [API Settings Page](https://www.cloudns.net/api-settings/).

##### Start Over

```shell
tsh logout
systemctl --user disable --now teleport
rm -rf "${HOME}/.config/teleport/*"
rm -rf "${HOME}/.local/share/teleport"
rm "${HOME}/.config/systemd/user/teleport.service"
systemctl --user daemon-reload
```

##### Register SSH Server

The following guide was assembled by following the step outlined in the [Server Access Getting Started Guide](https://goteleport.com/docs/enroll-resources/server-access/getting-started/).

###### Login

```shell
TELEPORT_FQDN=teleport.yourdomain.com

tsh login --proxy=${TELEPORT_FQDN} --user=admin
```

If successful, the result will look something like:

```generic
Enter password for Teleport user admin:
Enter an OTP code from a device:
> Profile URL:        https://teleport.yourdomain.com:443
  Logged in as:       admin
  Cluster:            teleport.yourdomain.com
  Roles:              access, editor
  Logins:             root,ubuntu,ec2-user
  Kubernetes:         enabled
  Valid until:        2025-09-26 22:16:48 +0200 CEST [valid for 12h0m0s]
  Extensions:         login-ip, permit-agent-forwarding, permit-port-forwarding, permit-pty, private-key-policy
```

###### Add Token

```shell
tctl tokens add --type=node --format=text > ${HOME}/.config/teleport/teleport_token
```

###### Configure local Node

```shell
teleport node configure \
    --data-dir=${HOME}/.local/share/teleport \
    --output=file://${HOME}/.config/teleport/teleport.yaml \
    --token=${HOME}/.config/teleport/teleport_token \
    --proxy=${TELEPORT_FQDN}:443
```

###### Start local Node

To start `teleport` as a _One Shot_:

```shell
teleport start --config="${HOME}/.config/teleport/teleport.yaml"
```

To setup `teleport` with `systemd` in `--user` space:

```shell
cat > ${HOME}/.config/systemd/user/teleport.service << "EOF"
[Unit]
Description=Teleport Service
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=5
# EnvironmentFile has to be absolute, so the following
# will not work (hence, disabled):
# EnvironmentFile=-${HOME}/.config/teleport/teleport
ExecStart=/usr/bin/teleport start --config ${HOME}/.config/teleport/teleport.yaml --pid-file=${HOME}/teleport/teleport.pid
# systemd before 239 needs an absolute path
ExecReload=/bin/sh -c "exec pkill -HUP -L -F ${HOME}/teleport/teleport.pid"
PIDFile=${HOME}/teleport/teleport.pid
LimitNOFILE=524288

[Install]
# Todo:
#  ::Unit ${HOME}/.config/systemd/user/teleport.service is added as a dependency to a non-existent unit multi-user.target.
WantedBy=multi-user.target
EOF
```

```shell
systemctl --user daemon-reload
systemctl --user enable --now teleport
# Display logs with `journalctl --user -fu teleport`
```