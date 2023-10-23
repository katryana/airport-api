from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airplane,
    AirplaneType,
    Airport,
    Crew,
    Flight,
    Order,
    Route,
    Ticket,
)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = (
            "id", "name", "airplane_type", "rows", "seats_in_row", "capacity"
        )
        read_only = ("id", "capacity")


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField(many=False, read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id", "name", "airplane_type", "capacity"
        )
        read_only = ("id", "capacity")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "distance", "source", "destination")


class RouteListSerializer(RouteSerializer):
    source = serializers.StringRelatedField(many=False, read_only=True)
    destination = serializers.StringRelatedField(many=False, read_only=True)


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super().validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    flight = serializers.StringRelatedField(many=False, read_only=True)
    order = serializers.StringRelatedField(many=False, read_only=True)


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "duration",
            "route",
            "airplane",
        )


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(many=False, read_only=True)
    airplane = serializers.StringRelatedField(many=False, read_only=True)
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )
    seats_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "duration",
            "route",
            "airplane",
            "airplane_capacity",
            "seats_available",
        )


class TicketDetailSerializer(TicketSerializer):
    flight = FlightListSerializer()
    order = serializers.StringRelatedField(many=False, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = AirplaneListSerializer(many=False, read_only=True)
    taken_seats = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )
    crews = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "duration",
            "route",
            "airplane",
            "taken_seats",
            "crews",
        )


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class CrewListSerializer(serializers.ModelSerializer):
    flights = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "flights")


class CrewDetailSerializer(CrewSerializer):
    flights = FlightSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "flights")
