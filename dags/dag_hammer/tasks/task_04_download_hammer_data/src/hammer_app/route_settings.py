from hammer_app.hammer_settings import HammerAppSettings


class RouteSettings(HammerAppSettings):
    def __init__(
        self,
        fastest_or_balanced="fastest",
        avoid_ferry=True,
        avoid_toll_road=False,
        avoid_tunnel=False,
        avoid_highway=False,
        avoid_shuttle_train=False,
        avoid_unpaved_roads=True,
        avoid_difficult_turns=True,
    ):
        self.routing = self.get_route_settings(fastest_or_balanced)
        self.avoid = self.get_avoid_settings(
            avoid_ferry,
            avoid_toll_road,
            avoid_tunnel,
            avoid_highway,
            avoid_shuttle_train,
            avoid_unpaved_roads,
            avoid_difficult_turns,
        )

    def get_route_settings(self, fastest_or_balanced):
        if fastest_or_balanced not in ("fastest", "balanced"):
            raise ValueError(
                f"`fastest_or_balanced` must be one of ('fastest', 'balanced')"
            )

        fastest = fastest_or_balanced == "fastest"
        balanced = not fastest

        route_settings = {
            "fastest": {"value": fastest, "label": "Fastest+route"},
            "balanced": {"value": balanced, "label": "Balanced+route"},
        }

        return route_settings

    def get_avoid_settings(
        self,
        avoid_ferry,
        avoid_toll_road,
        avoid_tunnel,
        avoid_highway,
        avoid_shuttle_train,
        avoid_unpaved_roads,
        avoid_difficult_turns,
    ):
        avoid_settings = {
            "ferry": {"value": avoid_ferry, "label": "Avoid+ferries"},
            "tollRoad": {"value": avoid_toll_road, "label": "Avoid+tolls"},
            "tunnel": {"value": avoid_tunnel, "label": "Avoid+tunnels"},
            "controlledAccessHighway": {
                "value": avoid_highway,
                "label": "Avoid+highways",
            },
            "carShuttleTrain": {
                "value": avoid_shuttle_train,
                "label": "Avoid+shuttle+trains",
            },
            "dirtRoad": {"value": avoid_unpaved_roads, "label": "Avoid+unpaved+roads"},
            "difficultTurns": {
                "value": avoid_difficult_turns,
                "label": "Avoid+difficult+turns",
            },
        }

        return avoid_settings
