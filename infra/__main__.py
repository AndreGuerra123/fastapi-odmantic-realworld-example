import json
from pulumi import export, ResourceOptions, Output
import pulumi_aws as aws
import pulumi_docker as docker
import pulumi_awsx as awsx

repository = awsx.ecr.Repository(
    "repository",
    awsx.ecr.RepositoryArgs(
        force_delete=True
    ),
)

image = awsx.ecr.Image(
    "image",
    awsx.ecr.ImageArgs(
        repository_url=repository.url, context="../", dockerfile="../dockerfile", platform="linux/amd64"
    ),
)

# Create an ECS cluster to run a container-based service.
cluster = aws.ecs.Cluster('cluster')

lb = awsx.lb.ApplicationLoadBalancer("lb")

service = awsx.ecs.FargateService(
    "service",
    awsx.ecs.FargateServiceArgs(
        cluster=cluster.arn,
        assign_public_ip=True,
        task_definition_args=awsx.ecs.FargateServiceTaskDefinitionArgs(
            container=awsx.ecs.TaskDefinitionContainerDefinitionArgs(
                name="my-service",
                image=image.image_uri,
                cpu=512,
                memory=128,
                essential=True,
                port_mappings=[
                    awsx.ecs.TaskDefinitionPortMappingArgs(
                        container_port=80,
                        target_group=lb.default_target_group,
                    )
                ],
                environment=[
                    awsx.ecs.TaskDefinitionKeyValuePairArgs(name="mongo_uri", value="test"),
				]
            ),
        ),
    ),
)

export("url", Output.concat("http://", lb.load_balancer.dns_name))

#TODO: Add mongo