import textwrap

import snakemd

"""
# Enroll SSH Server
# 1.)
# https://goteleport.com/docs/enroll-resources/server-access/getting-started/
$ tsh login --proxy=teleport.openstudiolandscapes.cloud-ip.cc --user=admin
Enter password for Teleport user admin:
Enter an OTP code from a device:
$ tctl status
> Profile URL:        https://teleport.openstudiolandscapes.cloud-ip.cc:443
  Logged in as:       admin
  Cluster:            teleport.farm.evil
  Roles:              access, editor
  Logins:             root, ubuntu, ec2-user
  Kubernetes:         enabled
  Valid until:        2025-09-23 22:30:43 +0200 CEST [valid for 12h0m0s]
  Extensions:         login-ip, permit-agent-forwarding, permit-port-forwarding, permit-pty, private-key-policy

Cluster: teleport.farm.evil
Version: 18.2.0
CA pins: sha256:7c1a3095c6be4478321f16a83d54bf2125fe8c060e43c5067066b99bab78b8d1

authority     rotation                protocol status algorithm   storage
------------- ----------------------- -------- ------ ----------- --------
host          standby (never rotated) SSH      active Ed25519     software
                                      TLS      active ECDSA P-256 software
user          standby (never rotated) SSH      active Ed25519     software
                                      TLS      active ECDSA P-256 software
db            standby (never rotated) TLS      active RSA 2048    software
db_client     standby (never rotated) TLS      active RSA 2048    software
openssh       standby (never rotated) SSH      active Ed25519     software
jwt           standby (never rotated) JWT      active ECDSA P-256 software
saml_idp      standby (never rotated) TLS      active RSA 2048    software
oidc_idp      standby (never rotated) JWT      active RSA 2048    software
spiffe        standby (never rotated) JWT      active RSA 2048    software
                                      TLS      active ECDSA P-256 software
okta          standby (never rotated) JWT      active ECDSA P-256 software
awsra         standby (never rotated) TLS      active ECDSA P-256 software
bound_keypair standby (never rotated) JWT      active Ed25519     software
# 2.)
# $ tctl tokens add --type=node --format=text > token.file
$ tctl tokens add --type=node --format=text > ./teleport_token
# 3.)
$ sudo teleport node configure \
   --output=file:///etc/teleport.yaml \
   --token=/home/michael/.config/teleport/teleport_token \
   --proxy=teleport.openstudiolandscapes.cloud-ip.cc:443

A Teleport configuration file has been created at "/etc/teleport.yaml".
To start Teleport with this configuration file, run:

sudo teleport start --config="/etc/teleport.yaml"

Note that starting a Teleport server with this configuration will require root access as:
- The Teleport configuration is located at "/etc/teleport.yaml".
- Teleport will be storing data at "/var/lib/teleport". To change that, edit the "data_dir" field in "/etc/teleport.yaml".
Happy Teleporting!
"""


