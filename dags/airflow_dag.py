from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
# from includes.vs_modules.test import hello
from airflow.operators.bash_operator import BashOperator
#
#
args = {
    'owner': 'Annu',
    'start_date': days_ago(1) # make start date in the past
}

dag = DAG(
    dag_id='airflow-dag',
    default_args=args,
    schedule_interval='@daily'# make this workflow happen every day
)

train = BashOperator(
    task_id='train',
    depends_on_past=False,
    bash_command='/Users/annukajla/Documents/sms_modelling/src/pipelines/train_model.py',
    retries=3,
    dag=dag,
)
# serve_commands = """
#     lsof -i tcp:8008 | awk 'NR!=1 {print $2}' | xargs kill;
#     python3 /Users/annukajla/Documents/sms_modelling/src/pipelines/predict_model.py serve
#     """
serve = BashOperator(
    task_id='serve',
    depends_on_past=False,
    bash_command='/Users/annukajla/Documents/sms_modelling/src/pipelines/predict_model.py ',
    retries=3,
    dag=dag,
)

#sets the ordering of the DAG. The >> directs the 2nd task to run after the 1st task. This means that
#download images runs first, then train, then serve.
train >> serve