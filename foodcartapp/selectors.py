from geopy import distance

from places.models import Place
from .models import RestaurantMenuItem


def get_place_coordinates(address, lat, lon):
    if lat is not None and lon is not None:
        return Place(lat=lat, lon=lon)

    coordinates = Place.fetch_coordinates(address)
    if coordinates is None:
        return None

    place, is_created = Place.objects.get_or_create(
        address=address,
        lat=coordinates.lat,
        lon=coordinates.lon,
    )

    return Place(lat=place.lat, lon=place.lon)


def get_restaurants_with_products_from_order(order):
    products_in_restaurants = RestaurantMenuItem.objects.get_products_in_restaurants().annotate_with_coordinates()
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
        restaurants=restaurants_with_needed_products,
        order_address=order.address,
        lat=order.lat,
        lon=order.lon,
    )


def calculate_distances_to_order(order_address, restaurants, lat, lon):
    order_place = get_place_coordinates(
        order_address,
        lat=lat,
        lon=lon,
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
    