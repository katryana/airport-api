from django.db.models import F, Count
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Order,
    Route,
)

from airport.serializers import (
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneTypeSerializer,
    AirportSerializer,
    CrewSerializer,
    CrewListSerializer,
    CrewDetailSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
)
from user.permissions import (
    IsAdminOrIfAuthenticatedReadOnly, IsAdminUserOrReadOnly
)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        return self.serializer_class


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAdminUserOrReadOnly, )


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly, )

    def get_serializer_class(self):

        if self.action == "get":
            return CrewListSerializer

        if self.action == "retrieve":
            return CrewDetailSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        if self.action in ("get", "retrieve"):
            queryset = queryset.prefetch_related("flights")

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route", "airplane"
    )
    serializer_class = FlightSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAdminUserOrReadOnly, )

    def get_serializer_class(self):

        if self.action == "list":
            return FlightListSerializer

        if self.action == "retrieve":
            return FlightDetailSerializer

        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = queryset.annotate(
                seats_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
                )
            )

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("crews")

        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets__flight__airplane", "tickets__flight__route"
    )
    serializer_class = OrderSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):

        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related(
        "source", "destination"
    )
    serializer_class = RouteSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAdminUserOrReadOnly, )

    def get_serializer_class(self):

        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return self.serializer_class
