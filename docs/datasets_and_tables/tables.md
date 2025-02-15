# Tables (WIP)

## GTFS Tables
Reference: [gtfs.org](http://gtfs.org/reference/static)

| Tablename | Description |
| ------- | ----------- |
| agency | Transit agencies with service represented in this dataset. |
| calendar | Service dates specified using a weekly schedule with start and end dates. This file is required unless all dates of service are defined in `calendar_dates`. |
| calendar_dates | Exceptions for the services defined in the `calendar`. If `calendar` is omitted, then `calendar_dates` is required and must contain all dates of service. |
| calipt_files | tables available for each transit agency. | **double check**
| calipt_load_errors | **empty** |
| calitp_status | Cal-ITP ID and GTFS URLs for each transit agency. | **double check**
| fare_attributes | Fare information for a transit agency's routes. |
| fare_rules | Rules to apply fares for itineraries. |
| feed_info | Dataset metadata, including publisher, version, and expiration information. |
| frequencies | Headway (time between trips) for headway-based service or a compressed representation of fixed-schedule service. |
| routes | Transit routes. A route is a group of trips that are displayed to riders as a single service. |
| shapes | Rules for mapping vehicle travel paths, sometimes referred to as route alignments. |
| stop_times | Times that a vehicle arrives at and departs from stops for each trip. |
| stops | Stops where vehicles pick up or drop off riders. Also defines stations and station entrances. |
| transfers | Rules for making connections at transfer points between routes. |
