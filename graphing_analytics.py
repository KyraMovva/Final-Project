import pandas as pd
import rrule_decrypt as rr_d
import cron_decrypt as c_d
import plotly.express as px
import plotly.subplots as sp
import csvfunctions as csvf
import io


def finding_rows_facility_id(keyword):
    fac_num = keyword
    csvf.merge_csvs()
    full_list = pd.read_csv("full_list.csv")

    if fac_num != "all":
        mask = full_list['facility_id'].isin([int(fac_num)])

        masked_df = full_list[mask]

        rrule = using_fac_id_rrule_indiv(masked_df)
        # print(rrule)
        final_df = using_fac_id_cron_indiv(masked_df, rrule)
        return True, final_df
    final_df = all_fac_id_rrule(full_list)
    # final_df = all_fac_id_cron(full_list, rrule_dict)
    return False, final_df


def comparing_alerts(df, typer):
    if typer == "r":
        alert_list = list(df['report_file_name'])
    else:
        alert_list = list(df['file_name'])

    csvf.create_unique_report_names()
    combined_alerts = pd.read_csv("report_names.csv")

    valid_alerts = []

    if alert_list:
        for i in range(len(alert_list)):
            alert_str = str(alert_list[i]).strip().replace(".pdf", "").title().replace("_", " ")
            if (combined_alerts == alert_str).any().any():
                valid_alerts.append(alert_str)
        return valid_alerts
    return None


def check_valid_ind(df):
    valid_inds = []

    for i in df:
        if not pd.isnull(i):
            valid_inds.append(df.index(i))
    return valid_inds


def using_fac_id_rrule_indiv(df):
    rrule_list = list(df['rr_rule'])
    rrule_starts = list(df['start_date'])

    valid_reports = comparing_alerts(df, "r")

    inds = []

    counter = 0
    inds = []
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

    if rrule_list != [] and valid_reports != []:
        rrule_occurrences = {}

        for i in range(len(rrule_list)):
            rrule_occurrences.update({valid_reports[i]: 0})

        for i in rrule_list:
            rrule_start_entry = rrule_starts[rrule_list.index(i)]
            rrule_occurrences[valid_reports[rrule_list.index(i)]] += rr_d.get_occurrences(i, rrule_start_entry)
    return rrule_occurrences


def using_fac_id_cron_indiv(df, rrule_dict):
    if rrule_dict != {}:
        cron_list = list(df['cron_expression'])
        cron_starts = list(df['local_start_at'])

        valid_reports = comparing_alerts(df, "c")

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
        if cron_list == [] and rrule_dict == {}:
            pass
    cron_df = pd.DataFrame(
        {"Reports": [], "Occurrences": []})
    return cron_df


def all_fac_id_rrule(df):
    facility_ids = []

    for i in df["facility_id"]:
        facility_ids.append(i)

    combined_alerts = pd.read_csv("report_names.csv")
    combined_alerts = combined_alerts["Alert Reports!!"].tolist()
    rrule_df = {"Reports": combined_alerts}

    for i in facility_ids:
        rrule_df.update({i: []})
        for j in combined_alerts:
            rrule_df[i].append(0)

    for i in facility_ids:
        mask = df['facility_id'].isin([int(i)])
        masked_df = df[mask]
        valid_reports = comparing_alerts(masked_df, "r")
        valid_cron_reports = comparing_alerts(masked_df, "c")
        valid_reports.extend(valid_cron_reports)
        for j in valid_reports:
            rep_ind = combined_alerts.index(j)
            rp_lst = rrule_df[i]
            rp_lst[rep_ind] += 1
    final_df = pd.DataFrame(rrule_df)
    return final_df



def init(keyword):
    indiv, final_df = finding_rows_facility_id(keyword)

    if indiv:
        final_fig = px.bar(final_df, x="Reports", y="Occurrences", color="Reports", barmode="group")
    else:
        rrule_df = final_df.melt(id_vars='Reports', var_name='Facilities', value_name='Occurrences')
        skip = 0
        interval = 6
        final_fig = sp.make_subplots(rows=interval, cols=1)
        for i in range(6):
            fig1 = px.bar(rrule_df[skip::interval], x="Reports", y="Occurrences", color="Facilities", barmode="group")
            skip += 1

            fig1_trace = []

            for trace in range(len(fig1["data"])):
                fig1_trace.append(fig1["data"][trace])

            for traces in fig1_trace:
                final_fig.add_trace(traces, row=skip, col=1)

        final_fig.update_traces(width=0.05)
        final_fig.update_layout(height=3600, width=2400, title_text="Total Facility With Occurrences", showlegend=False)
    # final_fig.show()

    img_buf = io.BytesIO()
    final_fig.write_image(img_buf, format='png')
    img_buf.seek(0)
    return img_buf


# init("all")

