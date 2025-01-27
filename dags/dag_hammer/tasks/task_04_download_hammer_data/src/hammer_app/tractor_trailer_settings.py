from hammer_app.hammer_settings import HammerAppSettings


class TractorTrailerSettings(HammerAppSettings):
    id = 1
    type = "tractorTrailer"
    label = "Tractor Trailer"
    truck_type = "tractorTrailer"
    trailers = 1
    height = {"ft": 13, "in": 6}
    length = {"ft": 70, "in": 0}
    width = {"ft": 8, "in": 6}
    gross_weight = {"lb": 60000}
    weight_per_axle = {"lb": 14000}
    shipped_hazardous_goods = {
        "explosive": False,
        "gas": True,
        "flammable": False,
        "combustible": False,
        "organic": False,
        "poison": False,
        "radioactive": False,
        "corrosive": False,
        "poisonous_inhalation": False,
        "harmful_to_water": False,
        "other": False,
    }
