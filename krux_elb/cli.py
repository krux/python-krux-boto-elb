# -*- coding: utf-8 -*-
#
# © 2019 Salesforce.com
#

from __future__ import print_function

from krux.cli import get_group
import krux_boto.cli

from . import elb


class Application(krux_boto.cli.Application):

    def __init__(self, name=elb.NAME):
        # Call to the superclass to bootstrap.
        super(Application, self).__init__(name=name)
        self.elb = elb.get_elb(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser):
        super(Application, self).add_cli_arguments(parser)
        elb.add_elb_cli_arguments(parser, include_boto_arguments=False)

    def run(self):
        print(self.elb.find_load_balancers(
            # Arbitrary chosen as a test instance: console-c001.krxd.net
            instance_id='i-030b394f463cc079b'
        ))


def main():
    app = Application()
    with app.context():
        app.run()


# Run the application stand alone
if __name__ == '__main__':
    main()
