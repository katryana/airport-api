from django.contrib import admin

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


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_filter = [
        "airplane_type",
    ]
    search_fields = [
        "name",
    ]
    list_display = [
        "name",
        "airplane_type",
        "capacity",
    ]


admin.site.register(AirplaneType)


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "closest_big_city",
    ]
    list_filter = [
        "closest_big_city",
    ]


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("__str__", "display_flights")

    def display_flights(self, obj):
        return ", ".join([flight.__str__() for flight in obj.flights.all()])

    display_flights.short_description = "Flights"


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    search_fields = [
        "route__source__closest_big_city",
        "route__destination__closest_big_city",
    ]
    list_filter = [
        "departure_time",
        "arrival_time",
    ]

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.exclude = ("crews", )
        else:
            self.exclude = None
        return super().get_form(request, obj, **kwargs)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)
    list_filter = [
        "created_at",
    ]
    search_fields = [
        "user",
    ]
    list_display = [
        "created_at",
        "user",
    ]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    search_fields = [
        "source__name",
        "destination__name",
    ]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_filter = [
        "order",
    ]
