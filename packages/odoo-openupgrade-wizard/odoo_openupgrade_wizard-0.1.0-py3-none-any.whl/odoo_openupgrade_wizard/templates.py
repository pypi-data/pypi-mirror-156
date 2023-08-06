CONFIG_YML_TEMPLATE = """project_name: {{ project_name }}

postgres_image_name: postgres:13
postgres_container_name: {{project_name}}-db

odoo_host_xmlrpc_port: 9069
odoo_default_country_code: FR


odoo_versions:
{%- for odoo_version in odoo_versions %}
  - {{ odoo_version }}
{%- endfor %}

migration_steps:
{%- for step in steps %}
  - name: {{ step['name'] }}
    version: {{ step['version'] }}
    execution_context: {{ step['execution_context'] }}
    complete_name: {{ step['complete_name'] }}
{% endfor %}

workload_settings:

    # porting a module requires 45 minutes minimaly
    port_minimal_time: 45

    # a migration cost more for each version
    port_per_version: 15

    # Porting 120 lines of Python code costs 1 hour
    port_per_python_line_time: 0.5

    # Porting 120 lines of Python code costs 1 hour
    port_per_javascript_line_time: 0.5

    # Porting 10 lines of XML costs 1 minute
    port_per_xml_line_time: 0.10

    # Minimal time for Openupgrade PR
    open_upgrade_minimal_time: 10

    # time for a line of model in the openupgrade_analysis.txt
    openupgrade_model_line_time: 10

    # Time for a line of field in the openupgrade_analysis.txt
    openupgrade_field_line_time: 5

    # Time for a line of XML in the openupgrade_analysis.txt
    openupgrade_xml_line_time: 0.1

"""

REPO_YML_TEMPLATE = """
##############################################################################
## Odoo Repository
##############################################################################

./src/odoo:
  defaults:
    depth: 1
  remotes:
    odoo: https://github.com/odoo/odoo
  target: odoo {{ odoo_version }}-target
  merges:
    - odoo {{ odoo_version }}

##############################################################################
## OpenUpgrade Repository
##############################################################################

./src/openupgrade:
  defaults:
    depth: 1
  remotes:
    OCA: https://github.com/OCA/OpenUpgrade
  target: OCA {{ odoo_version }}-target
  merges:
    - OCA {{ odoo_version }}

{% for org_name, repo_list in orgs.items() %}
##############################################################################
## {{ org_name }} Repositories
##############################################################################
{% for repo in repo_list %}
./src/{{ org_name }}/{{ repo }}:
  defaults:
    depth: 1
  remotes:
    {{ org_name }}: https://github.com/{{ org_name }}/{{ repo }}
  target: {{ org_name }} {{ odoo_version }}-target
  merges:
    - {{ org_name }} {{ odoo_version }}
{% endfor %}
{% endfor %}

"""

PYTHON_REQUIREMENTS_TXT_TEMPLATE = """
{%- for python_librairy in python_libraries -%}
{{ python_librairy }}
{% endfor %}
odoorpc
click-odoo
"""

DEBIAN_REQUIREMENTS_TXT_TEMPLATE = """
git
"""

ODOO_CONFIG_TEMPLATE = ""


# Technical Notes:
# - We set apt-get update || true, because for some version (at least odoo:10)
#   the command update fail, because of obsolete postgresql repository.
DOCKERFILE_TEMPLATE = """
FROM odoo:{{ odoo_version }}
MAINTAINER GRAP, Coop It Easy

# Set User root for installations
USER root

# 1. Make available files in the containers

COPY debian_requirements.txt /debian_requirements.txt

COPY python_requirements.txt /python_requirements.txt

# 2. Install extra debian packages
RUN apt-get update || true &&\
 xargs apt-get install -y --no-install-recommends <debian_requirements.txt

# 3. Install extra Python librairies
RUN {{ python_major_version }}\
 -m pip install -r python_requirements.txt

# Reset to odoo user to run the container
USER odoo
"""

PRE_MIGRATION_SQL_TEMPLATE = ""

POST_MIGRATION_PY_TEMPLATE = """
import logging

_logger = logging.getLogger(__name__)
_logger.info("Executing post-migration.py script ...")

env = env  # noqa: F821

"""

GIT_IGNORE_CONTENT = """
*
!.gitignore
"""

# TODO, this value are usefull for test for analyse between 13 and 14.
# move that values in data/extra_script/modules.csv
# and let this template with only 'base' module.
MODULES_CSV_TEMPLATE = """
base,Base
account,Account Module
web_responsive,Web Responsive Module
"""

