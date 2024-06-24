#import necessary packages
from csvfunctions import *

combined_to_file()
#find the path of the excel file from desktop
csv_file = "active_sites.csv"
#read the the excel file
df = pd.read_csv(csv_file)

#get rid of whitespace from column names
df.columns = df.columns.str.strip()

#accessing columns
column1_data = df["facility_id"]
column2_data = df["facility_name"]
column3_data = df["institution_id"]
column4_data = df["institution_name"]


#define the match function
def match_institution_id(facility_id):
    filtered_df = df[df['facility_id'] == facility_id]
    institution_id = filtered_df.iloc[:, -2:-1].values[0]

    return institution_id[0]


def match_institution_name(facility_id):
    filtered_df = df[df['facility_id'] == facility_id]

    institution_name = filtered_df.iloc[:, -1:].values[0]
    return institution_name[0]

def match_facility_name(facility_id):
    filtered_df = df[df['facility_id'] == facility_id]
    facility_name = filtered_df.iloc[:, -3:-1].values[0]

    return facility_name[0]
