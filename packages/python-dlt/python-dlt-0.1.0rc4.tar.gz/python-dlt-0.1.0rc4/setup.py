# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dlt',
 'dlt.cli',
 'dlt.common',
 'dlt.common.configuration',
 'dlt.common.normalizers.json',
 'dlt.common.normalizers.names',
 'dlt.common.runners',
 'dlt.common.schema',
 'dlt.common.storages',
 'dlt.dbt_runner',
 'dlt.extractors',
 'dlt.extractors.generator',
 'dlt.loaders',
 'dlt.loaders.dummy',
 'dlt.loaders.gcp',
 'dlt.loaders.redshift',
 'dlt.pipeline',
 'dlt.unpacker',
 'examples',
 'examples.schemas',
 'examples.sources']

package_data = \
{'': ['*'],
 'examples': ['data/*', 'data/rasa_trackers/*', 'data/singer_taps/*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'cachetools>=5.2.0,<6.0.0',
 'hexbytes>=0.2.2,<0.3.0',
 'json-logging==1.4.1rc0',
 'jsonlines>=2.0.0,<3.0.0',
 'pendulum>=2.1.2,<3.0.0',
 'prometheus-client>=0.11.0,<0.12.0',
 'requests>=2.26.0,<3.0.0',
 'semver>=2.13.0,<3.0.0',
 'sentry-sdk>=1.4.3,<2.0.0',
 'simplejson>=3.17.5,<4.0.0']

extras_require = \
{'dbt': ['GitPython>=3.1.26,<4.0.0',
         'dbt-core==1.0.6',
         'dbt-redshift==1.0.1',
         'dbt-bigquery==1.0.0'],
 'gcp': ['grpcio==1.43.0', 'google-cloud-bigquery>=2.26.0,<3.0.0'],
 'postgres': ['psycopg2-binary>=2.9.1,<3.0.0'],
 'redshift': ['psycopg2-binary>=2.9.1,<3.0.0']}

entry_points = \
{'console_scripts': ['dlt = dlt.cli.dlt:main']}

setup_kwargs = {
    'name': 'python-dlt',
    'version': '0.1.0rc4',
    'description': 'DLT is an open-source python-native scalable data loading framework that does not require any devops efforts to run.',
    'long_description': '# Quickstart Guide: Data Load Tool (DLT)\n\n## **TL;DR: This guide shows you how to load a JSON document into Google BigQuery using DLT.**\n\n![](docs/DLT-Pacman-Big.gif)\n\n*Please open a pull request [here](https://github.com/scale-vector/dlt/edit/master/QUICKSTART.md) if there is something you can improve about this quickstart.*\n\n## 1. Grab the demo\n\na. Clone the example repository:\n```\ngit clone https://github.com/scale-vector/dlt-quickstart-example.git\n```\n\nb. Enter the directory:\n```\ncd dlt-quickstart-example\n```\n\nc. Open the files in your favorite IDE / text editor:\n- `data.json` (i.e. the JSON document you will load)\n- `credentials.json` (i.e. contains the credentials to our demo Google BigQuery warehouse)\n- `quickstart.py` (i.e. the script that uses DLT)\n\n## 2. Set up a virtual environment\n\na. Ensure you are using either Python 3.8 or 3.9:\n```\npython3 --version\n```\n\nb. Create a new virtual environment:\n```\npython3 -m venv ./env\n```\n\nc. Activate the virtual environment:\n```\nsource ./env/bin/activate\n```\n\n## 3. Install DLT and support for the target data warehouse\n\na. Install DLT using pip:\n```\npip3 install python-dlt\n```\n\nb. Install support for Google BigQuery:\n```\npip3 install python-dlt[gcp]\n```\n\n## 4. Configure DLT\n\na. Import necessary libaries\n```\nimport base64\nimport json\nfrom dlt.common.utils import uniq_id\nfrom dlt.pipeline import Pipeline, GCPPipelineCredentials\n```\n\nb. Create a unique prefix for your demo Google BigQuery table\n```\nschema_prefix = \'demo_\' + uniq_id()[:4]\n```\n\nc. Name your schema\n```\nschema_name = \'example\'\n```\n\nd. Name your table\n```\nparent_table = \'json_doc\'\n```\n\ne. Specify your schema file location\n```\nschema_file_path = \'schema.yml\'\n```\n\nf. Load credentials\n```\nwith open(\'credentials.json\', \'r\') as f:\n    gcp_credentials_json = json.load(f)\n\n# Private key needs to be decoded (because we don\'t want to store it as plain text)\ngcp_credentials_json["private_key"] = bytes([_a ^ _b for _a, _b in zip(base64.b64decode(gcp_credentials_json["private_key"]), b"quickstart-sv"*150)]).decode("utf-8")\ncredentials = GCPPipelineCredentials.from_services_dict(gcp_credentials_json, schema_prefix)\n```\n\n## 5. Create a DLT pipeline\n\na. Instantiate a pipeline\n```\npipeline = Pipeline(schema_name)\n```\n\nb. Create the pipeline with your credentials\n```\npipeline.create_pipeline(credentials)\n```\n\n## 6. Load the data from the JSON document\n\na. Load JSON document into a dictionary\n```\nwith open(\'data.json\', \'r\') as f:\n    data = json.load(f)\n```\n\n## 7. Pass the data to the DLT pipeline\n\na. Extract the dictionary into a table\n```\npipeline.extract(iter(data), table_name=parent_table)\n```\n\nb. Unpack the pipeline into a relational structure\n```\npipeline.unpack()\n```\n\nc. Save schema to `schema.yml` file\n```\nschema = pipeline.get_default_schema()\nschema_yaml = schema.as_yaml(remove_default=True)\nwith open(schema_file_path, \'w\') as f:\n    f.write(schema_yaml)\n```\n\n\n## 8. Use DLT to load the data\n\na. Load\n```\npipeline.load()\n```\n\nb. Make sure there are no errors\n```\ncompleted_loads = pipeline.list_completed_loads()\n# print(completed_loads)\n# now enumerate all complete loads if we have any failed packages\n# complete but failed job will not raise any exceptions\nfor load_id in completed_loads:\n    print(f"Checking failed jobs in {load_id}")\n    for job, failed_message in pipeline.list_failed_jobs(load_id):\n        print(f"JOB: {job}\\nMSG: {failed_message}")\n```\n\nc. Run the script:\n```\npython3 quickstart.py\n```\n\nd. Inspect `schema.yml` that has been generated:\n```\nvim schema.yml\n```\n\n## 9. Query the Google BigQuery table\n\na. Run SQL queries\n```\ndef run_query(query):\n    df = c._execute_sql(query)\n    print(query)\n    print(list(df))\n    print()\n\nwith pipeline.sql_client() as c:\n\n    # Query table for parents\n    query = f"SELECT * FROM `{schema_prefix}_example.json_doc`"\n    run_query(query)\n\n    # Query table for children\n    query = f"SELECT * FROM `{schema_prefix}_example.json_doc__children` LIMIT 1000"\n    run_query(query)\n\n    # Join previous two queries via auto generated keys\n    query = f"""\n        select p.name, p.age, p.id as parent_id,\n            c.name as child_name, c.id as child_id, c._dlt_list_idx as child_order_in_list\n        from `{schema_prefix}_example.json_doc` as p\n        left join `{schema_prefix}_example.json_doc__children`  as c\n            on p._dlt_id = c._dlt_parent_id\n    """\n    run_query(query)\n```\n\nb. See results like the following\n\ntable: json_doc\n```\n{  "name": "Ana",  "age": "30",  "id": "456",  "_dlt_load_id": "1654787700.406905",  "_dlt_id": "5b018c1ba3364279a0ca1a231fbd8d90"}\n{  "name": "Bob",  "age": "30",  "id": "455",  "_dlt_load_id": "1654787700.406905",  "_dlt_id": "afc8506472a14a529bf3e6ebba3e0a9e"}\n```\n\ntable: json_doc__children\n```\n    # {"name": "Bill", "id": "625", "_dlt_parent_id": "5b018c1ba3364279a0ca1a231fbd8d90", "_dlt_list_idx": "0", "_dlt_root_id": "5b018c1ba3364279a0ca1a231fbd8d90",\n    #   "_dlt_id": "7993452627a98814cc7091f2c51faf5c"}\n    # {"name": "Bill", "id": "625", "_dlt_parent_id": "afc8506472a14a529bf3e6ebba3e0a9e", "_dlt_list_idx": "0", "_dlt_root_id": "afc8506472a14a529bf3e6ebba3e0a9e",\n    #   "_dlt_id": "9a2fd144227e70e3aa09467e2358f934"}\n    # {"name": "Dave", "id": "621", "_dlt_parent_id": "afc8506472a14a529bf3e6ebba3e0a9e", "_dlt_list_idx": "1", "_dlt_root_id": "afc8506472a14a529bf3e6ebba3e0a9e",\n    #   "_dlt_id": "28002ed6792470ea8caf2d6b6393b4f9"}\n    # {"name": "Elli", "id": "591", "_dlt_parent_id": "5b018c1ba3364279a0ca1a231fbd8d90", "_dlt_list_idx": "1", "_dlt_root_id": "5b018c1ba3364279a0ca1a231fbd8d90",\n    #   "_dlt_id": "d18172353fba1a492c739a7789a786cf"}\n```\n\nSQL result:\n```\n    # {  "name": "Ana",  "age": "30",  "parent_id": "456",  "child_name": "Bill",  "child_id": "625",  "child_order_in_list": "0"}\n    # {  "name": "Ana",  "age": "30",  "parent_id": "456",  "child_name": "Elli",  "child_id": "591",  "child_order_in_list": "1"}\n    # {  "name": "Bob",  "age": "30",  "parent_id": "455",  "child_name": "Bill",  "child_id": "625",  "child_order_in_list": "0"}\n    # {  "name": "Bob",  "age": "30",  "parent_id": "455",  "child_name": "Dave",  "child_id": "621",  "child_order_in_list": "1"}\n```\n\n## 10. Next steps\n\na. Replace `data.json` with data you want to explore\n\nb. Check that the inferred types are correct in `schema.yml`\n\nc. Set up your own Google BigQuery warehouse (and replace the credentials)\n\nd. Use this new clean staging layer as the starting point for a semantic layer / analytical model (e.g. using dbt)\n',
    'author': 'ScaleVector',
    'author_email': 'services@scalevector.ai',
    'maintainer': 'Marcin Rudolf',
    'maintainer_email': 'marcin@scalevector.ai',
    'url': 'https://github.com/scale-vector',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
