"""
Corrects the pincode_ward_mapping table in samvaad.db
based on PMC 2025 Ward Formation data and Pune pincode directory.
"""
import sqlite3

DB = "backend/data/samvaad.db"

# pincode -> list of (ward_id, locality_or_None)
# ward_id is the DB id column (not ward_number)
CORRECT_MAPPING = {
    # 411001 = Pune Camp / Sadashiv Peth / Cantonment
    "411001": [(13, None), (24, "Kasba area")],
    # 411002 = Raviwar Peth / Budhwar Peth / Ganj Peth
    "411002": [(23, None), (24, None)],
    # 411003 = Khadki / Kirkee
    "411003": [(8, "Khadki")],
    # 411004 = Deccan Gymkhana / Erandwane
    "411004": [(28, None)],
    # 411005 = Shivajinagar / Model Colony / Ganeshkhind
    "411005": [(12, None)],
    # 411006 = Yerawada / Gandhinagar / Nagar Road
    "411006": [(6, None)],
    # 411007 = Aundh / Bopodi / Phugewadi
    "411007": [(8, None), (7, None)],
    # 411008 = Baner / Balewadi / Sus
    "411008": [(9, None), (10, None)],
    # 411009 = Navi Peth / Parvati / Padmavati / Sadashiv Peth
    "411009": [(27, None), (35, "Padmavati")],
    # 411011 = Kasba Peth / Somwar Peth / Narayan Peth
    "411011": [(24, None), (25, None)],
    # 411012 = Dapodi
    "411012": [(8, "Dapodi")],
    # 411013 = Hadapsar / Fatimanagar / Ramtekdi Industrial
    "411013": [(16, None), (17, None)],
    # 411014 = Viman Nagar / Lohegaon (civil)
    "411014": [(3, None), (5, None)],
    # 411015 = Dhanori / Kalas area
    "411015": [(1, None), (2, None)],
    # 411016 = Wakdewadi / Gokhale Nagar / Bhandarkar Road
    "411016": [(7, None), (12, None)],
    # 411019 = Nagpur Chawl / Dhanori (part)
    "411019": [(2, None)],
    # 411020 = Range Hills / Telco Colony / Kirkee
    "411020": [(8, "Range Hills")],
    # 411021 = Baner Gaon / Sus Road / Mahalunge
    "411021": [(9, None), (10, None)],
    # 411023 = Khadakwasla / NDA Road
    "411023": [(32, None)],
    # 411024 = NDA / Khadakwasla area
    "411024": [(32, None)],
    # 411025 = Wagholi / Kesnand / Uruli Devachi road
    "411025": [(4, None)],
    # 411027 = Aundh Camp / Jagtap Dairy
    "411027": [(8, "Aundh Camp")],
    # 411028 = Hadapsar / Phursungi / Magarpatta
    "411028": [(16, None)],
    # 411030 = Sadashiv Peth / Shaniwar Peth / Navi Peth
    "411030": [(25, None), (27, None)],
    # 411032 = Lohegaon / Airport area
    "411032": [(3, "Lohegaon")],
    # 411036 = Mundhwa / Ghorpadi / Koregaon Park
    "411036": [(14, None)],
    # 411037 = Bibvewadi / Salisbury Park
    "411037": [(20, None), (21, None)],
    # 411038 = Kothrud / Erandwane / Chandani Chowk
    "411038": [(10, None), (30, "Kothrud")],
    # 411040 = Wanawadi / Salunkhe Vihar / Ramtekdi
    "411040": [(18, None), (17, None)],
    # 411041 = Dhayari / Vadgaon Budruk / Nanded City
    "411041": [(33, None)],
    # 411042 = Ganj Peth / Guruwar Peth
    "411042": [(25, None), (26, None)],
    # 411043 = Dhankawadi / Katraj
    "411043": [(36, None)],
    # 411045 = Pashan / Baner Gaon
    "411045": [(9, "Baner Gaon")],
    # 411046 = Ambegaon Budruk / Lower Katraj
    "411046": [(37, None)],
    # 411047 = Lohegaon / Military area
    "411047": [(3, None)],
    # 411048 = Kondhwa Khurd / Kondhwa Budruk
    "411048": [(19, None), (39, None)],
    # 411051 = Karve Nagar / Hingne Home Colony
    "411051": [(29, None)],
    # 411052 = Karve Nagar / Erandwane (part)
    "411052": [(29, "Karvenagar")],
    # 411057 = Sus / near Hinjewadi boundary
    "411057": [(9, None)],
    # 411058 = Warje / Popular Nagar / Bhusari Colony
    "411058": [(31, "Warje / Bhusari Colony")],
    # 411060 = Mohammadwadi / Undri / Pisoli
    "411060": [(40, None)],
    # 411067 = Kalas area
    "411067": [(1, None)],
}

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("DELETE FROM pincode_ward_mapping")
print(f"Cleared existing mappings.")

inserted = 0
for pin_code, entries in CORRECT_MAPPING.items():
    for ward_id, locality in entries:
        cur.execute(
            "INSERT INTO pincode_ward_mapping (pin_code, ward_id, locality) VALUES (?, ?, ?)",
            (pin_code, ward_id, locality)
        )
        inserted += 1

conn.commit()
conn.close()
print(f"Inserted {inserted} rows across {len(CORRECT_MAPPING)} pincodes.")

# Verify
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT pwm.pin_code, pwm.ward_id, w.ward_number, w.ward_name, pwm.locality "
    "FROM pincode_ward_mapping pwm JOIN wards w ON w.id=pwm.ward_id "
    "ORDER BY pwm.pin_code"
).fetchall()
for r in rows:
    loc = f' [{r["locality"]}]' if r["locality"] else ""
    print(f'  {r["pin_code"]} → Ward {r["ward_number"]:2d}: {r["ward_name"]}{loc}')
conn.close()
