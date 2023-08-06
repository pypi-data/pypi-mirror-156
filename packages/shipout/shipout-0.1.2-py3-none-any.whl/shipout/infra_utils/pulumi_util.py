# Copyright 2022, Blurware, LLC.  All rights reserved.
import os
import pulumi
import pulumi_azure_native as azure_native
import pulumi_azure as azure

class NitroPulumiInfra: 
    def prep_environment(
        resource_group_name: str, 
        workspace_name: str, 
        kube_env_name: str, 
        container_name: str, 
        location: str, 
        workspacesku_name : str='PerGB2018', 
        dapr_ai_connection_string: str="InstrumentationKey=00000000-0000-0000-0000-000000000000;IngestionEndpoint=https://northcentralus-0.in.applicationinsights.azure.com/", 
        managed_environment_destination: str="log-analytics"
        ): 
        resource_group = azure_native.resources.ResourceGroup(resource_group_name)

        workspace = azure_native.operationalinsights.Workspace(workspace_name,
            resource_group_name=resource_group.name,
            sku=azure_native.operationalinsights.WorkspaceSkuArgs(name=workspacesku_name),
            retention_in_days=30)

        workspace_shared_keys = pulumi.Output.all(resource_group.name, workspace.name) \
            .apply(lambda args: azure_native.operationalinsights.get_shared_keys(
                resource_group_name=args[0],
                workspace_name=args[1]
            ))

        # Standup Managed KubeEnvironment
        managed_environment = azure_native.app.ManagedEnvironment(kube_env_name,
            app_logs_configuration=azure_native.app.AppLogsConfigurationArgs(
                log_analytics_configuration=azure_native.app.LogAnalyticsConfigurationArgs(
                    customer_id=workspace.customer_id, 
                    shared_key=workspace_shared_keys.apply(lambda r: r.primary_shared_key)
                ),
                destination=managed_environment_destination
            ),
            dapr_ai_connection_string=dapr_ai_connection_string,
            location=location,
            name=container_name,
            resource_group_name=resource_group.name,
            zone_redundant=False)

    def deploy_application(
        container_app_name : str, 
        target_port: int , 
        image_server: str, 
        docker_image_name: str,
        docker_image_repo_path: str, 
        docker_username: str, 
        docker_token: str    
        ):
        container_app = azure_native.app.ContainerApp(container_app_name,
            resource_group_name=resource_group.name,
            managed_environment_id=managed_environment.id, 
            configuration=azure_native.app.ConfigurationArgs(
                ingress=azure_native.app.IngressArgs(
                    external=True,
                    target_port=8020),
                registries=[azure_native.app.RegistryCredentialsArgs(
                    server=image_server, 
                    username=docker_username,  
                    password_secret_ref="pass"
                )], 
                secrets= [azure_native.app.SecretArgs(
                    name="pass", 
                    value=docker_token
                )]
            ), 
            template=azure_native.app.TemplateArgs(
                    containers=[azure_native.app.ContainerArgs(
                        name=docker_image_name, 
                        image=docker_image_repo_path # "repo/image:tag"
                    )]
                )
            
        )
        return pulumi.export("url", container_app.configuration.apply(lambda c: c.ingress).apply(lambda i: i.fqdn))

# https://www.pulumi.com/blog/azure-container-apps/
# https://www.pulumi.com/registry/packages/azure-native/api-docs/app/containerapp/