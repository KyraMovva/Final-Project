import datetime as dt
from dateutil import rrule, parser


def get_occurrences(rrule_string, dtstart_string):
    try:
        # Parses through DTSTART to get the start date at a datetime object
        # https://dateutil.readthedocs.io/en/stable/parser.html
        dtstart_string = str(dtstart_string)  # making sure it's a string
        dtstart = parser.parse(dtstart_string.split(':')[1])  # the splitting and indexing removes the DTSTART: part

        # Uses the rrule as a string and the above dtstart to now make a list of every occurrence
        # https://dateutil.readthedocs.io/en/stable/rrule.html#rrulestr-examples
        rule = rrule.rrulestr(rrule_string, dtstart=dtstart)

        # finds today's date in the time zone of the dtstart
        # https://dateutil.readthedocs.io/en/stable/parser.html
        now = dt.datetime.now(dtstart.tzinfo)
        days_30 = now + dt.timedelta(days=-30, hours=0)

        total = 0
        # Print each occurrence if it is after 30 days ago
        # Breaks the loop when you reach current time
        for occurrence in rule:
            if occurrence > days_30:
                if occurrence > now:
                    break
                total += 1
                # print(occurrence)
        return total

    except Exception as err:
        print("Error:" + str(err) + "\nwith " + str(rrule_string) + " at " + str(dtstart_string))


# Test:
# get_occurrences('RRULE:FREQ=MONTHLY;UNTIL=20250501T235900Z;BYMONTHDAY=01;BYHOUR=00;BYMINUTE=00', 'RT:20240115T090000Z')
