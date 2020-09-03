from __future__ import print_function
import json
import boto3
import boto.ec2
import logging
import time
import datetime
import types


# enable logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Keys to save for images
EC2_IMAGE_KEYS = ["ImageId", "State", "OwnerId",
        "Public", "Architecture", "PlatformDetails", "ImageType", "kernel_id",
        "ramdisk_id", "Name", "Description", "product_codes",
        "billing_products", "RootDeviceType", "RootDeviceName",
        "VirtualizationType", "Hypervisor", "instance_lifecycle",
        "sriov_net_support"]

## ec2 objects
ec2_resource = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

# Ensure image json format
def pop_description_result_image(item, keys, init_result):
    if item is None:
        return {}
    result = init_result
    for key in keys:
        result[key] = str(item['Images'][0].get(key))

    return result

# Ensure Snapshot json format
def pop_description_result_snapshot(item, keys, init_result):
    if item is None:
        return {}
    result = init_result
    for key in keys:
        result[key] = item.get(key, None)

    return result

# Ensure Instance json format
def pop_description_result_instance(item, keys, init_result):
    if item is None:
        return {}
    result = init_result
    for key in keys:
        result[key] = str(getattr(item, key, None))

    return result

# get image metadata
def _get_image_attributes(image_id):
    try:
        image_attributes = ec2_client.describe_images(ImageIds=[image_id])
    except BotoServerError as e:
        image_attributes = None
        logger.warn('image load has failed because of %s', str(e))
    return image_attributes

def ec2_instances():
    # get all instances
    keys = ["state", "state_code", "previous_state", "previous_state_code",
            "placement", "placement_tenancy",
            "ami_launch_index", "architecture", "client_token", "dns_name",
            "ebs_optimized", "group_name", "hypervisor", "id", "image_id",
            "instance_profile", "instance_type", "ip_address", "item",
            "kernel", "key_name", "launch_time", "monitored", "monitoring",
            "monitoring_state", "persistent", "platform", "private_dns_name",
            "private_ip_address", "public_dns_name", "reason",
            "root_device_name", "root_device_type", "sourceDestCheck",
            "spot_instance_request_id", "subnet_id", "tags",
            "virtualization_type", "vpc_id"]
    image = {}
    results = []
    all_instances = ec2_resource.instances.all()
    for instance in all_instances:
        return getattr(instance, "state_code")
        image_id = getattr(instance, 'image_id', None)
        if image_id is not None:
            image_attributes = _get_image_attributes(image_id)
        else:
            image_attributes = None

        if image_attributes is not None:
            image = pop_description_result_image(image_attributes, EC2_IMAGE_KEYS, {})

        result = pop_description_result_instance(instance, keys, {
            "owner_id": image_attributes['Images'][0]['OwnerId'],
            "image": {
                "id": image_id,
                "attributes": image
            }
        })
        results.append(result)
    return results

def ec2_reserved_instances():
    results = []
    reserved_instances = ec2_client.describe_reserved_instances()['ReservedInstances']
    results.append(reserved_instances)

    return results

def ec2_ebs_snapshots():
    snapshots = ec2_client.describe_snapshots(OwnerIds=['self'])
    snapshots['Snapshots']

    return snapshots['Snapshots']
