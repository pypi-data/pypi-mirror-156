from ipsilon.util import config as pconfig
from ipsilon.info.infosssd import InfoProvider as SSSDInfoProvider


AWS_IDP_ARN = "arn:aws:iam::125523088429:saml-provider/id.fedoraproject.org"
AWS_GROUPS = {
    "aws-master": "arn:aws:iam::125523088429:role/aws-master",
    "aws-iam": "arn:aws:iam::125523088429:role/aws-iam",
    "aws-billing": "arn:aws:iam::125523088429:role/aws-billing",
    "aws-atomic": "arn:aws:iam::125523088429:role/aws-atomic",
    "aws-s3-readonly": "arn:aws:iam::125523088429:role/aws-s3-readonly",
    "aws-fedoramirror": "arn:aws:iam::125523088429:role/aws-fedoramirror",
    "aws-s3": "arn:aws:iam::125523088429:role/aws-s3",
    "aws-cloud-poc": "arn:aws:iam::125523088429:role/aws-cloud-poc",
    "aws-infra": "arn:aws:iam::125523088429:role/aws-infra",
    "aws-docs": "arn:aws:iam::125523088429:role/aws-docs",
    "aws-copr": "arn:aws:iam::125523088429:role/aws-copr",
    "aws-centos": "arn:aws:iam::125523088429:role/aws-centos",
    "aws-min": "arn:aws:iam::125523088429:role/aws-min",
    "aws-fedora-ci": "arn:aws:iam::125523088429:role/aws-fedora-ci",
    "aws-fcos-mgmt": "arn:aws:iam::125523088429:role/aws-fcos-mgmt",
}


class InfoProvider(SSSDInfoProvider):
    def __init__(self, *kwargs):
        super().__init__(*kwargs)
        self.name = "fas"
        self.description = """
A Fedora-specific version of the SSSd info plugin.
"""
        self.new_config(
            self.name,
            pconfig.Condition(
                "preconfigured", "SSSD can only be used when pre-configured", False
            ),
        )

    def get_user_attrs(self, user):
        reply = super().get_user_attrs(user)
        reply["_extras"]["awsroles"] = []
        for group in reply["_groups"]:
            if group in AWS_GROUPS:
                reply["_extras"]["awsroles"].append(
                    "%s,%s" % (AWS_IDP_ARN, AWS_GROUPS[group])
                )
        return reply