def readme_feature(doc: snakemd.Document) -> snakemd.Document:

    # Some Specific information

    doc.add_heading(
        text="Official Resources",
        level=1,
    )

    # Logo

    doc.add_paragraph(
        snakemd.Inline(
            text=textwrap.dedent(
                """
                Logo Teleport
                """
            ),
            image={
                # "Teleport": "https://goteleport.com/blog/_next/image/?url=https%3A%2F%2Fwebsite.goteleport.com%2F_uploads%2Ffull_20logo_20color_f886ff21bc.svg&w=256&q=75",
                "Teleport": "https://website.goteleport.com/_uploads/full_20logo_20color_f886ff21bc.svg",
            }["Teleport"],
            link="https://www.url.com",
        ).__str__()
    )

    doc.add_heading(
        text="Teleport",
        level=2,
    )

    doc.add_heading(
        text="Feature Matrix",
        level=3,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            `OpenStudioLandscapes-Teleport` is based on the Teleport
            Community Edition.
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            [Teleport Feature Matrix](https://goteleport.com/docs/feature-matrix/)
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Here you can find some [basic user guides](https://goteleport.com/docs/connect-your-client/).
            """
        )
    )

    doc.add_heading(
        text="Requirements",
        level=3,
    )

    doc.add_unordered_list(
        [
            "`[tctl](https://goteleport.com/docs/reference/cli/tctl/)`",
            "`[tsh](https://goteleport.com/docs/reference/cli/tsh/)`",
            "`[teleport](https://goteleport.com/docs/reference/cli/teleport/)`",
        ]
    )

    doc.add_heading(
        text="Usage",
        level=3,
    )

    doc.add_heading(
        text="Create a User",
        level=4,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Teleport does *NOT* come with a preconfigured user. This step *MUST* be performed
            before a user can access resources via the Web UI or the CLI.
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            # Run command:
            # $ docker ps -a --no-trunc --filter name=^/teleport$
            #
            # Which results in something like:
            # CONTAINER ID                                                       IMAGE                                                           COMMAND                                                                             CREATED       STATUS                   PORTS     NAMES
            # 3e4105e329a532718759903cca3df7ccb0d38cf8b7c6c5659ad5c3fe72d7d76a   public.ecr.aws/gravitational/teleport-distroless-debug:18.2.0   "/usr/bin/dumb-init /usr/local/bin/teleport start -c /etc/teleport/teleport.yaml"   2 weeks ago   Exited (0) 2 weeks ago             teleport
            DOCKER_CONTAINER_ID=<teleport_docker_container_id>
            /usr/local/bin/docker exec ${DOCKER_CONTAINER_ID} tctl users add admin --roles=editor,access --logins=root,ubuntu,ec2-user\
            """
        ),
        lang="shell",
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            For convenience, if a Landscape has been configured with OpenStudioLandscapes (with
            OpenStudioLandscapes-Teleport enabled), the command above can be copied from the
            `Teleport__cmd_create_teleport_admin` metadata in the `cmd_create_teleport_admin` asset.
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            [http://127.0.0.1:3000/assets/Teleport/cmd_create_teleport_admin](http://127.0.0.1:3000/assets/Teleport/cmd_create_teleport_admin)
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            The command will return something like:
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            User "admin" has been created but requires a password. Share this URL with the user to complete user setup, link is valid for 1h:
            https://teleport.yourdomain.com:443/web/invite/f25e44d67778cd48a39db3afe87f5174
            
            NOTE: Make sure teleport.yourdomain.com:443 points at a Teleport proxy which users can access.\
            """
        ),
        lang="shell",
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            Go ahead and visite the linke you're presented with and register your mobile device for
            Multi-Factor Authentication.
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            After a user has been created, you can proceed with the following steps.
            """
        )
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            All subsequent steps are being performed from your local machine.
            """
        )
    )

    doc.add_heading(
        text="Guides",
        level=4,
    )

    doc.add_heading(
        text="Start Over",
        level=5,
    )

    doc.add_code(
        code=textwrap.dedent(
            f"""\
            tsh logout
            sudo rm -rf /var/lib/teleport
            sudo rm /etc/teleport.yaml
            rm -rf ~/.config/teleport/*\
            """
        ),
        lang="shell",
    )

    doc.add_heading(
        text="Register SSH Server",
        level=5,
    )

    doc.add_heading(
        text="Login",
        level=6,
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            TELEPORT_FQDN=teleport.yourdomain.com
            
            tsh login --proxy=${TELEPORT_FQDN} --user=admin\
            """
        ),
        lang="shell",
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            If successful, the result will look something like:
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            Enter password for Teleport user admin:
            Enter an OTP code from a device:
            > Profile URL:        https://teleport.yourdomain.com:443
              Logged in as:       admin
              Cluster:            teleport.yourdomain.com
              Roles:              access, editor
              Logins:             root,ubuntu,ec2-user
              Kubernetes:         enabled
              Valid until:        2025-09-26 22:16:48 +0200 CEST [valid for 12h0m0s]
              Extensions:         login-ip, permit-agent-forwarding, permit-port-forwarding, permit-pty, private-key-policy\
            """
        ),
        lang="shell",
    )

    doc.add_heading(
        text="Add Token",
        level=6,
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            tctl tokens add --type=node --format=text > ${HOME}/.config/teleport/teleport_token\
            """
        ),
        lang="shell",
    )

    doc.add_heading(
        text="Configure local Node",
        level=6,
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            teleport node configure \
                --data-dir=${HOME}/.local/share/teleport \
                --output=file://${HOME}/.config/teleport/teleport.yaml \
                --token=${HOME}/.config/teleport/teleport_token \
                --proxy=teleport.yourdomain.com:443\
            """
        ),
        lang="shell",
    )

    doc.add_heading(
        text="Start local Node",
        level=6,
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            To start `teleport` as a _One Shot_:
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            teleport start --config="${HOME}/.config/teleport/teleport.yaml"\
            """
        ),
        lang="shell",
    )

    doc.add_paragraph(
        text=textwrap.dedent(
            """
            To start `teleport` with `systemd` in `--user` space:
            """
        )
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            cat > ${HOME}/.config/systemd/teleport.service2 << "EOF"
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
            EOF\
            """
        ),
        lang="shell",
    )

    doc.add_code(
        code=textwrap.dedent(
            """\
            systemctl --user daemon-reload
            systemctl --user enable teleport
            systemctl --user start teleport
            # Display logs with `journalctl --user -fu teleport`\
            """
        ),
        lang="shell",
    )

    # doc.add_horizontal_rule()

    return doc


if __name__ == "__main__":
    pass
