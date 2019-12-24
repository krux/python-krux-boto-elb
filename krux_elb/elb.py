# -*- coding: utf-8 -*-
#
# © 2019 Salesforce.com
#

from typing import List

from krux_boto.boto import add_boto_cli_arguments, Boto3
from krux.logging import get_logger
from krux.stats import get_stats
from krux.cli import get_parser, get_group
from krux.object import Object

NAME = 'krux-elb'


def get_elb(args=None, logger=None, stats=None):
    """
    Return a usable ELB object without creating a class around it.

    In the context of a krux.cli (or similar) interface the 'args', 'logger'
    and 'stats' objects should already be present. If you don't have them,
    however, we'll attempt to provide usable ones for the SQS setup.

    (If you omit the add_elb_cli_arguments() call during other cli setup,
    the Boto object will still work, but its cli options won't show up in
    --help output)

    (This also handles instantiating a Boto object on its own.)
    """
    if not args:
        parser = get_parser()
        add_elb_cli_arguments(parser)
        args = parser.parse_args()
    if not logger:
        logger = get_logger(name=NAME)

    if not stats:
        stats = get_stats(prefix=NAME)

    boto = Boto3(
        log_level=args.boto_log_level,
        access_key=args.boto_access_key,
        secret_key=args.boto_secret_key,
        region=args.boto_region,
        logger=logger,
        stats=stats,
    )
    return ELB(
        boto=boto,
        logger=logger,
        stats=stats,
    )


def add_elb_cli_arguments(parser, include_boto_arguments=True):
    """
    Utility function for adding ELB specific CLI arguments.
    """
    if include_boto_arguments:
        # GOTCHA: Since ELB both uses Boto, the Boto's CLI arguments can be included multiple times,
        # when used with other libraries, causing an error. This creates a way to circumvent that.

        # Add all the boto arguments
        add_boto_cli_arguments(parser)

    # Add those specific to the application
    group = get_group(parser, NAME)


class ELB(Object):
    """
    A manager to handle all ELB related functions.
    Each instance is locked to a connection to a designated region (self.boto.cli_region).
    """

    def __init__(
        self,
        boto,
        logger=None,
        stats=None,
    ):
        super(ELB, self).__init__(name=NAME, logger=logger, stats=stats)

        if not isinstance(boto, Boto3):
            raise TypeError('krux_elb.elb.ELB only supports krux_boto.boto.Boto3')

        self.boto = boto

        # Private variables, not to be used outside this module
        self._name = NAME
        self._logger = logger or get_logger(self._name)
        self._stats = stats or get_stats(prefix=self._name)

        # Set up default cache
        self._client = None

    def _get_client(self):
        """
        Returns a client to the designated region (self.boto.cli_region).
        .. note::
            The connection is established on the first call for this instance (lazy) and cached.
        :return: Client to the designated region
        :rtype: boto3.client
        """
        if self._client is None:
            self._client = self.boto.client(service_name='elb', region_name=self.boto.cli_region)

        return self._client

    def find_load_balancers(self, instance_id):  # type: (str) -> List[str]
        """
        Returns a list of Load Balancer names that the given instance is behind
        """
        elb = self._get_client()
        load_balancer_descriptions = elb.describe_load_balancers()['LoadBalancerDescriptions']

        load_balancers = [
            lb['LoadBalancerName'] for lb in load_balancer_descriptions
            if instance_id in [instances['InstanceId'] for instances in lb['Instances']]
        ]

        self._logger.info('Found following load balancers: %s', load_balancers)

        if len(load_balancers) > 1:
            self._logger.warning('The instance %s is under multiple load balancers: %s', instance_id, load_balancers)

        return load_balancers

    def remove_instance(self, instance_id, load_balancer_name):  # type: (str, str) -> None
        """
        Removes the given instance from the ELB with the given name.
        """
        elb = self._get_client()
        elb.deregister_instances_from_load_balancer(
            LoadBalancerName=load_balancer_name,
            Instances=[{'InstanceId': instance_id}]
        )
        self._logger.info('Removed instance %s from load balancer %s', instance_id, load_balancer_name)

    def add_instance(self, instance_id, load_balancer_name):  # type: (str, str) -> None
        """
        Adds the given instance to the ELB with the given name.
        """
        elb = self._get_client()
        elb.register_instances_with_load_balancer(
            LoadBalancerName=load_balancer_name,
            Instances=[{'InstanceId': instance_id}]
        )
        self._logger.info('Added instance %s to load balancer %s', instance_id, load_balancer_name)
