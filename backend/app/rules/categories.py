CATEGORY_RULES = {
    "garbage": {
        "keywords": [
            "garbage", "waste", "kacra", "कचरा", "trash", "kacara",
            "bin not emptied", "door to door", "garbage collection",
            "kooda", "kooda", "घनकचरा", "garbage not picked"
        ],
        "routing": "corporator",
        "sla_hours": 24
    },
    "potholes": {
        "keywords": [
            "pothole", "potholes", "road damage", "khadda", "खड्डा",
            "broken road", "road repair", "road broken", "खड्डे",
            "rasta", "road condition", "cracks in road"
        ],
        "routing": "corporator",
        "sla_hours": 48
    },
    "streetlights": {
        "keywords": [
            "street light", "streetlight", "light not working",
            "दिवा", "lamp post", "no light", "light broken",
            "street lamp", "pole light", "अंधार", "dark road"
        ],
        "routing": "corporator",
        "sla_hours": 72
    },
    "drainage": {
        "keywords": [
            "drainage", "sewage", "drain block", "water logging",
            "नाला", "सीवरेज", "stagnant water", "drain clogged",
            "nalla", "gutter", "drain overflow", "पाणी साचले"
        ],
        "routing": "corporator",
        "sla_hours": 48
    },
    "water supply": {
        "keywords": [
            "water supply", "no water", "water pipe", "पाणी",
            "water leakage", "low water pressure", "pipe broken",
            "pani", "water tanker", "पाणीपुरवठा", "water cut"
        ],
        "routing": "corporator",
        "sla_hours": 24
    }
}

CATEGORY_LIST = list(CATEGORY_RULES.keys())
