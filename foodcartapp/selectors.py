from geopy import distance

from places.models import Place


def get_place_coordinates(address, lat, lon):
    if lat is not None and lon is not None:
        return Place(address=address, lat=lat, lon=lon)

    coordinates = Place.fetch_coordinates(address)
    if coordinates is None:
        return None
        
    longitude, latitude = coordinates
    place, is_created = Place.objects.get_or_create(
        address=address,
        lon=longitude,
        lat=latitude,
    )

    return place


def get_restaurants_with_products_from_order(order, products_in_restaurants):
    order_products = order.ordered_products.all()

    restaurants_with_needed_products = []
    for order_product in order_products:
        for product_in_restaurants in products_in_restaurants:
            if product_in_restaurants.product == order_product.product:
                restaurants_with_needed_products.append(
                    [
                        product_in_restaurants.restaurant,
                        product_in_restaurants.restaurant_lat,
                        product_in_restaurants.restaurant_lon,
                    ]
                )
    
    return calculate_distances_to_order(
        order_address=order.address,
        order_lat=order.lat,
        order_lon=order.lon,
        restaurants=set(map(tuple, restaurants_with_needed_products)),
    )


def calculate_distances_to_order(order_address, order_lat, order_lon, restaurants):
    order_place = get_place_coordinates(
        address=order_address,
        lat=order_lat,
        lon=order_lon,
    )

    restaurants_with_order_distance = []
    for restaurant, restaurant_lat, restaurant_lon in restaurants:
        restaurant_place = get_place_coordinates(
            address=restaurant.address,
            lat=restaurant_lat,
            lon=restaurant_lon,
        )
        if order_place is None or restaurant_place is None:
            distance_between_restauraunt_and_order = 0
        else:
            distance_between_restauraunt_and_order = distance.distance(
                (order_place.lat, order_place.lon), (restaurant_place.lat, restaurant_place.lon),
            ).km

        restaurants_with_order_distance.append(
            {
                'restaurant': restaurant,
                'order_distance': round(distance_between_restauraunt_and_order, 2),
            }
        )

    return sorted(restaurants_with_order_distance, key=lambda restaurant: restaurant['order_distance'])
    