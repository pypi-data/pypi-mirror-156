# Copyright 2018-2019, James Nugent.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain
# one at http://mozilla.org/MPL/2.0/.

"""
Contains a Pulumi ComponentResource for creating a good-practice AWS VPC.
"""
import json, time
from typing import Mapping, Sequence
from pulumi import ComponentResource, ResourceOptions, StackReference
from pulumi import Input, Output

from resources import rds, ec2, sm, random
from resourceComponents import secrets_manager, security_group


class RDS(ComponentResource):
    """
    Comment here

    """

    def __init__(self, name: str, props: None, vpc_props: None, mssql_sg: None, opts:  ResourceOptions = None):
        """
        Constructs an Postgresql Cluster.

        :param name: The Pulumi resource name. Child resource names are constructed based on this.
        """
        super().__init__('Mssql', name, {}, opts)

        # Make base info available to other methods
        # self.name = name
        # self.description = props.description
        # self.base_tags = props.base_tags

        Resources = [rds, ec2]

        for resource in Resources:
            resource.self = self
            resource.base_tags = props.base_tags


        # Create RDS Instance Password
        password = random.RandomString(
            name,
            parent=self,
            depends_on=opts.depends_on,
        )

        # Create RDS Cluster
        rds_cluster = [rds.Cluster(
            props.postgresql[i]["cluster_name"],
            props,
            username=props.postgresql[i]["setflow_sm"]["secret_version"]["username"],
            password=password.result,
            engine=props.postgresql[i]["engine"],
            engine_version=props.postgresql[i]["engine_version"],
            cluster_class=props.postgresql[i]["cluster_class"],
            apply_immediately=props.postgresql[i]["apply_immediately"],
            secgrp_ids=mssql_sg,
            snetgrp_name=(rds.SubnetGroup(
                props.postgresql[i]["snetgrp_name"],
                props,
                # snet_ids=[snet1,snet2,snet3],
                snet_ids=vpc_props["subnets"],
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            optgrp_name=(rds.OptionGroup(
                props.postgresql[i]["optgrp_name"],
                props,
                parent=self, 
                provider=opts.providers.get(props.stack+'_prov')).name),
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )
        for i in props.postgresql
        ]

        # construct secrets parameters
        string = Output.all(host=rds_cluster[0].endpoint, pword=password.result).apply(lambda args: sm.rdsJsonify(
                username=props.sm["postgresql-secrets"]["secret_version"]["username"],
                password=args['pword'],
                engine=props.sm["postgresql-secrets"]["secret_version"]["engine"],
                host=args['host'],
                port=props.sm["postgresql-secrets"]["secret_version"]["port"],
                db_id=props.sm["postgresql-secrets"]["secret_version"]["dbInstanceIdentifier"],
                db=props.sm["postgresql-secrets"]["secret_version"]["database"],
            )
        )

        # Store Credentials and Properties in Secrets Manager
        secret = secrets_manager.SecretsManager(
            'postgresql-'+props.stack,
            props=props,
            name=props.sm["postgresql-secrets"]["secret_name"],
            secrets = string,
            parent=self,
            depends_on=opts.depends_on,
            provider=opts.providers.get(props.stack+'_prov')
        )


        