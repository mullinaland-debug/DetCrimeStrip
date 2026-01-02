DetCrime.py will take RMS_Crime_Incidents.csv from the Detroit Open Data portal and pull out all of the crimes committed in the list defined in a JSON file. It will then write them to 
Detroit_Crime_Clients.csv and a separate CSV for each item in the search list. It takes a JSON file to determine what column to pull by, which rows to pull and what years if provided. If no years are provided, it defaults to
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
Date: 1/2/2026
Python Version: 3.14.2
Author: Alan Mullin
