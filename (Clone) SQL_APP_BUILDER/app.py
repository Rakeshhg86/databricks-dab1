import time
import hashlib
import json
import streamlit as st
import pandas as pd
from databricks.sdk.core import Config
from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs
from databricks import sql

CATALOG = "databricks_cookies_dataset_dais_2024"

SCHEMA = "sales"
TABLES = {
    "customers": "c",
    "franchises": "f",
    "suppliers": "s",
    "transactions": "t"
}
NOTEBOOK_RUNNER_PATH = "/Workspace/Shared/Execute_SQL_To_CSV"  # keep consistent with your notebook path

# ---------------- UI SETUP ----------------
st.set_page_config(page_title="Databricks SQL Builder (Apps)", layout="wide")
st.title("SQL Builder & Job Scheduler — Sales schema")
st.caption(f"Catalog: {CATALOG} • Schema: {SCHEMA}")

cfg = Config()
server_hostname = cfg.host

#http_path = st.text_input("SQL Warehouse HTTP Path", placeholder="/sql/1.0/warehouses/XXXX")
http_path="/sql/1.0/warehouses/cd3dcab1137559d4"
using_join = st.toggle("Build a single SQL joining multiple tables", value=True)
primary_table = st.selectbox("Primary table", list(TABLES.keys()), index=0)

# Meta tables (Unity Catalog)
#meta_catalog = st.text_input("Meta Catalog", value="app_meta")
meta_catalog="databricks_app"
#meta_schema  = st.text_input("Meta Schema",  value="vendor")
meta_schema="audit"
config_table = f"{meta_catalog}.{meta_schema}.vendor_extract_config"
audit_table  = f"{meta_catalog}.{meta_schema}.vendor_extract_audit"

# ---------------- SQL WAREHOUSE CONNECTION ----------------
@st.cache_resource
def get_sql_connection(http_path: str):
    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        credentials_provider=lambda: cfg.authenticate,
    )

conn = get_sql_connection(http_path) if http_path else None

def quote_ident(name: str) -> str:
    parts = name.split(".")
    return ".".join([f"`{p}`" for p in parts])

def get_columns(conn, table: str) -> pd.DataFrame:
    q = f"""
    SELECT column_name, data_type
    FROM {quote_ident(CATALOG)}.information_schema.columns
    WHERE table_schema = '{SCHEMA}' AND table_name = '{table}'
    ORDER BY ordinal_position
    """
    with conn.cursor() as cur:
        cur.execute(q)
        return cur.fetchall_arrow().to_pandas()

def build_select_list(selected_cols_by_table):
    items = []
    for tbl, cols in selected_cols_by_table.items():
        alias = TABLES[tbl]
        for col in cols:
            items.append(f"{alias}.`{col}` AS {alias}_{col}")
    return ",\n ".join(items) if items else "*"

def build_from_and_joins(primary_table: str, join_specs: list):
    from_clause = f"FROM {quote_ident(CATALOG)}.{quote_ident(SCHEMA)}.{quote_ident(primary_table)} {TABLES[primary_table]}"
    join_clauses = []
    for spec in join_specs:
        jt  = spec.get("type", "INNER").upper()
        tbl = spec["table"]
        alias = TABLES[tbl]
        on  = spec["on"].strip()
        join_clauses.append(
            f"{jt} JOIN {quote_ident(CATALOG)}.{quote_ident(SCHEMA)}.{quote_ident(tbl)} {alias} ON {on}"
        )
    return "\n".join([from_clause] + join_clauses)

def combine_where_clauses(per_table_where: dict, global_where: str, using_join: bool):
    clauses = []
    if using_join:
        for tbl, expr in per_table_where.items():
            expr = (expr or "").strip()
            if expr:
                clauses.append(expr)
    else:
        for expr in per_table_where.values():
            expr = (expr or "").strip()
            if expr:
                clauses.append(expr)
    if global_where and global_where.strip():
        clauses.append(global_where.strip())
    return " AND ".join([f"({c})" for c in clauses]) if clauses else ""

def build_sql(primary_table, selected_cols_by_table, per_table_where, global_where, using_join, join_specs):
    select_list = build_select_list(selected_cols_by_table)
    if using_join:
        from_joins = build_from_and_joins(primary_table, join_specs)
    else:
        from_joins = f"FROM {quote_ident(CATALOG)}.{quote_ident(SCHEMA)}.{quote_ident(primary_table)} {TABLES[primary_table]}"
    where_clause = combine_where_clauses(per_table_where, global_where, using_join)
    sql_stmt = f"SELECT\n {select_list}\n{from_joins}"
    if where_clause:
        sql_stmt += f"\nWHERE {where_clause}"
    return sql_stmt

