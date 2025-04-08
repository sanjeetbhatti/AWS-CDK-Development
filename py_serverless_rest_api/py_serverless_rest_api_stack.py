from aws_cdk import (
    Stack,
    aws_apigateway,
    aws_lambda,
    aws_dynamodb
)
from constructs import Construct

class PyServerlessRestApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Creating DynamoDB table that will be accessible inside lambda
        employee_table = aws_dynamodb.TableV2(
            self,
            "EmployeeTable",
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING
            ),
            billing=aws_dynamodb.Billing.on_demand()
        )

        # Creating a lambda
        employee_lambda = aws_lambda.Function(
             self,
             "EmployeeLambda",
             runtime=aws_lambda.Runtime.PYTHON_3_11,
             code=aws_lambda.Code.from_asset("services"), 
             handler="index.handler", # filename.function
             environment={"TABLE_NAME": employee_table.table_name} # adding reference to the table
         )
        
        # Granting access to lambda to perform read & write operations inside the table 
        employee_table.grant_read_write_data(employee_lambda)

        # Building api and attaching it to the stack
        api = aws_apigateway.RestApi(self, "Employee-Api")
        employee_resource = api.root.add_resource("employee")
        
        # Attaching the lambda to the api gateway
        employee_lambda_integration = aws_apigateway.LambdaIntegration(employee_lambda) #lambda integration object from api gateway
        employee_resource.add_method("GET", employee_lambda_integration) # two methods 'get and post' added
        employee_resource.add_method("POST", employee_lambda_integration)
