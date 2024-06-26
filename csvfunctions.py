import pandas as pd
from functools import *


# Pandas display options
display = pd.options.display
display.max_columns = 6
display.max_rows = 10
display.max_colwidth = 222
display.width = None

# Reading various csvs given
job_table = pd.read_csv("job.csv")

tempo_worn = pd.read_csv("tempo_worn.csv")

facility = pd.read_csv("facility.csv")

job_table_spliced = (job_table[['facility_id', "cron_expression", "file_name", "recurrence", "local_start_at"]])
job_table_spliced = job_table_spliced[job_table_spliced['recurrence'].astype(str).str.contains("1")]


tempo_worn_spliced = tempo_worn[["facility_id", "institution_id", "rr_rule", "start_date", "report_file_name"]]

active_facilities = facility[["id", "facility_name", "institution_id"]].rename(columns={"id": "facility_id"})

inst_table = pd.read_csv("institution.csv")

inst_spliced = inst_table[["id", "institution_name"]].rename(columns={"id": "institution_id"})
active_sites = pd.merge(active_facilities, inst_spliced, how='left')

sorted_tab = active_sites.sort_values("institution_id")


# Merges to make a full list of all active facilities with their cron and rrule expressions
def merge_csvs():
    active_jobs = pd.merge(sorted_tab, job_table_spliced, how="left")

    active_tempos = pd.merge(sorted_tab, tempo_worn_spliced, how="left")

    full_list = pd.concat([active_tempos, active_jobs], ignore_index=True)
    full_list = full_list.sort_values("facility_id")
    full_list.drop_duplicates(inplace=True)
    full_list.to_csv("full_list.csv", sep=',', index=False, encoding='utf-8')


# Returns a set with the unique report names
def create_unique_report_names():
    # unique_report_names = job_table_spliced['file_name'].to_string(index=False).split("\n")
    # uni = tempo_worn_spliced["report_file_name"].to_string(index=False).split("\n")
    # unique_report_names.extend(uni)
    unique_report_names = pd.read_csv("report_names.csv")["Alert Reports:"].tolist()
    for x in unique_report_names:
        unique_report_names[unique_report_names.index(x)] = x.strip().replace(".pdf", "").replace("_", " ").title()
    unique_report_names = reduce(lambda re, x: re+[x] if x not in re else re, unique_report_names, [])
    with open("report_names.csv", "w") as f:
        f.write('Alert Reports:\n')
        for items in unique_report_names:
            f.write('%s\n' % items)


# Combines facility and institution csvs into one dataframe called active sites and returns the table sorted by
# institution id
def combined_active_facilities():
    facility = pd.read_csv("facility.csv")

    active_facilities = facility[["id", "facility_name", "institution_id"]].rename(columns={"id": "facility_id"})

    inst_table = pd.read_csv("institution.csv")

    inst_spliced = inst_table[["id", "institution_name"]].rename(columns={"id": "institution_id"})
    active_sites = pd.merge(active_facilities, inst_spliced, how='left')

    sorted_tab = active_sites.sort_values("institution_id")
    return sorted_tab


# Writes the active sites dataframe to a csv file
def combined_to_file():
    sorted_t = combined_active_facilities()
    sorted_t.to_csv("active_sites.csv", sep=',', index=False, encoding='utf-8')


# Gets the active site ids and names and returns them in a formatted list
def active_facility_id_name():
    sorted_t = combined_active_facilities()

    id_list = sorted_t['facility_id'].to_string(index=False).split("\n")
    name_list = sorted_t['facility_name'].to_string(index=False).split("\n")

    final_list = []

    for x in range(len(id_list)):
        id_list[x] = id_list[x].strip().title()
        name_list[x] = name_list[x].strip().title()
        final_list.append(id_list[x] + " - " + name_list[x])

    return final_list