ANALYSIS_HTML_TEMPLATE = """
<html>
  <body>
    <h1>Migration Analysis</h1>
    <table border="1" width="100%">
      <thead>
        <tr>
          <th>Initial Version</th>
          <th>Final Version</th>
          <th>Project Name</th>
          <th>Analysis Date</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>{{ ctx.obj["config"]["odoo_versions"][0] }}</td>
          <td>{{ ctx.obj["config"]["odoo_versions"][-1] }}</td>
          <td>{{ ctx.obj["config"]["project_name"] }}</td>
          <td>{{ current_date }}</td>
        </tr>
      </tbody>
    </table>

    <h2>Summary</h2>
    <table border="1" width="100%">
      <thead>
        <tr>
          <th>Module Type</th>
          <th>Module Quantity</th>
          <th>Remaining Hours</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Odoo</td>
          <td>{{ analysis.get_module_qty("odoo") }}</td>
          <td>{{ analysis.workload_hour_text("odoo") }}</td>
        </tr>
        <tr>
          <td>OCA</td>
          <td>{{ analysis.get_module_qty("OCA") }}</td>
          <td>{{ analysis.workload_hour_text("OCA") }}</td>
        </tr>
        <tr>
          <td>Custom</td>
          <td>{{ analysis.get_module_qty("custom") }}</td>
          <td>{{ analysis.workload_hour_text("custom") }}</td>
        </tr>
      </tbody>
      <tfood>
        <tr>
          <th>Total</th>
          <td>{{ analysis.get_module_qty() }}</td>
          <td>{{ analysis.workload_hour_text() }}</td>
        </tr>
      </tfood>
    </table>

    <h2>Details</h2>
    <table border="1" width="100%">
      <thead>
        <tr>
          <th>&nbsp;</th>
{%- for odoo_version in ctx.obj["config"]["odoo_versions"] -%}
          <th>{{ odoo_version }}</th>
{% endfor %}

        </tr>
      </thead>
      <tbody>
{% set ns = namespace(
  current_repository='',
  current_module_type='',
) %}
{% for odoo_module in analysis.modules %}

<!-- ---------------------- -->
<!-- Handle New Module Type -->
<!-- ---------------------- -->

  {% if (
    ns.current_module_type != odoo_module.module_type
    and odoo_module.module_type != 'odoo') %}
    {% set ns.current_module_type = odoo_module.module_type %}
        <tr>
          <th colspan="{{1 + ctx.obj["config"]["odoo_versions"]|length}}">
            {{ ns.current_module_type}}
          </th>
        <tr>
  {% endif %}

<!-- -------------------- -->
<!-- Handle New Repository-->
<!-- -------------------- -->

  {% if ns.current_repository != odoo_module.repository %}
    {% set ns.current_repository = odoo_module.repository %}
        <tr>
          <th colspan="{{1 + ctx.obj["config"]["odoo_versions"]|length}}">
            {{ ns.current_repository}}
          </th>
        <tr>
  {% endif %}

<!-- -------------------- -->
<!-- Display Module Line  -->
<!-- -------------------- -->

        <tr>
          <td>{{odoo_module.name}}
          </td>
  {% for version in odoo_module.analyse.all_versions %}
    {% set module_version = odoo_module.get_module_version(version) %}
    {% if module_version %}
      {% set size_text = module_version.get_size_text() %}
      {% set analysis_text = module_version.get_analysis_text() %}
      {% set workload = module_version.workload %}

          <td style="background-color:{{module_version.get_bg_color()}};">
            {{module_version.get_text()}}

      {% if workload %}
        <span style="background-color:lightblue;">
          ({{ module_version.workload_hour_text()}})
        </span>
      {% endif %}
      {% if size_text %}
        <br/>
        <span style="color:gray;font-size:11px;font-family:monospace;">
          ({{ size_text}})
        </span>
      {% endif %}
      {% if analysis_text %}
        <br/>
        <span style="color:gray;font-size:11px;font-family:monospace;">
          <a href="{{module_version.analysis_url()}}" target="_blank">
          ({{ analysis_text}})
          </a>
        </span>
      {% endif %}

          </td>
    {% else %}
          <td style="background-color:gray;">&nbsp;</td>
    {% endif %}
  {% endfor %}
        </tr>

{% endfor %}

      </tbody>
    </table>
  </body>
</html>
"""
