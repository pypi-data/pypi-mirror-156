import boto3
from tabulate import tabulate


class ECSManager:

    @classmethod
    def get_node_arn(cls, cluster, pattern=None, anti_pattern=None):
        taks_per_service = {}
        client = boto3.client('ecs')
        for x in client.list_services(cluster=cluster).get('serviceArns', []):
            if pattern:
                for c in pattern:
                    if c in x.lower():
                        return x
            elif anti_pattern:
                found_node = True
                for c in anti_pattern:
                    if c in x.lower():
                        found_node = False
                        continue
                if found_node:
                    return x

    @classmethod
    def start_service(cls, cluster, pattern=None, anti_pattern=None, nb_tasks=1):
        client = boto3.client('ecs')
        service_arn = cls.get_node_arn(cluster, pattern=pattern, anti_pattern=anti_pattern)
        client.update_service(
            cluster=cluster,
            service=service_arn,
            desiredCount=nb_tasks
        )
        while True:
            running_tasks = client.list_tasks(cluster=cluster, serviceName=service_arn).get('taskArns', [])
            if not running_tasks:
                continue
            desc = client.describe_tasks(cluster=cluster, tasks=running_tasks)
            is_started = True
            for task in desc.get('tasks', []):
                lastStatus = task.get('lastStatus')
                if lastStatus.lower() != 'running':
                    is_started = False
            if is_started:
                break
        return service_arn

    @classmethod
    def stop_service(cls, cluster, pattern=None, anti_pattern=None):
        client = boto3.client('ecs')
        service_arn = cls.get_node_arn(cluster, pattern=pattern, anti_pattern=anti_pattern)
        client.update_service(
            cluster=cluster,
            service=service_arn,
            desiredCount=0)

    @classmethod
    def info_cluster(cls, cluster):
        client = boto3.client('ecs')
        services = sorted(client.list_services(cluster=cluster).get('serviceArns', []))
        describe_service = client.describe_services(cluster=cluster, services=services).get('services', [])
        display = [['Service Name', 'Nb desired', 'Nb running', 'Nb pending']]
        for service in describe_service:
            service_name = service['serviceName'].split('/')[-1]
            running_count = service['runningCount']
            pending_count = service['pendingCount']
            desired_count = service['desiredCount']
            display.append([service_name, desired_count, running_count, pending_count])
        print(tabulate(display[1:], headers=display[0]))

