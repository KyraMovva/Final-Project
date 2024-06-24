import croniter as cr
import datetime as dt
from dateutil import parser

years = []  # initializing list of acceptable years
w_list = []  # initializing list of acceptable days if W is used
now = dt.datetime.now()


# Handles question marks because croniter treats * like ?
def handling_question_marks(str_cron):
    return str_cron.replace("?", "*")


# Checks if there are years in the expression. If there are, creates a list of acceptable years.
def handling_years(str_cron):
    global years
    check = 0
    split_cron = str_cron.split(' ')
    check_list = []
    for num in split_cron[-1]:
        if num == ',' or num == '-':
            if len(check_list) > 3:
                check = 1
                break
            else:
                check_list = []
        else:
            check_list.append(num)
    if len(check_list) > 3:
        check = 1
    if check == 1:
        if "," in split_cron[-1]:
            split_cron2 = split_cron[-1].split(",")
            for x in split_cron2:
                if "-" in x:
                    x = x.split("-")
                    while int(x[0]) <= int(x[1]):
                        years.append(int(x[0]))
                        x[0] = int(x[0]) + 1
                else:
                    years.append(int(x))
        else:
            x = split_cron[-1]
            if "-" in x:
                x = x.split("-")
                while int(x[0]) <= int(x[1]):
                    years.append(int(x[0]))
                    x[0] = int(x[0]) + 1
            else:
                years.append(int(x))
        str_cron = " ".join(split_cron[:-1])
    # This will not work if there is nothing entered for seconds but something for years since years is optional and
    # seconds aren't
    if len(split_cron) > 6 and split_cron[-1] == '*':
        str_cron = " ".join(split_cron[:-1])
    return str_cron


# If there are seconds in the expression, it puts them at the end because that's how croniter takes them
def handling_seconds(str_cron):
    split_cron = str_cron.split(' ')
    if len(split_cron) > 5:
        seconds = split_cron[0]
        split_cron.pop(0)
        split_cron.append(seconds)
        str_cron = " ".join(split_cron)
    return str_cron


# Handles L
def handling_day_of_week(str_cron):
    split_cron = str_cron.split(' ')
    if split_cron[4] == '1':
        split_cron[4] = 'SUN'
        str_cron = " ".join(split_cron)
    elif split_cron[4] == '2':
        split_cron[4] = 'MON'
        str_cron = " ".join(split_cron)
    elif split_cron[4] == '3':
        split_cron[4] = 'TUE'
        str_cron = " ".join(split_cron)
    elif split_cron[4] == '4':
        split_cron[4] = 'WED'
        str_cron = " ".join(split_cron)
    elif split_cron[4] == '5':
        split_cron[4] = 'THU'
        str_cron = " ".join(split_cron)
    elif split_cron[4] == '6':
        split_cron[4] = 'FRI'
        str_cron = " ".join(split_cron)
    elif split_cron[4] == '7' or split_cron[4] == '0' or split_cron[4] == 'L':
        split_cron[4] = 'SAT'
        str_cron = " ".join(split_cron)
    return str_cron


def handling_w(str_cron):
    w_use = str_cron.split(" ")[2]
    if 'W' in w_use:
        num = int(w_use[:-1])
        diffs = {}
        for month in range(1, 13):
            check_date = dt.date(year=now.year, month=month, day=num)
            days_2 = check_date + dt.timedelta(days=-2, hours=0)
            for i in range(5):
                if days_2.month == check_date.month and days_2.weekday() < 4:
                    diffs[abs(days_2.day - num)] = days_2
                days_2 += dt.timedelta(days=1, hours=0)
            w_list.append(diffs[min(list(diffs.keys()))])
            diffs = {}
        for month in range(1, 13):
            check_date = dt.date(year=now.year - 1, month=month, day=num)
            days_2 = check_date + dt.timedelta(days=-2, hours=0)
            for i in range(5):
                if days_2.month == check_date.month and days_2.weekday() < 4:
                    diffs[abs(days_2.day - num)] = days_2
                days_2 += dt.timedelta(days=1, hours=0)
            w_list.append(diffs[min(list(diffs.keys()))])
            diffs = {}
    return str_cron.replace(w_use, '*')


def count_cron_occurrences(str_cron, start_date):
    start_date = parser.parse(start_date)
    str_cron = handling_question_marks(str_cron)
    str_cron = handling_years(str_cron)
    str_cron = handling_seconds(str_cron)
    str_cron = handling_day_of_week(str_cron)
    str_cron = handling_w(str_cron)

    days_30 = now + dt.timedelta(days=-30, hours=0)
    if start_date > days_30:
        days_30 = start_date

    first_occurrence = cr.croniter(str_cron, days_30)
    occurrences_set = {}
    occurrences_set = set(occurrences_set)
    count = 0

    while True:
        next_date = first_occurrence.get_next(dt.datetime)
        if next_date > now:
            break
        if next_date >= days_30:
            if len(years) > 0:
                if len(w_list) != 0:
                    if next_date.year in years and next_date.date() in w_list:
                        occurrences_set.add(next_date)
                        count += 1
                else:
                    if next_date.year in years:
                        occurrences_set.add(next_date)
                        count += 1
            else:
                if len(w_list) != 0:
                    if next_date.date() in w_list:
                        occurrences_set.add(next_date)
                        count += 1
                else:
                    occurrences_set.add(next_date)
                    count += 1
    # for occurrence in occurrences_set:
    #     print(occurrence)
    print(count)
    return count
    # return occurrences_set
    # if you want the count as well
    # return occurrences_set, count


# # Test:
# str_cron = '0 30 9 * * ?'
# try:
#     print(count_cron_occurrences(str_cron, '6/13/2024 0:00:56'))
# except Exception as err:
#     print("Error:" + str(err) + "\nwith " + str_cron)
# #  use new_set = set1.union(set2) to join all the sets
