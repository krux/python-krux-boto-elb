# krux_elb

`krux_elb` is a library that provides wrapper functions for common S3 usage. It uses `krux_boto` to connect to AWS ELB.

## Warning

In the current version, `krux_elb.elb.ELB` is only compatible with `krux_boto.boto.Boto` object. Passing other objects, such as `krux_boto.boto.Boto3`, will cause an exception.

## Application quick start

The most common use case is to build a CLI script using `krux_boto.cli.Application`.
Here's how to do that:

```python

from krux_boto.cli import Application
from krux_elb.elb import ELB

def main():
    # The name must be unique to the organization. The object
    # returned inherits from krux.cli.Application, so it provides
    # all that functionality as well.
    app = Application(name='krux-my-boto-script')

    ec2 = EC2(boto=app.boto)
    f = Filter({
        'tag:Name': 'example.krxd.net',
        'instance-state-name': ['running', 'stopped'],
    })
    instance = ec2.find_instances(f)

    elb = ELB(boto=app.boto)
    print self.elb.find_load_balancers(
        instance=instance[0]
    )

### Run the application stand alone
if __name__ == '__main__':
    main()

```

As long as you get an instance of `krux_boto.boto.Boto`, the rest are the same. Refer to `krux_boto` module's [README](https://github.com/krux/python-krux-boto/blob/master/README.md) on various ways to instanciate the class.
