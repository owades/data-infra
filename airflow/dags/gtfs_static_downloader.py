"""
Download the state of CA GTFS files, async version
"""
import requests
import logging
import zipfile
import io
import pathlib
import datetime
import yaml

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import gcsfs
from airflow.utils.email import send_email
import pandas as pd


def make_gtfs_list():
    """
    Read in a list of GTFS urls
    from the main db
    plus metadata
    kwargs:
     catalog = a intake catalog containing an "official_list" item.
    """

    agencies = yaml.safe_load(open("data/agencies.yml"))

    # yaml has form <agency_name>: { agency_name: "", gtfs_schedule_url: [...,] }
    df = pd.DataFrame.from_dict(agencies, orient="index")

    # TODO: handle multiple urls
    # currently stores urls as a list, so get first (and hopefully only) entry
    df["gtfs_schedule_url"] = df["gtfs_schedule_url"].str.get(0)

    # TODO: Figure out what to do with Metro
    # For now, we just take the bus.

    # TODO: Replace URLs with Zip ones.
    # For now we filter, and then remove ones that don't contain
    # zip filters
    df = df[(df.gtfs_schedule_url.str.contains("zip")) & (df.gtfs_schedule_url.notna())]
    return df


def clean_url(url):
    """
    take the list of urls, clean as needed.
    used as a pd.apply, so singleton.
    """
    # LA Metro split requires lstrip
    return url


class NoFeedError(Exception):
    """
    No Feed / Feed Error base
    class. Placeholder for now.
    """

    pass


def download_url(url, itp_id, gcs_project, **kwargs):
    """
    Download a URL as a task item
    using airflow. **kwargs are airflow
    """
    run_time = kwargs["execution_date"]
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/83.0.4103.97 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.warning(f"No feed found for {url}, {err}")
        raise NoFeedError
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        # replace here with s3fs
        fs = gcsfs.GCSFileSystem(project=gcs_project, token="cloud")
        path = f"/tmp/gtfs-data/{run_time}/{int(itp_id)}"
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        z.extractall(path)
        fs.put(
            path, f"gs://gtfs-data/schedule/{run_time}/{int(itp_id)}", recursive=True
        )
    except zipfile.BadZipFile:
        logging.warning(f"failed to zipfile {url}")
        raise NoFeedError


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.datetime(2021, 2, 15),
    "email": ["hunter.owens@dot.ca.gov"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=2),
    "concurrency": 50
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}


dag = DAG(
    dag_id="gtfs-downloader", default_args=default_args, schedule_interval="@daily"
)


def gen_list(**kwargs):
    """
    task callable to generate the list and push into
    xcom
    """
    provider_set = make_gtfs_list().apply(clean_url)
    return provider_set.to_dict("records")


generate_provider_list_task = PythonOperator(
    task_id="generating_provider_list", python_callable=gen_list, dag=dag
)


def downloader(**kwargs):
    provider_set = kwargs["task_instance"].xcom_pull(
        task_ids="generating_provider_list"
    )
    error_agencies = []
    for row in provider_set:
        print(row)
        try:
            download_url(
                row["gtfs_schedule_url"], row["itp_id"], "cal-itp-data-infra", **kwargs
            )
        except Exception as e:
            logging.warn(f"error downloading agency {row['agency_name']}")
            logging.info(e)
            error_agencies.append(row["agency_name"])
            continue
    logging.info(f"error agencies: {error_agencies}")
    # email out error agencies
    email_template = (
        "The follow agencies failed to have GTFS a GTFS feed at"
        "the URL or the Zip File Failed to extract:"
        f"{error_agencies}"
        "{{ ds }}"
    )
    send_email(
        to=["ruth.miller@dot.ca.gov", "hunter.owens@dot.ca.gov"],
        html_content=email_template,
        subject=(
            "Operator GTFS Errors for" f"{datetime.datetime.now().strftime('%Y-%m-%d')}"
        ),
    )


download_to_gcs_task = PythonOperator(
    task_id="downloading_data",
    python_callable=downloader,
    dag=dag,
    provide_context=True,
)

generate_provider_list_task >> download_to_gcs_task
