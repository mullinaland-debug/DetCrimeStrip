"""
DeroitCrime.py will take RMS_Crime_Incidents.csv from the Detroit Open Data portal and pull out all of the crimes committed in the list of neighborhoods defined lower in the file. It will then write them to 
Detroit_Crime_Clients.csv and a separate CSV for each neighborhood. It takes a JSON file to determine what column to pull by, which rows to pull and what years if provided. If no years are provided, it defaults to
2020 through the current year.

Version: 1.1
Date: 12/30/2025
Python Version: 3.14.2
Author: Alan Mullin
"""
import os, sys, csv, datetime, argparse, json    

#
# GetNeighborhoodNames() looks in the RMS_Crime_Incidents.csv file and pulls out all the unique neighborhood names.
# Known issue: for some reason, it inserts a string "nan" in between 'Downtown' and 'Outer Drive-Hayes'. It does not\
# appear to be in the original data, and when you print the list, it is not treated as a string. EG: [...,'Downtown',nan,'Outer Drive-Hayes',...]
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
            case "police_precinct":
                print(f"Pulling precincts from {fname}...")
            case _:
                print(f"Invalid or unknown method provided.")
                return []
        
        return data

def main():
    start_time = datetime.datetime.now()
    crimes = []
    crimes_total = 0
    
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
            for h in sort_list:
                if row[sort_method] == h:
                    crimes.append(row)
                    crimes_total += 1
    
    print(f"Total Crimes: {crimes_total}")
    csvfile.close()
    
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
        fname = h + ' - ' + str(start_year) + ' to ' + str(end_year) + '.csv'
        fname = fname.replace('/','-')
        rows = 0
        with open(fname, 'w', newline='') as yearfile:
            print(f"Writing {fname}...")
            writer = csv.DictWriter(yearfile,fieldnames=reader.fieldnames)
            writer.writeheader()
            for c in crimes:
                year = int(c.get("incident_year"))
                if year >= start_year and year <= end_year:
                    if c[sort_method] == h:
                        writer.writerow(c)
                        rows += 1
                else:
                    continue
            print(f"Rows: {rows}")
        yearfile.close()

    print(f"Total Time: {(datetime.datetime.now() - start_time)}")

main()
