# -*- coding: utf-8 -*-
#
# © 2016 Krux Digital, Inc.
#

#
# Standard libraries
#

from __future__ import absolute_import
import os

#
# Internal libraries
#

from krux.cli import get_group
import krux_boto.cli
from krux_elb.elb import add_elb_cli_arguments, get_elb, NAME


class Application(krux_boto.cli.Application):

    def __init__(self, name=NAME):
        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)

        self.elb = get_elb(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser):
        # Call to the superclass
        super(Application, self).add_cli_arguments(parser)

        add_elb_cli_arguments(parser, include_boto_arguments=False)

    def run(self):
        print self.elb.find_load_balancers(
            # console-b001.krxd.net
            # Arbitrary chosen as a test instance
            instance_id='i-16137da5'
        )


def main():
    app = Application()
    with app.context():
        app.run()


# Run the application stand alone
if __name__ == '__main__':
    main()
