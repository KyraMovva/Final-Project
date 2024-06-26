# import necessary libraries
import pandas as pd
import rrule_decrypt as rr_d
import cron_decrypt as c_d
import plotly.express as px
import plotly.subplots as sp
import csvfunctions as csvf
import io


# finding the rows based on their facility id and filters
# calls main functions and returns a boolean on whether the graph outputted is individual or total
def finding_facility(keyword):
    fac_num = keyword
    csvf.merge_csvs()
    full_list = pd.read_csv("full_list.csv")

    if fac_num != "all":
        mask = full_list['facility_id'].isin([int(fac_num)])

        masked_df = full_list[mask]

        rrule = rrule_indiv_reports(masked_df)
        final_df = cron_indiv_reports(masked_df, rrule)
        return True, final_df
    final_df = all_reports(full_list)
    return False, final_df


# compares the alerts and report names in each row
# calls a function from a different file to create a formatted file of all of the report names
# the csv is read and the program
# ensures that none of them are blank before
# RETURNS LIST OF VALID INDEXES OF FROM the facility thign
def comparing_alerts(df, typer):
    if typer == "r":
        alert_list = list(df['report_file_name'])
    else:
        alert_list = list(df['file_name'])

    combined_alerts = pd.read_csv("report_names.csv")
    reports = combined_alerts["Alert Reports:"].tolist()

    formatted_reports = []

    for i in reports:
        formatted_reports.append(i.strip().replace(".pdf", "").replace("_", " ").title())

    inds_from_csv = []
    valid_report_inds = []

    # try:
    # print("begin loop")
    if alert_list:
        for i in range(len(alert_list)):
            if not pd.isnull(alert_list[i]):
                # print("str", str(alert_list[i]))
                alert_str = str(alert_list[i]).strip().replace(".pdf", "").replace("_", " ").title()
                # print("li", alert_list)
                # print("st", alert_str)
                if alert_str in formatted_reports:
                    # print("ind", formatted_reports.index(alert_str))
                    valid_report_inds.append(i)
                    inds_from_csv.append(formatted_reports.index(alert_str))
        return valid_report_inds, inds_from_csv
    # except Exception as e:
    #     print("ok", e)
    #     return []


# uses the facility id and rrule to get and return an individual
# pandas dataframe for formatting and graphing
def rrule_indiv_reports(df):
    og_rrule_list = list(df['rr_rule'])
    og_rrule_starts = list(df['start_date'])

    valid_report_inds, inds_from_csv = comparing_alerts(df, "r")
    reports = pd.read_csv("report_names.csv")
    report_names = reports["Alert Reports:"].tolist()
    # print("v", valid_report_inds, len(valid_report_inds))
    # print("l", og_rrule_list, len(og_rrule_list))

    # print("r", report_names, len(report_names))

    rrule_list = []
    rrule_starts = []
    reports = []

    for i in valid_report_inds:
        rrule_list.append(og_rrule_list[i])
        rrule_starts.append(og_rrule_starts[i])

    for i in inds_from_csv:
        reports.append(report_names[i])

    counter = 0
    inds = []

    # loops through the list of rrule statements and checks if they are null
    # (meaning that there would be a cron expression instead)
    for i in rrule_list:
        if pd.isnull(i):
            inds.append(rrule_list.index(i))
            rrule_list.remove(i)
            rrule_starts.remove(i)
            i = str(i) + str(counter)
            rrule_list.insert(inds[-1], i)
            rrule_starts.insert(inds[-1], i)
            counter += 1
    inds.sort(reverse=True)

    for i in inds:
        rrule_starts.pop(i)
        rrule_list.pop(i)

    rrule_occurrences = {}

    # checks if there
    if rrule_list != [] and valid_report_inds != []:
        rrule_occurrences = {}

        # print(valid_report_inds)
        # print(rrule_list)

        for i in range(len(rrule_list)):
            rrule_occurrences.update({reports[i]: 0})

        for i in rrule_list:
            rrule_start_entry = rrule_starts[rrule_list.index(i)]
            rrule_occurrences[reports[rrule_list.index(i)]] += rr_d.get_occurrences(i, rrule_start_entry)
    return rrule_occurrences


