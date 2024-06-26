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
    check = 0  # checks if there is or isn't a year
    split_cron = str_cron.split(' ')
    # None of the other categories can have inputs linger than 3 characters
    # Sets Check to 1 if there are 4 or more characters in a row not separated by a - or ,
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
    # If the expression does include years, all the acceptable years are added to the list years
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
    if len(split_cron) > 5:  # Checks for seconds using length as years were already dealt with
        seconds = split_cron[0]
        split_cron.pop(0)
        split_cron.append(seconds)
        str_cron = " ".join(split_cron)
    return str_cron


# Handles possible different values for the day of the week
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


# Handles use of W if it's there
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


# runs all the previous functions and returns a set of occurrences that fulfill the criteria
def count_cron_occurrences(str_cron, start_date):
    start_date = parser.parse(start_date)
    str_cron = handling_question_marks(str_cron)
    str_cron = handling_years(str_cron)
    str_cron = handling_seconds(str_cron)
    str_cron = handling_day_of_week(str_cron)
    str_cron = handling_w(str_cron)

    # If the expression was set to start after 30 days ago, it starts counting from the start date instead
    days_30 = now + dt.timedelta(days=-365, hours=0)
    if start_date > days_30:
        days_30 = start_date

    first_occurrence = cr.croniter(str_cron, days_30)  # starts off the loop
    occurrences_set = {}  # initializes the set
    occurrences_set = set(occurrences_set)  # forces into a set rather than a dict
    count = 0

    while True:
        next_date = first_occurrence.get_next(dt.datetime)  # finds the next date after the first time
        if next_date > now:
            break
        if next_date >= days_30:
            if len(years) > 0:  # If there were years in the expression
                if len(w_list) != 0:  # If there was a W in the expression
                    if next_date.year in years and next_date.date() in w_list:  # Checks against the acceptable years and weekdays
                        occurrences_set.add(next_date)
                        count += 1
                else:  # If there wasn't a W in the expression
                    if next_date.year in years:  # Checks against acceptable years
                        occurrences_set.add(next_date)
                        count += 1
            else:  # If there weren't years in the expression
                if len(w_list) != 0:  # If there was a W in the expression
                    if next_date.date() in w_list: # Checks against acceptable weekdays

                        occurrences_set.add(next_date)
                        count += 1
                else:  # If there wasn't a W in the expression
                    occurrences_set.add(next_date)
                    count += 1
    return count
