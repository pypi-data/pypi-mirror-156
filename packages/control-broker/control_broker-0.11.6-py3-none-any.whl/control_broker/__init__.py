'''
# Control Broker

*Give everyone in your organization subsecond security and compliance decisions based on the organization's latest policies.*

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Versions

This `main` branch represents the (unstable) working branch of the repository.
It contains the latest updates, but is probably not what you want if you
definitely want to deploy a working Control Broker.

For previous stable versions, see the [Releases](https://github.com/VerticalRelevance/ControlBrokerEvalEngine-Blueprint/releases) page.

Please note that this software is meant as a starting point and is therefore not production-ready.

## Features

* Runs a Policy as Code service as a serverless AWS application - you bring the policies, and Control Broker helps you store, organize, and use them - plus it helps you monitor, and analyze their usage.
* Defined in the AWS Python CDK for push-button, repeatable deployment.
* Can be invoked from anywhere in your environment that can invoke a Step Function State Machine (i.e. anywhere that can assume a properly permissioned role), including on-premise and various cloud locations.
* Supports policies written for Open Policy Agent (CloudFormation Guard planned).
* Also helps with notifications, auditing, and analysis of discovered compliance issues.

## Example use cases

* [Using the Control Broker from a CodePipeline application pipeline to block deployment of non-compliant CDK resources](https://github.com/VerticalRelevance/control-broker-codepipeline-example)
* [Using the Control Broker to detect non-compliant changes to deployed resources with AWS Config](https://github.com/VerticalRelevance/control-broker-consumer-example-config)
* [Using the Control Broker from a development machine to evaluate IaC against the organization's latest security policies as it is being written](https://github.com/VerticalRelevance/control-broker-consumer-example-local-dev)

## Deploying Your Own Control Broker

<!--### Upload your secret config file--><!--The Control Broker needs some secret values to be available in its environment. These are stored in a Secrets Manager Secret as a JSON--><!--blob, and the Control Broker's deployment mechanisms grab these values as they need to.--><!--Before proceeding, you'll have to copy [our example secrets file](./supplementary_files/) to a secure location on your machine and replace--><!--the values in it with your own. Then, [create a Secret--><!--in Secrets--><!--Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_basic.html#tutorial-basic-step1)--><!--called "control-broker/secret-config" with this JSON text as its value.--><!--![Using the SecretsManager console to create the secret value](docs/diagrams/images/secretsmanager-console-secret-config.png)--><!--![Using the SecretsManager console to name the secret and give it a description](docs/diagrams/images/secretsmanager-console-secret-config-name-page.png)--><!--Here are some helpful hints about what to put in these values:--><!--> Note: You can change the name of the secret that Control Broker uses by changing the value of the "control-broker/secret-config/secrets-manager-secret-id" context variable.-->

### Deploy the CDK app

Install the [AWS CDK Toolkit
v2](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) CLI tool.

If you encounter issues running the `cdk` commands below, check the version of
`aws-cdk-lib` from [./requirements.txt](./requirements.txt) for the exact
version of the CDK library used in this repo. The latest v2 version of the CDK
Toolkit should be compatible, but try installing the CDK Toolkit version
matching `requirements.txt` before trying other things to resolve your issues.

Clone this repo to your machine before proceeding.

Follow the setup steps below to properly configure the environment and first
deployment of the infrastructure.

To manually create a virtualenv on MacOS and Linux:

`$ python3 -m venv .venv`

After the init process completes and the virtualenv is created, you can use the
following step to activate your virtualenv.

`$ source .venv/bin/activate`

If you are on a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

`$ pip install -r requirements.txt`

[Bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-bootstrap) the
cdk app:

`cdk bootstrap`

At this point you can
[deploy](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-deploy) the CDK
app for this blueprint:

`$ cdk deploy`

After running `cdk deploy`, the Control Broker will be set up.

## Next Steps

Try launching one of the [Example use cases](./README.md#example-use-cases)!
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_apigatewayv2_alpha
import constructs


class Api(
    aws_cdk.aws_apigatewayv2_alpha.HttpApi,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.Api",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api_name: typing.Optional[builtins.str] = None,
        cors_preflight: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.CorsPreflightOptions] = None,
        create_default_stage: typing.Optional[builtins.bool] = None,
        default_authorization_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_authorizer: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.IHttpRouteAuthorizer] = None,
        default_domain_mapping: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.DomainMappingOptions] = None,
        default_integration: typing.Optional[aws_cdk.aws_apigatewayv2_alpha.HttpRouteIntegration] = None,
        description: typing.Optional[builtins.str] = None,
        disable_execute_api_endpoint: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_name: (experimental) Name for the HTTP API resource. Default: - id of the HttpApi construct.
        :param cors_preflight: (experimental) Specifies a CORS configuration for an API. Default: - CORS disabled.
        :param create_default_stage: (experimental) Whether a default stage and deployment should be automatically created. Default: true
        :param default_authorization_scopes: (experimental) Default OIDC scopes attached to all routes in the gateway, unless explicitly configured on the route. Default: - no default authorization scopes
        :param default_authorizer: (experimental) Default Authorizer to applied to all routes in the gateway. Default: - No authorizer
        :param default_domain_mapping: (experimental) Configure a custom domain with the API mapping resource to the HTTP API. Default: - no default domain mapping configured. meaningless if ``createDefaultStage`` is ``false``.
        :param default_integration: (experimental) An integration that will be configured on the catch-all route ($default). Default: - none
        :param description: (experimental) The description of the API. Default: - none
        :param disable_execute_api_endpoint: (experimental) Specifies whether clients can invoke your API using the default endpoint. By default, clients can invoke your API with the default ``https://{api_id}.execute-api.{region}.amazonaws.com`` endpoint. Enable this if you would like clients to use your custom domain name. Default: false execute-api endpoint enabled.

        :stability: experimental
        '''
        props = aws_cdk.aws_apigatewayv2_alpha.HttpApiProps(
            api_name=api_name,
            cors_preflight=cors_preflight,
            create_default_stage=create_default_stage,
            default_authorization_scopes=default_authorization_scopes,
            default_authorizer=default_authorizer,
            default_domain_mapping=default_domain_mapping,
            default_integration=default_integration,
            description=description,
            disable_execute_api_endpoint=disable_execute_api_endpoint,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class ControlBroker(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.ControlBroker",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        jsii.create(self.__class__, self, [scope, id])


__all__ = [
    "Api",
    "ControlBroker",
]

publication.publish()
