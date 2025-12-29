"""
DeroitCrime.py will take RMS_Crime_Incidents.csv from the Detroit Open Data portal and pull out all of the crimes committed in the list of neighborhoods defined lower in the file. It will then write them to 
Detroit_Crime_Clients.csv

Version: 1.0
Date: 12/29/2025
Author: Alan Mullin
"""
import os, sys, csv, datetime, argparse
    

def main():
    start_time = datetime.datetime.now()
    crimes = []
    crimes_total = 0
    
    # Add or remove neighborhood names to this list as needed.
    hoods = ['Downtown','Midtown','Chalfonte','Grandmont','Cultural Center', 'Gateway Community', 'Islandview', 'New Center','Elmwood Park','Warrendale', 'Central Southwest','Delray', 'Greektown', 'Davison',
    'Carbon Works','Elijah McCoy','Corktown','North Corktown','Farwell','Forest Park','Brush Park','Airport Sub','Rivertown','Wayne State','Happy Homes','Dexter-Fenkell','Schoolcraft Southfield']
    
    with open('RMS_Crime_Incidents.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        print(f"Fieldnames: {reader.fieldnames}")
        print(f"Beginning read of RMS_Crime_Incidents.csv...")
        
        for row in reader:
            for h in hoods:
                if row['neighborhood'] == h:
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
    
    # Write only the last 5 years in another file
    print(f"Extracting last 5 years of each neighborhood...")
    for h in hoods:
        fname = h + ' - Last Five Years.csv'
        print(f"Saving {h} to {fname}...")
        with open(fname,'w',newline='') as lastfive:
            writer = csv.DictWriter(lastfive,fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for c in crimes:
                if c['neighborhood'] != h:
                    continue # go on to next row
                if int(c['incident_year']) < 2019:
                    continue
                    
                writer.writerow(c)
        lastfive.close()
        #on to next neighborhood in the list
        
    print(f"Total Time: {(datetime.datetime.now() - start_time)}")
    
main()
