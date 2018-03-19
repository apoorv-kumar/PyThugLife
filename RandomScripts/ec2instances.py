import pprint

pprint.pprint(
    [tag
        for instance in boto3.resource('ec2', 'us-west-2').instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        for tag in instance.meta.data['Tags'] if tag['Key'] == 'Name']
)
