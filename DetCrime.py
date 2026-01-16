"""
DetroitCrime.py will take RMS_Crime_Incidents.csv from the Detroit Open Data portal and pull out all of the crimes committed in the list of neighborhoods defined lower in the file. It will then write them to 
Detroit_Crime_Clients.csv and a separate CSV for each neighborhood. It takes a JSON file to determine what column to pull by, which rows to pull and what years if provided. If no years are provided, it defaults to
2020 through the current year.

Matches are performed with regular expression matching. So ".*ASSAULT" in the pull_list will return "ASSAULT" and "AGGRAVATED ASSAULT"

JSON format:
{
    "method": neighborhood/nearest_intersection/zip_code/police_precinct/offense_category as a string
    "keep_blank_loc" : True/False as a string
    "pull_list" : What in the column heading you want to search for as a list of strings
    "start_year" : When to begin, as a string. Optional
    "end_year" : When to stop, as a string. Optional, but must be present if start_year is used
}

{
    "method" : "zip_code",
    "keep_blank_loc" : "True"
    "pull_list" : ["48221", "48219"],
    "start_year" : "2019",
    "end_year" : "2025"
}
    

Version: 1.1.1
Date: 1/13/2026
Python Version: 3.14.2
Author: Alan Mullin
"""
import os, sys, csv, datetime, argparse, json, re
from operator import itemgetter

#
# GetNeighborhoodNames() looks in the RMS_Crime_Incidents.csv file and pulls out all the unique neighborhood names.
# Known issue: for some reason, it inserts a string "nan" in between 'Downtown' and 'Outer Drive-Hayes'. It does not\
# appear to be in the original data, and when you print the list, it is not treated as a string. EG: [...,'Downtown',nan,'Outer Drive-Hayes',...]
#
def GetNeighborhoodNames():
        import pandas
        
        print(f"Beginning read of RMS_Crime_Incidents.csv...")
        
        df = pandas.read_csv("RMS_Crime_Incidents.csv")
        neighborhood_names = df['neighborhood'].unique()
        num_names = df['neighborhood'].nunique()
        
        print(f"Found {num_names} neighborhood names: {neighborhood_names}")
        with open("Neighborhood_List_All.txt","w") as outfile:
            for h in neighborhood_names:
                print(f"{h}")
                outfile.write(str(h) + '\n')
        outfile.close()

#
# SetSort() loads the desired JSON file and returns a list of what to sort.. zip codes, neighborhoods, or precincts.
# It returns the JSON object
# Single digit precinct numbers have leading zeroes that MUST be in the JSON: "08" instead of "8"
#
def SetSort(fname='default.json'):    
    with open(fname,'r') as file:
        data = json.load(file)
        
        keys = data.keys()
        if 'method' not in keys or 'pull_list' not in keys:
            print(f"{fname} is not properly formatted...")
            return []
        
        method = data['method']
        match method:
            case "zip_code":
                print(f"Pulling ZIP Codes from {fname}...")
            case "neighborhood":
                print(f"Pulling neighborhoods from {fname}...")
            case "report_number":
                print(f"Pullin report numbers from {fname}...")
            case "police_precinct":
                print(f"Pulling precincts from {fname}...")
            case "offense_category":
                print(f"Pulling offense categories from {fname}...")
            case "offense_description":
                print(f"Pulling offense descriptions from {fname}...")
            case "nearest_intersection":
                print(f"Pulling nearest intersections from {fname}...")                
            case _:
                print(f"Invalid or unknown method provided.")
                return []
        
        return data

def main():
    start_time = datetime.datetime.now()
    crimes = []
    crimes_total = 0
    sort_keepblank = False
    
    parser = argparse.ArgumentParser(
                        prog='Detroit Crime Strip',
                        description='Pulls data from Detroit Open Portal into files by neighborhood',
                        epilog='v1.0.1')
    parser.add_argument('filename', nargs='?', default='default.json')
    args = parser.parse_args()
        
    sort_data = SetSort(args.filename)
    if sort_data == []:
        exit(1)
    
    sort_method = sort_data.get("method")
    sort_list = sort_data.get("pull_list")
    
    # Remove rows without location? Default is no
    if sort_data.get("keep_blank_loc") == "True":
        sort_keepblank = True
        
    #include starting and ending year if provided
    if 'start_year' in sort_data.keys():
        start_year = sort_data.get("start_year")
        start_year = int(start_year)
    else:
        start_year = None
    if 'end_year' in sort_data.keys():
        end_year = sort_data.get("end_year")
        end_year = int(end_year)
    else:
        end_year = None
    
    with open('RMS_Crime_Incidents.csv', newline='') as csvfile:
        print(f"Beginning read of RMS_Crime_Incidents.csv...")
        reader = csv.DictReader(csvfile)        
        
        for row in reader:
            if sort_method == 'offense_description': # remove trailing white space
                row['offense_description'] = row['offense_description'].rstrip()
            
            for h in sort_list:
                if sort_keepblank == False and not (row.get("X") or row.get("Y") or row.get("nearest_intersection")):
                    continue # skip the bad location info
                search_term = re.compile(h)
                if search_term.match(row[sort_method]):
                    crimes.append(row)
                    crimes_total += 1
    
    print(f"Total Crimes: {crimes_total}")
    csvfile.close()
    
    # sort by incident_occurred_at
    crimes = sorted(crimes, key=itemgetter('incident_occurred_at'))
    
    #Write our grand output
    print(f"Beginning file write...")
    with open('Detroit_Crime_Clients.csv','w',newline='') as outfile:
        writer = csv.DictWriter(outfile,fieldnames=reader.fieldnames)
        writer.writeheader()
        
        for c in crimes:
            writer.writerow(c)
            crimes_total -= 1
        if crimes_total != 0:
            print(f"Total Crimes: {crimes_total}")
            
    outfile.close()
    
    # If start and end year were provided, output files by year
    if start_year is None or end_year is None:
        print(f"Defaulting to 2020 through {start_time.year}.")
        start_year = 2020
        end_year = start_time.year
        
    for h in sort_list:
        # Build filename and strip out wildcards
        # pull characters out to esnure a valid file name
        fname = re.sub(r'[^a-zA-Z0-9]','',h)
        fname = fname + ' - ' + str(start_year) + ' to ' + str(end_year) + '.csv'
        fname = fname.replace('/','_')
        fname = fname.replace('*','')
        rows = 0
        
        with open(fname, 'w', newline='') as yearfile:
            print(f"Writing {fname}...")
            writer = csv.DictWriter(yearfile,fieldnames=reader.fieldnames)
            writer.writeheader()
            for c in crimes:
                year = int(c.get("incident_year"))
                if year >= start_year and year <= end_year:
                    search_term = re.compile(h)
                    if search_term.match(c[sort_method]):
                            writer.writerow(c)
                            rows += 1
                else:
                    continue
            print(f"Rows: {rows}")
        yearfile.close()

    print(f"Total Time: {(datetime.datetime.now() - start_time)}")

if __name__ == "__main__":
    main()
