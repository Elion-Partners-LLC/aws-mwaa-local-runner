from elion.operators.ms_teams import MSTeamsWebhookOperator

MS_TEAMS_CONN_ID = "ms_teams_data_alerts"


def send_task_failure_alert_to_ms_teams(context):
    ms_teams_msg = "Task {task} failed".format(
        task=context.get("task_instance").task_id
    )
    ms_teams_subtitle = "Dag: {dag} | Execution Time: {exec_date}".format(
        dag=context.get("task_instance").dag_id, exec_date=context.get("execution_date")
    )

    failed_alert = MSTeamsWebhookOperator(
        task_id="ms_teams_alert",
        http_conn_id=MS_TEAMS_CONN_ID,
        message=ms_teams_msg,
        subtitle=ms_teams_subtitle,
        button_text="View logs",
        button_url=context.get("task_instance").log_url,
    )

    return failed_alert.execute(context=context)
