data "aws_iam_role" "ecs_task_execution_role" {
  name = "DataEngineeringECSTaskRole"
}

resource "aws_cloudwatch_log_group" "log" {
  name              = "/hammer/download_hammer_data"
}

resource "aws_ecs_task_definition" "download_hammer_data" {
  family                   = "download_hammer_data"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 1024 * 2
  task_role_arn            = data.aws_iam_role.ecs_task_execution_role.arn
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn
  container_definitions = jsonencode([
    {
      name  = "download_hammer_data"
      image = "${var.ecr_repository_url}:dag-hammer-task-04-download-hammer-data"
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.log.name
          awslogs-region        = "us-east-2"
          awslogs-create-group  = "true"
          awslogs-stream-prefix = "ecs"
        }
      }
      environment = [
        {
          name  = "DATA_LAKE_S3_BUCKET_NAME",
          value = var.data_lake_s3_bucket_name
        },
        {
          name  = "TEMP_DATA_STORE_S3_BUCKET_NAME",
          value = var.temp_data_store_s3_bucket_name
        },
      ]
    }
  ])
}
