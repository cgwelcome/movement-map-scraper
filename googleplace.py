from googleplaces import GooglePlaces
import sys

google_places = GooglePlaces(sys.argv[1])

church_name = 'Animal Adoptions Of Flamborough'
location = 'WaterDown'

query_result = google_places.nearby_search(location=location, keyword=church_name)

for place in query_result.places:
    place.get_details()
    print(place.formatted_address)
    print(place.website)
