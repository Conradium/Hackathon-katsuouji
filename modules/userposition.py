import geocoder
import folium  # Optional: For visualizing the location on a map

def get_user_geo_position():
    """
    Gets the user's geolocation data (latitude, longitude, address).

    Returns:
        A dictionary containing latitude, longitude, and address if successful,
        or None if an error occurs.
    """
    try:
        g = geocoder.ip('me')  # Use the user's IP address

        if g.ok:  # Check if the geocoding was successful
            latitude = g.lat
            longitude = g.lng
            address = g.address

            return {
                'latitude': latitude,
                'longitude': longitude,
                'address': address
            }
        else:
            print(f"Error: Geocoding failed. Status: {g.status}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def display_location_on_map(latitude, longitude, address=None):
    """
    Displays the location on an interactive map using Folium.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
        address: (Optional) The address to display in the popup.
    """

    try:
        # Create a map centered at the location
        my_map = folium.Map(location=[latitude, longitude], zoom_start=13)

        # Add a marker at the location
        popup_text = f"Latitude: {latitude}<br>Longitude: {longitude}"
        if address:
            popup_text += f"<br>Address: {address}"
        folium.Marker([latitude, longitude], popup=popup_text).add_to(my_map)


        # Save the map to an HTML file (you can open this in your browser)
        map_filename = "user_location_map.html"
        my_map.save(map_filename)
        print(f"Map saved to {map_filename}. Open this file in a web browser to view the map.")


    except Exception as e:
        print(f"Error displaying map: {e}")



def main():
    """Main function to get the user's geolocation and optionally display it."""

    geo_data = get_user_geo_position()

    if geo_data:
        print(f"Latitude: {geo_data['latitude']}")
        print(f"Longitude: {geo_data['longitude']}")
        print(f"Address: {geo_data['address']}")

        # Optional: Display the location on a map
        display_map = input("Do you want to display the location on a map? (y/n): ").lower()
        if display_map == 'y':
            display_location_on_map(geo_data['latitude'], geo_data['longitude'], geo_data['address'])

    else:
        print("Failed to retrieve geolocation data.")


if __name__ == "__main__":
    main()