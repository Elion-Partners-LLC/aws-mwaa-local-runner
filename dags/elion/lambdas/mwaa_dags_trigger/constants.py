MWAA_ENV_NAME = "airflow-elion"
MWAA_CLI_COMMAND = "dags trigger"

DAG_FILE_MAPPING = (
    # (dag_name, file_prefix, file_suffix)
    ("lease_comps", "raw/compstak/lease_comps/", ".xlsx"),
    ("lease_comps", "raw/manual_lease_comps/", ".xlsx"),
    ("cash_flow", "raw/manual_upload/cashflow/", ".xlsx"),
    ("rent_roll_file", "raw/manual_upload/rent_roll/", ".xlsx"),
    ("greenstreet", "raw/greenstreet/", ".xlsx"),
    ("loan_abstract", "raw/manual_upload/loan_abstracts/", ".xlsx"),
    ("costar_properties_lands_sales_comps", "raw/costar/properties/", ".csv"),
    ("costar_properties_lands_sales_comps", "raw/costar/sales_comps/", ".csv"),
    ("costar_properties_lands_sales_comps", "raw/costar/lands_comps/", ".csv"),
    ("costar_properties_lands_sales_comps", "raw/manual_sales_comps/", ".csv"),
    ("costar_properties_lands_sales_comps", "raw/manual_lands_comps/", ".csv"),
)