# uses the facility id to count cron occurrences and append those to a dictionary to turn it into a pandas dataframe
# validates reports, loops through and gets rid of all blank entries,
# then appends to the dictionary using a function from the cron_decrypt
def cron_indiv_reports(df, rrule_dict):
    og_cron_list = list(df['cron_expression'])
    og_cron_starts = list(df['local_start_at'])
    if og_cron_list:
        valid_report_inds, inds_from_csv = comparing_alerts(df, "r")
        reports = pd.read_csv("report_names.csv")
        report_names = reports["Alert Reports:"].tolist()

        cron_list = []
        cron_starts = []
        valid_reports = []

        for i in valid_report_inds:
            cron_list.append(og_cron_list[i])
            cron_starts.append(og_cron_starts[i])

        for i in inds_from_csv:
            valid_reports.append(report_names[i])

        counter = 0
        inds = []
        for i in cron_list:
            if pd.isnull(i):
                inds.append(cron_list.index(i))
                cron_list.remove(i)
                cron_starts.remove(i)
                i = str(i) + str(counter)
                cron_list.insert(inds[-1], i)
                cron_starts.insert(inds[-1], i)
                counter += 1
        inds.sort(reverse=True)

        for i in inds:
            cron_starts.pop(i)
            cron_list.pop(i)

        if cron_list != [] and valid_reports != []:
            for i in range(len(cron_list)):
                if valid_reports[i] in list(rrule_dict.keys()):
                    pass
                else:
                    rrule_dict.update({valid_reports[i]: 0})

            index = 0
            while index < len(cron_list):
                i = cron_list[index]
                cron_start_entry = cron_starts[index]
                rrule_dict[valid_reports[index]] += c_d.count_cron_occurrences(i, cron_start_entry)
                cron_starts.pop(index)
                valid_reports.pop(index)
                cron_list.pop(index)
            cron_df = pd.DataFrame(
                {"Reports": list(rrule_dict.keys()), "Occurrences": list(rrule_dict.values())})
            return cron_df
    cron_df = pd.DataFrame(
        {"Reports": list(rrule_dict.keys()), "Occurrences": list(rrule_dict.values())})
    return cron_df


# gets a formatted dataframe with all of the reports and their occurrences
# loops through facilities and saves alerts to each facility list
# the most inefficient part of the code
def all_reports(df):
    facility_ids = []

    for i in df["facility_id"]:
        facility_ids.append(i)

    combined_alerts = pd.read_csv("report_names.csv")
    combined_alerts = combined_alerts["Alert Reports:"].tolist()
    rrule_df = {"Reports": combined_alerts}

    for i in facility_ids:
        rrule_df.update({i: []})
        for j in combined_alerts:
            rrule_df[i].append(0)

    # print("df", rrule_df)

    for i in set(facility_ids):
        # print("i", i)
        single_df = df[df['facility_id'] == int(i)]
        # print("si", single_df)
        occurrences_dict = rrule_indiv_reports(single_df)
        # print("o", occurrences_dict)
        full_df = cron_indiv_reports(single_df, occurrences_dict)
        # print("e", full_df)
        full_report_names = full_df["Reports"].tolist()
        # print("f", full_report_names)
        for j in full_report_names:
            # print("j", j)
            # print("s", combined_alerts.index(j))
            j = j.title()
            rrule_df[i][combined_alerts.index(j)] += full_df["Occurrences"][full_report_names.index(j)]
    final_df = pd.DataFrame(rrule_df)
    # print("r", rrule_df)
    return final_df


# initial function
# creates a csv of all the report names
# if individual, returns a simple bar graph
# if total, returns 6 different subplots to conserve space
# writes the graph to an image buffer and returns it for the tkinter GUI
def init(keyword):
    csvf.create_unique_report_names()
    indiv, final_df = finding_facility(keyword)
    if indiv:
        final_fig = px.bar(final_df, x="Reports", y="Occurrences", color="Reports", barmode="group")
    else:
        rrule_df = final_df.melt(id_vars='Reports', var_name='Facilities', value_name='Occurrences')
        skip = 0
        interval = 1
        final_fig = sp.make_subplots(rows=interval, cols=1)
        for i in range(interval):
            fig1 = px.bar(rrule_df[skip::interval], x="Reports", y="Occurrences", color="Facilities", barmode="group")
            skip += 1

            for trace in fig1.data:
                final_fig.add_trace(trace, row=i+1, col=1)

        final_fig.update_traces(width=0.05)
        final_fig.update_layout(height=600, width=1200, title_text="Total Facility With Occurrences")

    # final_fig.show()
    img_buf = io.BytesIO()
    final_fig.write_image(img_buf, format='png')
    img_buf.seek(0)
    return img_buf


# init("all")

