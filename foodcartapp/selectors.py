from geopy.distance import geodesic

from places.models import Place


def get_coordinates(address, places):
    for place in places:
        if place.address == address:
            return place.lon, place.lat
    else:
        return Place.fetch_coordinates(address)


def get_available_restaurants(order, products_in_restaurants):
    ordered_products = order.ordered_products.all()

    restaurants = []
    for ordered_product in ordered_products:
        restaurants_with_products = [
            product_in_restaurant.restaurant
            for product_in_restaurant in products_in_restaurants
            if product_in_restaurant.product == ordered_product.product
        ]
        restaurants.append(set(restaurants_with_products))
    
    available_restaurants = set.intersection(*restaurants)

    return available_restaurants


def get_restaurants_with_distance(order, products_in_restaurants, places):
    available_restaurants = get_available_restaurants(order, products_in_restaurants)

    order_place = get_coordinates(
        address=order.address,
        places=places,
    )

    for restaurant in available_restaurants:
        restaurant_place = get_coordinates(
            address=restaurant.address,
            places=places,
        )
        restaurant_place_lon, restaurant_place_lat = restaurant_place
        
        if order_place is not None:
            order_place_lon, order_place_lat = order_place
            distance_between_restauraunt_and_order = round(
                geodesic(
                    (order_place_lon, order_place_lat),
                    (restaurant_place_lon, restaurant_place_lat),
                ).km,
            2)
        else:
            distance_between_restauraunt_and_order = None

        restaurant.order_distance = distance_between_restauraunt_and_order

    return sorted(
        available_restaurants, key=lambda restaurant: (
            restaurant.order_distance is None,
            restaurant.order_distance
        )
    )