# ---------------- Column pickers + per-table WHERE ----------------
selected_cols_by_table = {}
per_table_where = {}
tabs = st.tabs(list(TABLES.keys()))
for i, tbl in enumerate(TABLES.keys()):
    with tabs[i]:
        st.subheader(f"Table: {tbl}")
        if conn:
            cols_df = get_columns(conn, tbl)
            all_cols = list(cols_df["column_name"])
        else:
            all_cols = []
        selected = st.multiselect("Select columns", options=all_cols, default=all_cols[:3], key=f"cols_{tbl}")
        selected_cols_by_table[tbl] = selected
        per_table_where[tbl] = st.text_area(
            "WHERE (optional, for this table)",
            placeholder="e.g., c.country = 'IN' or t.amount > 1000",
            key=f"where_{tbl}"
        )

# ---------------- Join config ----------------
join_specs = []
if using_join:
    st.markdown("---")
    st.subheader("Join configuration")
    st.caption("Example ON: c.customer_id = t.customer_id")
    for tbl, alias in TABLES.items():
        if tbl == primary_table:
            continue
        col = st.columns([2, 1, 3])
        with col[0]:
            enabled = st.checkbox(f"Join {tbl}", key=f"join_enable_{tbl}", value=False)
        with col[1]:
            join_type = st.selectbox("Type", ["INNER", "LEFT", "RIGHT", "FULL"], key=f"join_type_{tbl}")
        with col[2]:
            on_cond = st.text_input("ON condition", key=f"join_on_{tbl}", placeholder=f"{TABLES[primary_table]}.id = {alias}.id")
        if enabled and on_cond.strip():
            join_specs.append({"table": tbl, "type": join_type, "on": on_cond})

# ---------------- Global WHERE ----------------
global_where = st.text_area("Global WHERE (optional)", placeholder="e.g., c.country = 'IN' AND t.amount > 1000")

# ---------------- Build SQL ----------------
sql_stmt = build_sql(primary_table, selected_cols_by_table, per_table_where, global_where, using_join, join_specs)
st.markdown("### Generated SQL")
st.code(sql_stmt, language="sql")

# ---------------- Preview ----------------
st.markdown("---")
st.subheader("Preview (first 10 rows)")
if conn and sql_stmt.strip():
    try:
        with conn.cursor() as cur:
            cur.execute(f"{sql_stmt}\nLIMIT 10")
            preview_df = cur.fetchall_arrow().to_pandas()
        st.dataframe(preview_df, use_container_width=True)
    except Exception as e:
        st.error(f"Preview failed: {e}")
else:
    st.info("Enter the SQL Warehouse HTTP Path to preview.")

# ---------------- Run & Save ----------------
st.markdown("---")
st.subheader("Run & Save")
file_type   = st.selectbox("File type", ["csv", "parquet"], index=0)  # NEW
output_dir  = st.text_input("Output directory (DBFS/ABFSS/S3)", value="/Volumes/databricks_app/build-app/target")
file_basename = st.text_input("File base name (without extension)", value=f"{primary_table}_{int(time.time())}")
delimiter   = st.text_input("Delimiter (CSV only)", value=",")
coalesce_one = st.checkbox("Save as single file (coalesce(1))", value=False)

schedule_enabled = st.checkbox("Schedule (Quartz cron)")
cron_expr = st.text_input("Quartz cron (e.g., 0 0 9 ? * MON-FRI)", value="0 0 9 ? * MON-FRI") if schedule_enabled else None
timezone   = st.text_input("Timezone", value="Asia/Kolkata") if schedule_enabled else None

reuse_job  = st.checkbox("Reuse job when query+options are identical", value=True)

run_now = st.button("Run & Save")

# ---------------- Helpers: meta tables DDL via SQL Warehouse ----------------
def ensure_meta_tables():
    if not conn:
        return
    ddl_config = f"""
    CREATE TABLE IF NOT EXISTS {config_table} (
      signature STRING,
      job_id STRING,
      job_name STRING,
      query_sql STRING,
      file_type STRING,
      delimiter STRING,
      coalesce_one BOOLEAN,
      output_dir STRING,
      file_basename STRING,
      schedule_enabled BOOLEAN,
      cron_expr STRING,
      timezone STRING,
      created_at TIMESTAMP,
      last_run_id STRING,
      target_file_path STRING,
      active BOOLEAN
    ) USING DELTA
    """
    ddl_audit = f"""
    CREATE TABLE IF NOT EXISTS {audit_table} (
      run_id STRING,
      job_id STRING,
      job_name STRING,
      signature STRING,
      status STRING,
      start_time TIMESTAMP,
      end_time TIMESTAMP,
      duration_ms BIGINT,
      records_loaded BIGINT,
      target_path STRING,
      error_message STRING
    ) USING DELTA
    """
    with conn.cursor() as cur:
        cur.execute(ddl_config)
        cur.execute(ddl_audit)

