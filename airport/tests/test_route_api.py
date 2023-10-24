from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from airport.models import Route, Airport
from airport.serializers import RouteListSerializer, RouteDetailSerializer

ROUTE_URL = reverse("airport:route-list")


def sample_route(**params):
    source = params.get("source", )
    destination = params.get("destination", )
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 90,
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


def sample_airport(**params):
    defaults = {
        "name": "Sample airport",
        "closest_big_city": "Sample city",
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


def detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


class UnauthenticatedRouteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "test12345",
        )
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        airport1 = sample_airport(name="Washington Airport")
        airport2 = sample_airport(name="Chicago Airport")
        sample_route(source=airport1, destination=airport2)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_routes_by_airports(self):
        airport1 = sample_airport(name="Washington Airport")
        airport2 = sample_airport(name="Chicago Airport")
        route1 = sample_route(source=airport1, destination=airport2)
        route2 = sample_route(source=airport2, destination=airport1)

        serializer1 = RouteListSerializer(route1)
        serializer2 = RouteListSerializer(route2)

        res = self.client.get(
            ROUTE_URL,
            {"source": airport1.name}
        )

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

        res = self.client.get(
            ROUTE_URL,
            {"destination": airport2.name}
        )

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_route_detail(self):
        airport1 = sample_airport(name="Washington Airport")
        airport2 = sample_airport(name="Chicago Airport")
        route = sample_route(source=airport1, destination=airport2)

        serializer = RouteDetailSerializer(route)

        url = detail_url(route.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        airport1 = sample_airport(name="Washington Airport")
        airport2 = sample_airport(name="Chicago Airport")
        payload = {
            "source": airport1,
            "destination": airport2,
            "distance": 180,
        }

        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "admin12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_route(self):
        airport1 = sample_airport(name="Washington Airport")
        airport2 = sample_airport(name="Chicago Airport")
        payload = {
            "source": airport1.id,
            "destination": airport2.id,
            "distance": 180,
        }

        res = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=res.data["id"])

        source = route.source
        del payload["source"]

        destination = route.destination
        del payload["destination"]

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(route, key))

        self.assertEqual(airport1, source)
        self.assertEqual(airport2, destination)

    def test_put_route_not_allowed(self):
        airport1 = sample_airport(name="Washington Airport")
        airport2 = sample_airport(name="Chicago Airport")
        route = sample_route(source=airport1, destination=airport2)

        url = detail_url(route.id)
        res = self.client.put(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_route_not_allowed(self):
        airport1 = sample_airport(name="Washington Airport")
        airport2 = sample_airport(name="Chicago Airport")
        route = sample_route(source=airport1, destination=airport2)

        url = detail_url(route.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
