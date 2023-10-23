from django.urls import include, path
from rest_framework import routers

from airport.views import (
    AirplaneViewSet,
    AirplaneTypeViewSet,
    AirportViewSet,
    CrewViewSet,
    FlightViewSet,
    OrderViewSet,
    RouteViewSet,
)

router = routers.DefaultRouter()

router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airports", AirportViewSet)
router.register("crews", CrewViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)
router.register("routers", RouteViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "airport"
