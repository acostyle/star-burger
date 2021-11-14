from geopy import distance

from places.models import Place
from .models import RestaurantMenuItem


def get_place_coordinates(address):
    coordinates = Place.fetch_coordinates(address)
    if coordinates is None:
        return None
        
    lon, lat = coordinates
    place, is_created = Place.objects.get_or_create(
        address=address,
        lon=lon,
        lat=lat,
    )

    return place


def get_restaurants_with_products_from_order(order):
    products_in_restaurants = RestaurantMenuItem.objects.get_products_in_restaurants().annotate_with_coordinates()
    order_products = order.ordered_products.all()

    restaurants_with_needed_products = []
    for order_product in order_products:
        restaurants_with_needed_products.append(
            [
                product_in_restaurants.restaurant
                for product_in_restaurants in products_in_restaurants
                if product_in_restaurants.product == order_product.product
            ]
        )
                
    
    return calculate_distances_to_order(
        order_address=order.address,
        restaurants=restaurants_with_needed_products,
    )


def calculate_distances_to_order(order_address, restaurants):
    order_place = get_place_coordinates(
        address=order_address
    )

    restaurants_with_order_distance = []
    for restaurant in restaurants:
        restaurant_place = get_place_coordinates(
            address=restaurant.address
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
    