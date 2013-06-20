from boto.ec2 import EC2Connection
from boto.ec2.securitygroup import SecurityGroup
import urllib2
import logging
from mako.template import Template
from pprint import pprint

def get_self_instance_id():
    '''
    Get this instance's id.
    '''
    logging.debug('get_self_instance_id()')
    response = urllib2.urlopen('http://169.254.169.254/1.0/meta-data/instance-id')
    instance_id = response.read()
    return instance_id


def get_all_security_groups(access_key=None, secret_key=None, security_group=None):
    conn = EC2Connection(aws_access_key_id=access_key,
                         aws_secret_access_key=secret_key)
    instances = []
    for reservation in conn.get_all_instances():
        if len(reservation.instances) > 0:
            for instance in reservation.instances:
                if len(instance.groups) > 0:
                    for group in instance.groups:
                        if security_group in group.name or security_group in group.id:
                            if instance.state == 'running':
                                instances.append(instance)

    return instances


def steal_elastic_ip(access_key=None, secret_key=None, ip=None):
    '''
    Assign an elastic IP to this instance.
    '''
    logging.debug('steal_elastic_ip()')
    instance_id = get_self_instance_id()
    conn = EC2Connection(aws_access_key_id=access_key,
                         aws_secret_access_key=secret_key)
    conn.associate_address(instance_id=instance_id, public_ip=ip)


def get_running_instances(access_key=None, secret_key=None, security_group=None):
    '''
    Get all running instances. Only within a security group if specified.
    '''
    logging.debug('get_running_instances()')

    conn = EC2Connection(aws_access_key_id=access_key,
                         aws_secret_access_key=secret_key)

    if security_group:
        sg = SecurityGroup(connection=conn, name=security_group)
        instances = [i for i in sg.instances() if i.state == 'running']
        return instances
    else:
        instances = conn.get_all_instances()
        return instances


def file_contents(filename=None, content=None):
    '''
    Just return the contents of a file as a string or write if content
    is specified. Returns the contents of the filename either way.
    '''
    logging.debug('file_contents()')
    if content:
        f = open(filename, 'w')
        f.write(content)
        f.close()
    
    try:
        f = open(filename, 'r')
        text = f.read()
        f.close()
    except:
        text = None

    return text


def generate_haproxy_config(template=None, instances=None):
    '''
    Generate an haproxy configuration based on the template and instances list.
    '''
    return Template(filename=template).render(instances=instances)
