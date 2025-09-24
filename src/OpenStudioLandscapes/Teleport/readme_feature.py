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

    # doc.add_heading(
    #     text="Official Resources",
    #     level=1,
    # )

    # Logo

    # doc.add_paragraph(
    #     snakemd.Inline(
    #         text=textwrap.dedent(
    #             """
    #             Logo Template
    #             """
    #         ),
    #         image={
    #             "Template": "https://www.url.com/yourlogo.png",
    #         }["Template"],
    #         link="https://www.url.com",
    #     ).__str__()
    # )
    #
    # doc.add_paragraph(
    #     text=textwrap.dedent(
    #         """
    #         Official Template information.
    #         """
    #     )
    # )

    # doc.add_horizontal_rule()

    return doc


if __name__ == "__main__":
    pass
