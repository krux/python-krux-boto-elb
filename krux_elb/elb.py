# -*- coding: utf-8 -*-
#
# © 2015 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import sys

#
# Third party libraries
#

from krux_boto import Boto, add_boto_cli_arguments
from krux.logging import get_logger
from krux.stats import get_stats
from krux.cli import get_parser, get_group
import boto.ec2
import boto.ec2.elb


NAME = 'krux-elb'


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


class ELBInstanceMismatchError(StandardError):
    pass


class ELB(object):
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
        # Private variables, not to be used outside this module
        self._name = NAME
        self._logger = logger or get_logger(self._name)
        self._stats = stats or get_stats(prefix=self._name)

        # Throw exception when Boto2 is not used
        if not isinstance(boto, Boto):
            raise TypeError('krux_elb.elb.ELB only supports krux_boto.boto.Boto')

        self.boto = boto

        # Set up default cache
        self._conn = None

    def _get_connection(self):
        """
        Returns a connection to the designated region (self.boto.cli_region).
        The connection is established on the first call for this instance (lazy) and cached.
        """
        if self._conn is None:
            self._conn = self.boto.ec2.elb.connect_to_region(self.boto.cli_region)

        return self._conn

    def find_load_balancers(self, instance):
        """
        Returns a list of ELB that the given instance is behind
        """
        elb = self._get_connection()

        load_balancers = [
            lb for lb in elb.get_all_load_balancers()
            if instance.id in [i.id for i in lb.instances]
        ]

        self._logger.info('Found following load balancers: %s', load_balancers)

        if len(load_balancers) > 1:
            self._logger.warning('The given instance is under multiple load balancers: %s', load_balancers)

        return load_balancers

    def remove_instance(self, instance, load_balancer_name):
        """
        Removes the given instance from the ELB with the given name.
        """
        elb = self._get_connection()
        try:
            elb.deregister_instances(load_balancer_name, [instance.id])
        except boto.exception.BotoServerError:
            trace = sys.exc_info()[2]
            raise ELBInstanceMismatchError(), None, trace
        self._logger.info('Removed instance %s from load balancer %s', instance.tags.get('Name'), load_balancer_name)

    def add_instance(self, instance, load_balancer_name):
        """
        Adds the given instance to the ELB with the given name.
        """
        elb = self._get_connection()
        try:
            elb.register_instances(load_balancer_name, [instance.id])
        except boto.exception.BotoServerError:
            trace = sys.exc_info()[2]
            raise ELBInstanceMismatchError(), None, trace
        self._logger.info('Added instance %s to load balancer %s', instance.tags.get('Name'), load_balancer_name)