def compute_signature():
    payload = {
        "query_sql": sql_stmt,
        "file_type": file_type,
        "delimiter": delimiter,
        "coalesce_one": bool(coalesce_one),
        "output_dir": output_dir.rstrip("/")
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest(), payload


def find_existing_job_by_signature(signature: str):
    if not conn:
        return None
    q = f"SELECT job_id, job_name FROM {config_table} WHERE signature = '{signature}' AND active = true"
    with conn.cursor() as cur:
        cur.execute(q)
        tbl = cur.fetchall_arrow()
        if tbl:
            df = tbl.to_pandas()
            return df.iloc[0]["job_id"], df.iloc[0]["job_name"]
    return None


def upsert_config(signature: str, job_id: str, job_name: str, payload: dict):
    if not conn:
        return
    with conn.cursor() as cur:
        # Insert or update
        cur.execute(f"""
        MERGE INTO {config_table} AS c
        USING (
          SELECT
            '{signature}' AS signature,
            '{job_id}' AS job_id,
            '{job_name}' AS job_name,
            {json.dumps(sql_stmt)!r} AS query_sql,
            '{payload["file_type"]}' AS file_type,
            '{payload["delimiter"]}' AS delimiter,
            {str(payload["coalesce_one"]).lower()} AS coalesce_one,
            '{payload["output_dir"]}' AS output_dir,
            '{file_basename}' AS file_basename,
            {str(bool(schedule_enabled)).lower()} AS schedule_enabled,
            {json.dumps(cron_expr)!r} AS cron_expr,
            {json.dumps(timezone)!r} AS timezone,
            current_timestamp() AS created_at,
            NULL AS last_run_id,
            NULL AS target_file_path,
            true AS active
        ) s
        ON c.signature = s.signature
        WHEN MATCHED THEN UPDATE SET
          c.job_id = s.job_id,
          c.job_name = s.job_name,
          c.query_sql = s.query_sql,
          c.file_type = s.file_type,
          c.delimiter = s.delimiter,
          c.coalesce_one = s.coalesce_one,
          c.output_dir = s.output_dir,
          c.file_basename = s.file_basename,
          c.schedule_enabled = s.schedule_enabled,
          c.cron_expr = s.cron_expr,
          c.timezone = s.timezone,
          c.active = true
        WHEN NOT MATCHED THEN INSERT *
        """)

def poll_run_status(w, run_id: int, poll_secs: float = 3.0, max_secs: int = 600):
    status_area = st.empty()
    start = time.time()
    while True:
        info = w.jobs.get_run(run_id=run_id)  # <-- use jobs.get_run
        life = info.state.life_cycle_state
        result = info.state.result_state
        status_area.info(f"Job status: {life} (result: {result})")
        if life in ("TERMINATED", "INTERNAL_ERROR") or result in ("SUCCESS", "FAILED", "TIMEDOUT", "CANCELED"):
            return life, result
        if (time.time() - start) > max_secs:
            return life, "TIMEDOUT"
        time.sleep(poll_secs)


def fetch_audit_by_run(run_id: str):
    if not conn:
        return None
    q = f"""
      SELECT status, target_path, records_loaded, duration_ms
      FROM {audit_table}
      WHERE run_id = '{run_id}'
      ORDER BY end_time DESC
      LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(q)
        tbl = cur.fetchall_arrow()
        if tbl:
            return tbl.to_pandas().iloc[0]
    return None


# Ensure meta tables exist
if conn:
    ensure_meta_tables()

# ---------------- Create / Reuse job, trigger run ----------------
def create_job_and_run(w: WorkspaceClient, job_name: str, base_parameters: dict,
                       schedule_enabled: bool, cron_expr: str, timezone: str):
    task = jobs.Task(
        task_key="run_sql_to_file",
        notebook_task=jobs.NotebookTask(
            notebook_path=NOTEBOOK_RUNNER_PATH,
            base_parameters=base_parameters
        )
    )
    
    job_settings = {
             "name": job_name,
             "tasks": [task],
             # NEW: add job parameters that will be resolved at run time
             "parameters": [
                 jobs.JobParameterDefinition(name="job_id",  default="{{job.id}}"),
                 jobs.JobParameterDefinition(name="run_id",  default="{{job.run_id}}"),
                 jobs.JobParameterDefinition(name="job_name", default=job_name),
             ],
         }

    if schedule_enabled:
        job_settings["schedule"] = jobs.CronSchedule(
            quartz_cron_expression=cron_expr,
            timezone_id=timezone,
            pause_status=jobs.PauseStatus.UNPAUSED
        )
    created = w.jobs.create(**job_settings)
    if not schedule_enabled:
        run = w.jobs.run_now(job_id=created.job_id, job_parameters=base_parameters)
        return created.job_id, run.run_id
    else:
        return created.job_id, None

if run_now:
    if not conn:
        st.error("Provide SQL Warehouse HTTP Path to proceed.")
    else:
        try:
            # Build signature and payload
            signature, payload = compute_signature()
            w = WorkspaceClient()

            # Base parameters for notebook
            base_parameters = {
                "query_sql": sql_stmt,
                "output_dir": payload["output_dir"],
                "file_basename": file_basename,
                "file_type": file_type,
                "delimiter": delimiter,
                "coalesce_one": str(bool(coalesce_one)),
                "config_table": config_table,
                "audit_table": audit_table,
                "filters_json": json.dumps({
                    "per_table": per_table_where,
                    "global": global_where
                }),
                # NEW: pass job name explicitly
                "job_name" : f"SQL Export [{signature[:8]}]"             
            }

            # Job naming scheme: deterministic by signature for reuse
            job_name = f"SQL Export [{signature[:8]}]"

          # job_id = None
          # run_id = None

            if reuse_job:
                existing = find_existing_job_by_signature(signature)
                if existing:
                    job_id, job_name_existing = existing
                    st.info(f"Reusing job {job_name_existing} (ID: {job_id})")
                    # Add job_id into parameters for the run
                    run_params = dict(base_parameters)
                    run_params["job_id"] = "{{job.id}}"
                    run_params["run_id"] = "{{job.run_id}}"
                    run_params["job_name"] = job_name 
                    run = w.jobs.run_now(job_id=job_id, job_parameters=run_params)
                    # pass job_parameters
                    run_id = run.run_id
                else:
                    job_id, run_id = create_job_and_run(w, job_name, base_parameters, schedule_enabled, cron_expr, timezone)
            else:
                job_id, run_id = create_job_and_run(w, job_name, base_parameters, schedule_enabled, cron_expr, timezone)

            # Write/Update config for tracking
            upsert_config(signature, job_id, job_name, payload)

            # UI messages           
            if run_id:
                st.success(f"Job ready (ID: {job_id}) and triggered (Run ID: {run_id}).")
                      # NEW: update last_run_id at source-of-truth (config) right away
                try:
                    with conn.cursor() as cur:
                        cur.execute(f"UPDATE {config_table} SET last_run_id = '{run_id}' WHERE signature = '{signature}'")
                    st.info(f"[DEBUG] config.last_run_id set to {run_id}")
                except Exception as e:
                    st.warning(f"[DEBUG] failed to set last_run_id from app: {e}")
                life, result = poll_run_status(w, run_id, poll_secs=3.0)
                st.info(f"Final status: {life} / {result}")
                audit_row = fetch_audit_by_run(run_id)      
                if audit_row is not None:
                    st.markdown("### Output")
                    st.write(f"**Target path:** `{audit_row['target_path']}`")
                    st.write(f"**Records loaded:** {int(audit_row['records_loaded']) if pd.notnull(audit_row['records_loaded']) else 'N/A'}")
                    st.write(f"**Duration (ms):** {int(audit_row['duration_ms']) if pd.notnull(audit_row['duration_ms']) else 'N/A'}")
                    st.caption("Copy the path into DBFS browser or mount location to download.")
                else:
                    st.warning("Run completed but audit record not found yet. Try refreshing.")
            else:
                st.success(f"Scheduled job created (ID: {job_id}). It will run per schedule.")

        except Exception as e:
            st.error(f"Run & Save failed: {e}")
#st.info(f"[DEBUG] from app: job_id={job_id}, run_id={run_id}, job_name={job_name}")

# Show the raw get_run payload to verify server-side sees it
        info = w.jobs.get_run(run_id=run_id)
        st.json({
            "run_id": info.run_id,
            "job_id": info.job_id,
            "state": {
            "life_cycle_state": info.state.life_cycle_state,
            "result_state": info.state.result_state
         }
        })

# Verify what the notebook wrote into audit
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {audit_table} WHERE run_id = '{run_id}' ORDER BY end_time DESC LIMIT 1")
            tbl = cur.fetchall_arrow()
            st.write("[DEBUG] audit row from warehouse:")
            st.dataframe(tbl.to_pandas())

# ---------------- Job history snapshot ----------------
st.markdown("---")
st.subheader("Recent runs")
if conn:
    with conn.cursor() as cur:
        cur.execute(f"""
        SELECT a.end_time, a.status, a.job_name, c.file_type, c.output_dir, c.file_basename, a.target_path, a.records_loaded
        FROM {audit_table} a
        LEFT JOIN {config_table} c ON a.signature = c.signature
        ORDER BY a.end_time DESC
        LIMIT 25
        """)
        hist_tbl = cur.fetchall_arrow()
        hist_df = hist_tbl.to_pandas()
    st.dataframe(hist_df, use_container_width=True)
else:
    st.info("Provide SQL Warehouse HTTP Path to view history.")
