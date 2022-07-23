import pandas as pd
import os

import googlemaps
from datetime import datetime
import geopy.distance

animalDF = pd.read_excel(os.path.join("data", "Animal Data.xlsx"))


gmaps = googlemaps.Client(key='API_KEY')

# # Geocoding an address
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
#
# geocode_result[0]["geometry"]["location"]


#############
##cleaning###
def getLngLat(address):
    try:
        geocode_result = gmaps.geocode(address)

        latLngDict = geocode_result[0]["geometry"]["location"]

        return latLngDict["lng"], latLngDict["lat"]
    except Exception as e:
        print("address extract error|","Address：",address,"|", e)

        return None, None

getLngLat('1600 Amphitheatre Parkway, Mountain View, CA')

##1.1 crorect coordinates##
for row in range(animalDF.shape[0]):
    foundAddress = animalDF.loc[row, "found_address"]

    found_lng, found_lat = getLngLat(foundAddress)

    if found_lng != None and found_lat != None:
        animalDF.loc[row, "found_lng"] = found_lng
        animalDF.loc[row, "found_lat"] = found_lat

    outcomeAddress = animalDF.loc[row, "outcome_address"]

    outcome_lng, outcome_lat = getLngLat(outcomeAddress)

    if outcome_lng != None and outcome_lat != None:
        animalDF.loc[row, "outcome_lng"] = outcome_lng
        animalDF.loc[row, "outcome_lat"] = outcome_lat


##1.2 get distance##
distanceList = []
for row in range(animalDF.shape[0]):
    coords_1 = (animalDF.loc[row, "found_lng"], animalDF.loc[row, "found_lat"])
    coords_2 = (animalDF.loc[row, "outcome_lng"], animalDF.loc[row, "outcome_lat"])

    distanceList.append(geopy.distance.geodesic(coords_1, coords_2).miles)

animalDF["distance"] = distanceList

##1.3 cleaning data##

##deal with errors or format problem: drop na rows##
animalDF = animalDF.dropna()

##deal with outliers##
import numpy as np
animalDF.select_dtypes(include=np.number).max()

numericCols = ['found_lng', 'found_lat', 'outcome_lng', 'outcome_lat',
       'distance_miles', 'age_at_intake', 'distance']


maxColsDict= {
 'age_at_intake':500,
 'distance':10000
}
###if col's value greater than setted max value, then replace by mean value###
for col in maxColsDict.keys():
    max_val = maxColsDict[col]
    index = animalDF[col] > max_val
    animalDF.loc[index, col] = round(animalDF.loc[~index, col].mean())


##export data##
animalDF.to_excel(os.path.join("data", "Animal Data clean.xlsx"), index=False)
