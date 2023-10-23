from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Flight(models.Model):
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    route = models.ForeignKey(
        "Route", on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        "Airplane", on_delete=models.CASCADE, related_name="flights"
    )
    crews = models.ManyToManyField("Crew", related_name="flights", blank=True)

    @property
    def duration(self) -> str:
        duration = self.arrival_time - self.departure_time
        hours, remainder = divmod(duration.total_seconds(), 3600)
        minutes = remainder // 60
        return f"{int(hours):02d}:{int(minutes):02d}"

    def __str__(self):
        return (
            f"{self.airplane.name} ({self.route.source.closest_big_city} "
            f"- {self.route.destination.closest_big_city})"
        )

    class Meta:
        ordering = [
            "departure_time",
        ]


class Route(models.Model):
    distance = models.IntegerField()
    source = models.ForeignKey(
        "Airport", on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        "Airport", on_delete=models.CASCADE, related_name="destination_routes"
    )

    def __str__(self):
        return self.source.name + " - " + self.destination.name

    def clean(self):
        if self.source == self.destination:
            raise ValidationError(
                "Source and destination airports cannot be the same."
            )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    class Meta:
        ordering = [
            "source",
            "destination",
        ]


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=63)

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            "name",
        ]
        unique_together = (
            "name",
            "closest_big_city",
        )


class Airplane(models.Model):
    name = models.CharField(max_length=255, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        "AirplaneType", on_delete=models.CASCADE, related_name="airplanes"
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name

    class Meta:
        ordering = [
            "name",
        ]


class AirplaneType(models.Model):
    name = models.CharField(max_length=127, unique=True)

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        "Flight", on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(airplane, airplane_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {airplane_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        return super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return (
            f"{self.flight.departure_time.strftime('%d/%m/%Y %H:%M')} "
            f"(row: {self.row}, seat: {self.seat})"
        )

    class Meta:
        ordering = ["row", "seat"]
        unique_together = ("flight", "row", "seat")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return self.created_at.strftime("%d/%m/%Y %H:%M")

    class Meta:
        ordering = ["-created_at"]
