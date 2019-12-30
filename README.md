# krux_elb

`krux_elb` is a library that provides wrapper functions for common ELB usage. It uses `krux_boto` to connect to AWS ELB.

## Application quick start

The most common use case is to build a CLI script using `krux_elb.cli.Application`.
Here's how to do that:

```python

import krux_elb.cli

# This class inherits from krux.cli.Application, so it provides
# all that functionality as well.
class Application(krux_elb.cli.Application):
    def run(self):
        print self.elb.find_load_balancers(
            instance='i-a1b2c3d4'
        )

def main():
    # The name must be unique to the organization.
    app = Application(name='krux-my-s3-script')
    with app.context():
        app.run()

# Run the application stand alone
if __name__ == '__main__':
    main()

```

## Extending your application

From other CLI applications, you can make the use of `krux_elb.elb.get_elb()` function.

```python

from krux_elb.elb import add_elb_cli_arguments, get_elb
import krux.cli

class Application(krux.cli.Application):

    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

        self.elb = get_elb(self.args, self.logger, self.stats)

    def add_cli_arguments(self, parser):
        super(Application, self).add_cli_arguments(parser)

        add_elb_cli_arguments(parser)

```

Alternately, you want to add ELB functionality to your larger script or application.
Here's how to do that:

```python

from krux_boto import Boto
from krux_elb import ELB

class MyApplication(object):

    def __init__(self, *args, **kwargs):
        boto = Boto(
            logger=self.logger,
            stats=self.stats,
        )
        self.elb = ELB(
            boto=boto,
            logger=self.logger,
            stats=self.stats,
        )

    def run(self):
        print self.elb.find_load_balancers(
            instance='i-a1b2c3d4'
        )

```

As long as you get an instance of `krux_boto.boto.Boto`, the rest are the same. Refer to `krux_boto` module's [README](https://github.com/krux/python-krux-boto/blob/master/README.md) on various ways to instanciate the class.
