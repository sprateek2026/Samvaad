#!/usr/bin/env python3
"""
Seed script: Imports ward GeoJSON data, representative mapping, and PIN codes.
Run once to initialize the database.
"""
import json
import sqlite3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend"))
from app.database import get_connection, init_db


def load_geojson(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data["features"]


def seed_wards(conn: sqlite3.Connection, geojson_path: str):
    features = load_geojson(geojson_path)
    print(f"Loading {len(features)} wards from GeoJSON...")

    for feat in features:
        props = feat["properties"]
        wardnum = props.get("wardnum") or props.get("prabhag_number") or props.get("ward_number")
        name1 = props.get("Name1") or props.get("name1") or props.get("prabhag_name") or ""
        name2 = props.get("Name2") or props.get("name2") or ""

        ward_name = name2 if name2 else name1
        geom = json.dumps(feat["geometry"])

        try:
            conn.execute(
                """INSERT INTO wards
                   (ward_number, ward_name, geometry)
                   VALUES (?, ?, ?)""",
                (int(wardnum), ward_name, geom)
            )
        except sqlite3.IntegrityError:
            pass  # already exists
    conn.commit()
    print("Wards imported successfully.")


def seed_representatives(conn: sqlite3.Connection):
    """Seed representative data based on MP_MLA_Corporator mapping.
    This maps ward numbers to their corporators, MLAs, and MPs.
    """
    mapping = {
        1: {"mla": "Bapusaheb Pathare", "mla_constituency": "Vadgaon Sheri", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Ashwini Rahul (Appa) Bhandare"},
        2: {"mla": "Bapusaheb Pathare", "mla_constituency": "Vadgaon Sheri", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Dhende Nandini Siddharth"},
        3: {"mla": "Bapusaheb Pathare", "mla_constituency": "Vadgaon Sheri", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Dr. Shreyas Pritam Khandve"},
        4: {"mla": "Bapusaheb Pathare", "mla_constituency": "Vadgaon Sheri", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Shri. Bansode Shailjeet Jaywant"},
        5: {"mla": "Bapusaheb Pathare", "mla_constituency": "Vadgaon Sheri", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Narayan Mohan Galande"},
        6: {"mla": "Bapusaheb Pathare", "mla_constituency": "Vadgaon Sheri", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Adv. Avinash Raj Salve"},
        7: {"mla": "Siddharth Shirole", "mla_constituency": "Shivajinagar", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Manvatkar Nisha Sachin"},
        8: {"mla": "Siddharth Shirole", "mla_constituency": "Shivajinagar", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Parshuram Balkrishna Wadekar"},
        9: {"mla": "Bapusaheb Pathare", "mla_constituency": "Vadgaon Sheri", "mla_party": "BJP",
            "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
            "corp_a": "Adv. Avinash Raj Salve"},
        10: {"mla": "Siddharth Shirole", "mla_constituency": "Shivajinagar", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Amruta Ram Mhetre (Zadpe)"},
        11: {"mla": "Siddharth Shirole", "mla_constituency": "Shivajinagar", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Harshwardhan Deepak Mankar"},
        12: {"mla": "Siddharth Shirole", "mla_constituency": "Shivajinagar", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Amruta Ram Mhetre (Zadpe)"},
        13: {"mla": "Sunil Kamble", "mla_constituency": "Pune Cantonment (SC)", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Nilesh Suresh Alhat"},
        14: {"mla": "Sunil Kamble", "mla_constituency": "Pune Cantonment (SC)", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Himali Navnath Kamble"},
        15: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Abnave Nanda Anil"},
        16: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Bankar Vaishali Sunil"},
        17: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Londhe Khandu Satish"},
        18: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Adv. Kedari Sahil Shivaji"},
        19: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Taslim Hasan Shaikh"},
        20: {"mla": "Hemant Rasne", "mla_constituency": "Kasba Peth", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Aaba (Rajendra) Y. Shilimkar"},
        21: {"mla": "Sunil Kamble", "mla_constituency": "Pune Cantonment (SC)", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Vairage Prasannajit Bharat"},
        22: {"mla": "Sunil Kamble", "mla_constituency": "Pune Cantonment (SC)", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Mrunal Pandurang (Bappu) Kamble"},
        23: {"mla": "Hemant Rasne", "mla_constituency": "Kasba Peth", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Javale Pallavi Chandrashekhar"},
        24: {"mla": "Hemant Rasne", "mla_constituency": "Kasba Peth", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Bahirat Kalpana Dilip"},
        25: {"mla": "Hemant Rasne", "mla_constituency": "Kasba Peth", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Sau. Swapnali Nitin Pandit"},
        26: {"mla": "Hemant Rasne", "mla_constituency": "Kasba Peth", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Ganesh Bugaji Kalyankar"},
        27: {"mla": "Madhuri Misal", "mla_constituency": "Parvati", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Mahesh (Amar) Vilas Awale"},
        28: {"mla": "Madhuri Misal", "mla_constituency": "Parvati", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Rithe Vrushali Anand"},
        29: {"mla": "Siddharth Shirole", "mla_constituency": "Shivajinagar", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Pande Sunil Namdev"},
        30: {"mla": "Madhuri Misal", "mla_constituency": "Parvati", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Dudhane Swapnil Devaram"},
        31: {"mla": "Chandrakant Patil", "mla_constituency": "Kothrud", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Mathwad Dinesh Mahadev"},
        32: {"mla": "Chandrakant Patil", "mla_constituency": "Kothrud", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Kiran Dagde Patil"},
        33: {"mla": "Chandrakant Patil", "mla_constituency": "Kothrud", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Bhosale Harshada Shantanu"},
        34: {"mla": "Chandrakant Patil", "mla_constituency": "Kothrud", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Barate Bharatbhushan Sharadchandra"},
        35: {"mla": "Chandrakant Patil", "mla_constituency": "Kothrud", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Gosavi Jyoti Kishor"},
        36: {"mla": "Madhuri Misal", "mla_constituency": "Parvati", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Veena Ganesh Ghosh"},
        37: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Dhanashree Dattatray Kolhe"},
        38: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Smita Sudhir Kondhare"},
        39: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Varsha Bhimrao Sathe"},
        40: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Archana Amit Jagtap"},
        41: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": "Alhat Prachi Ashish"},
        42: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        43: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        44: {"mla": "Sunil Kamble", "mla_constituency": "Pune Cantonment (SC)", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        45: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        46: {"mla": "Chetan Tupe", "mla_constituency": "Hadapsar", "mla_party": "NCP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        47: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        48: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        49: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        50: {"mla": "Madhuri Misal", "mla_constituency": "Parvati", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        51: {"mla": "Chandrakant Patil", "mla_constituency": "Kothrud", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        52: {"mla": "Chandrakant Patil", "mla_constituency": "Kothrud", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        53: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        54: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        55: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        56: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        57: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
        58: {"mla": "Bhimrao Tapkir", "mla_constituency": "Khadakwasala", "mla_party": "BJP",
             "mp": "Murlidhar Mohol", "mp_constituency": "Pune", "mp_party": "BJP",
             "corp_a": None},
    }

    count = 0
    for ward_num, data in mapping.items():
        conn.execute(
            """UPDATE wards SET
               corporator_a_name = ?,
               mla_name = ?, mla_constituency = ?, mla_party = ?,
               mp_name = ?, mp_constituency = ?, mp_party = ?
               WHERE ward_number = ?""",
            (data["corp_a"], data["mla"], data["mla_constituency"], data["mla_party"],
             data["mp"], data["mp_constituency"], data["mp_party"], ward_num)
        )
        conn.execute(
            """INSERT OR REPLACE INTO representative_mapping
               (ward_id, mla_name, mla_constituency, mla_party, mp_name, mp_constituency, mp_party)
               SELECT id, ?, ?, ?, ?, ?, ?
               FROM wards WHERE ward_number = ?""",
            (data["mla"], data["mla_constituency"], data["mla_party"],
             data["mp"], data["mp_constituency"], data["mp_party"], ward_num)
        )
        count += 1

    conn.commit()
    print(f"Seeded {count} ward representative mappings.")


def seed_categories(conn: sqlite3.Connection):
    categories = [
        ("Water Supply", "पाणीपुरवठा", "जल आपूर्ति", "corporator", 24),
        ("Waste Management & Sanitation", "कचरा व्यवस्थापन आणि स्वच्छता", "कचरा प्रबंधन और स्वच्छता", "corporator", 24),
        ("Roads & Footpaths", "रस्ते आणि पदपथ", "सड़कें और फुटपाथ", "corporator", 48),
        ("Streetlights & Electricity", "स्ट्रीट लाइट आणि वीज", "स्ट्रीट लाइट और बिजली", "corporator", 72),
        ("Public Hygiene & Pest Control", "सार्वजनिक स्वच्छता आणि कीड नियंत्रण", "सार्वजनिक स्वच्छता और कीट नियंत्रण", "corporator", 48),
        ("Parks, Gardens & Public Spaces", "उद्याने, बागा आणि सार्वजनिक जागा", "पार्क, बगीचे और सार्वजनिक स्थान", "corporator", 72),
        ("Public Health & Hospitals", "सार्वजनिक आरोग्य आणि रुग्णालये", "सार्वजनिक स्वास्थ्य और अस्पताल", "mla", 48),
        ("Education & Municipal Schools", "शिक्षण आणि नगरसेवक शाळा", "शिक्षा और नगर निगम स्कूल", "mla", 72),
        ("Traffic & Transportation", "वाहतूक आणि परिवहन", "यातायात और परिवहन", "corporator", 48),
        ("Safety & Law Enforcement", "सुरक्षा आणि कायदा अंमलबजावणी", "सुरक्षा और कानून प्रवर्तन", "corporator", 48),
        ("Environment & Pollution", "पर्यावरण आणि प्रदूषण", "पर्यावरण और प्रदूषण", "mla", 72),
        ("Building & Construction Issues", "इमारत आणि बांधकाम समस्या", "भवन और निर्माण संबंधी समस्याएं", "corporator", 72),
        ("Welfare Schemes & Citizen Services", "कल्याण योजना आणि नागरिक सेवा", "कल्याण योजनाएं और नागरिक सेवाएं", "mla", 72),
        ("Digital Governance & Online Services", "डिजिटल प्रशासन आणि ऑनलाइन सेवा", "डिजिटल शासन और ऑनलाइन सेवाएं", "corporator", 72),
        ("Disaster & Emergency Management", "आपत्ती आणि आपत्कालीन व्यवस्थापन", "आपदा और आपातकालीन प्रबंधन", "mla", 24),
        ("Community & Civic Participation", "समुदाय आणि नागरी सहभाग", "सामुदायिक और नागरिक भागीदारी", "corporator", 72),
        ("Corruption & Governance Complaints", "भ्रष्टाचार आणि प्रशासन तक्रारी", "भ्रष्टाचार और शासन संबंधी शिकायतें", "mla", 72),
        ("Smart City & Infrastructure Requests", "स्मार्ट सिटी आणि पायाभूत सुविधा", "स्मार्ट सिटी और बुनियादी ढांचा", "corporator", 72),
    ]

    for name, mr, hi, level, sla in categories:
        conn.execute(
            "INSERT OR IGNORE INTO complaint_categories (name, name_mr, name_hi, routing_level, sla_hours) VALUES (?, ?, ?, ?, ?)",
            (name, mr, hi, level, sla)
        )
    conn.commit()
    print("Seeded 18 complaint categories.")


def seed_sub_categories(conn: sqlite3.Connection):
    sub_data = {
        "Water Supply": [
            "Low water pressure", "No water supply", "Polluted / muddy water",
            "Pipeline leakage", "Broken water pipeline", "Illegal water connections",
            "Overflowing water tanks", "Water tanker request", "Delayed tanker supply",
            "Uneven water distribution", "Water shortage during summer",
            "Contaminated drinking water", "Meter issues", "High water bill complaints",
            "Public tap malfunction", "Borewell failure", "Water wastage from pipelines",
            "Rainwater harvesting issues",
        ],
        "Waste Management & Sanitation": [
            "Garbage pile-up", "Door-to-door collection not happening",
            "Overflowing dustbins", "Irregular garbage collection",
            "Wet/dry waste not segregated", "Biomedical waste disposal issues",
            "Construction debris dumping", "Open garbage burning",
            "Dead animal disposal", "Open sewage chamber", "Sewage overflow",
            "Blocked drainage", "Stormwater drain blockage", "Foul smell from drains",
            "Waterlogging due to drainage issues", "Septic tank overflow",
            "Public area littering",
        ],
        "Roads & Footpaths": [
            "Potholes", "Broken roads", "Damaged footpaths", "Encroached footpaths",
            "Missing footpaths", "Road cave-ins", "Poor road resurfacing",
            "Unfinished road work", "Dangerous speed breakers", "No zebra crossing",
            "Road markings faded", "Waterlogging on roads", "Illegal parking causing blockage",
            "Traffic bottlenecks", "Missing road signage", "Broken dividers",
            "Flyover maintenance issues", "Unsafe pedestrian crossings",
        ],
        "Streetlights & Electricity": [
            "Streetlight not working", "Flickering streetlights", "Missing streetlights",
            "Broken electric poles", "Hanging wires", "Transformer failure",
            "Frequent power cuts", "Illegal electricity connections", "Open electrical boxes",
            "Sparking wires", "High tension safety concerns",
            "Dark zones causing safety concerns", "Delayed streetlight repair",
        ],
        "Public Hygiene & Pest Control": [
            "Mosquito breeding", "Fogging request", "Dengue-prone areas",
            "Public toilet cleaning", "Dirty public toilets", "Lack of public toilets",
            "Rodent infestation", "Stray dog menace", "Stray cattle issue",
            "Dead animal removal", "Illegal slaughter waste", "Open urination hotspots",
            "Unsanitary market areas", "Pest control request",
            "Garbage causing health hazards",
        ],
        "Parks, Gardens & Public Spaces": [
            "Park maintenance", "Broken play equipment", "Unclean gardens",
            "Damaged benches", "Lack of security in parks",
            "Waterlogging in playgrounds", "Illegal encroachment in parks",
            "Broken walking tracks", "Tree trimming request", "Fallen trees",
            "Dangerous tree branches", "Lack of lighting in parks",
            "Sports ground maintenance", "Open gym equipment damaged",
        ],
        "Public Health & Hospitals": [
            "Poor hospital cleanliness", "Lack of medicines", "Long waiting times",
            "Staff shortage", "Ambulance delay", "Vaccination request",
            "Health camp request", "Non-functional health center",
            "Emergency response delay", "Medical waste disposal issue",
            "Unsafe drinking water complaints", "Disease outbreak reporting",
        ],
        "Education & Municipal Schools": [
            "Poor school infrastructure", "Broken toilets in schools",
            "Drinking water issues in schools", "Teacher shortage",
            "Unsafe school buildings", "Playground maintenance",
            "Midday meal quality issues", "Digital classroom request",
            "School transport issues", "Lack of sanitation",
        ],
        "Traffic & Transportation": [
            "Traffic congestion", "Signal not working", "Illegal parking",
            "Bus stop maintenance", "Need for additional buses",
            "Unsafe traffic junction", "Auto-rickshaw overcharging",
            "Traffic police absence", "Road accidents hotspot", "Speeding complaints",
            "Encroachment causing traffic", "Poor public transport connectivity",
        ],
        "Safety & Law Enforcement": [
            "Unsafe public areas", "Drug-related activities", "Illegal encroachment",
            "Noise pollution", "Illegal construction", "Public nuisance",
            "Harassment complaints", "CCTV installation request",
            "Lack of police patrolling", "Gambling activities",
            "Unauthorized hawkers", "Fire safety concerns",
        ],
        "Environment & Pollution": [
            "Air pollution", "Noise pollution", "River pollution",
            "Illegal tree cutting", "Construction dust", "Industrial pollution",
            "Plastic waste dumping", "Burning garbage", "Lake pollution",
            "Water body encroachment", "Green cover reduction",
            "Climate-related concerns",
        ],
        "Building & Construction Issues": [
            "Illegal construction", "Unsafe buildings", "Unauthorized modifications",
            "Construction noise", "Debris on roads", "Dangerous excavation",
            "Occupancy certificate issues", "Builder violations",
            "Encroachment complaints",
        ],
        "Welfare Schemes & Citizen Services": [
            "Pension application issues", "Ration card issues",
            "Birth certificate delays", "Death certificate issues",
            "Property tax complaints", "Water bill disputes",
            "Scheme eligibility queries", "Government subsidy requests",
            "RTI assistance", "Aadhaar update issues",
        ],
        "Digital Governance & Online Services": [
            "Website not working", "Online payment failure",
            "Complaint portal issues", "Mobile app issues", "OTP not received",
            "Service request tracking issue", "Digital certificate download issues",
            "Login problems",
        ],
        "Disaster & Emergency Management": [
            "Flooding", "Waterlogging", "Fire incidents",
            "Building collapse risk", "Landslide concerns",
            "Emergency shelter request", "Tree fall emergencies",
            "Storm damage", "Heatwave assistance", "Disaster relief requests",
        ],
        "Community & Civic Participation": [
            "Community hall maintenance", "Public event permissions",
            "Resident association coordination", "Ward meeting requests",
            "Civic volunteer programs", "Public awareness campaigns",
            "Citizen suggestion submissions",
        ],
        "Corruption & Governance Complaints": [
            "Bribery complaints", "Delay due to corruption", "Officer misconduct",
            "Misuse of public funds", "Tender irregularities",
            "Fake beneficiaries", "Political favoritism", "Lack of transparency",
        ],
        "Smart City & Infrastructure Requests": [
            "Public WiFi issues", "Smart pole maintenance",
            "EV charging station request", "CCTV not working",
            "Smart parking issues", "Public digital kiosk issues",
        ],
    }

    count = 0
    for cat_name, sub_list in sub_data.items():
        cat = conn.execute("SELECT id FROM complaint_categories WHERE name = ?", (cat_name,)).fetchone()
        if not cat:
            continue
        for sub in sub_list:
            conn.execute(
                "INSERT OR IGNORE INTO complaint_sub_categories (category_id, name) VALUES (?, ?)",
                (cat["id"], sub)
            )
            count += 1
    conn.commit()
    print(f"Seeded {count} sub-categories.")


def seed_pincode_wards(conn: sqlite3.Connection):
    pincode_data = {
        "411038": [31, 32, 33],
        "411004": [7, 8, 11],
        "411005": [25, 26],
        "411001": [17, 18, 19],
        "411002": [23, 24, 28],
        "411003": [27, 28, 29],
        "411006": [12, 13],
        "411007": [15, 16],
        "411008": [9, 10],
        "411011": [20, 21],
        "411012": [37, 38, 55],
        "411013": [49, 50],
        "411014": [36, 37],
        "411015": [39, 40],
        "411016": [1, 2, 8],
        "411017": [3, 4],
        "411018": [5, 6, 7],
        "411019": [41, 42, 43],
        "411020": [22, 44],
        "411021": [44, 45],
        "411022": [46, 47],
        "411023": [14, 33],
        "411024": [51, 52],
        "411025": [34, 35],
        "411026": [53, 54],
        "411027": [56, 57, 58],
        "411028": [48, 49],
        "411029": [41, 47],
        "411030": [30, 31],
        "411031": [36, 37],
        "411032": [38, 39],
        "411033": [55, 56],
        "411034": [34, 53],
        "411035": [51, 52],
        "411036": [40, 41],
        "411037": [32, 33],
        "411039": [42, 43],
        "411040": [44, 45],
        "411041": [14, 15],
        "411042": [46, 47],
        "411043": [56, 57],
        "411044": [48, 49],
        "411045": [52, 53],
        "411046": [27, 28],
        "411047": [24, 25],
        "411048": [54, 55],
        "411051": [50, 51],
        "411052": [57, 58],
        "411057": [10, 11],
        "411058": [32],
        "411060": [34, 35],
        "411061": [3, 4],
        "411062": [5, 6],
        "411067": [1, 2],
    }

    count = 0
    for pincode, ward_nums in pincode_data.items():
        for wn in ward_nums:
            ward = conn.execute("SELECT id FROM wards WHERE ward_number = ?", (wn,)).fetchone()
            if ward:
                conn.execute(
                    "INSERT OR IGNORE INTO pincode_ward_mapping (pin_code, ward_id) VALUES (?, ?)",
                    (pincode, ward["id"])
                )
                count += 1

    conn.commit()
    print(f"Seeded {count} PIN code to ward mappings.")


def seed_users(conn):
    users_data = [
        ("dev-user-9999999998", "System Admin", "9999999998", "411001", "admin", None),
        ("dev-user-9999999999", "E2E Test Citizen", "9999999999", "411038", "citizen", None),
        ("dev-user-001", "Test Citizen", "9876543210", "411038", "citizen", None),
    ]
    count = 0
    for uid, name, mobile, pin, role, ward_id in users_data:
        existing = conn.execute("SELECT id FROM users WHERE firebase_uid = ?", (uid,)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users (firebase_uid, full_name, mobile, pin_code, role, ward_id) VALUES (?, ?, ?, ?, ?, ?)",
                (uid, name, mobile, pin, role, ward_id)
            )
            count += 1
    conn.commit()
    print(f"Seeded {count} user(s).")


def main():
    geojson_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "data", "pune-2022-wards.geojson")

    if not os.path.exists(geojson_path):
        print(f"ERROR: GeoJSON file not found at {geojson_path}")
        print("Please download from: https://github.com/answerquest/pune-2022-wards")
        sys.exit(1)

    print("Initializing database...")
    init_db()

    conn = get_connection()
    try:
        seed_wards(conn, geojson_path)
        seed_representatives(conn)
        seed_categories(conn)
        seed_sub_categories(conn)
        seed_pincode_wards(conn)
        seed_users(conn)
        print("\n=== Database seeded successfully! ===")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
