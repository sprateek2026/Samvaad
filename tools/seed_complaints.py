"""
Seed 100 realistic random complaints across different users, wards,
categories, and statuses. Simulates 3 months of citizen activity.
"""
import sqlite3, random, datetime, sys

DB = "backend/data/samvaad.db"

# ---------------------------------------------------------------------------
# Realistic titles + descriptions per (category_id, sub_category_id)
# ---------------------------------------------------------------------------
TEMPLATES = {
    # Water Supply
    1:  [("Low water pressure in our area",
          "Water pressure has been very low for the past two weeks. We can barely fill buckets on the ground floor. Upper floors get no water at all."),
         ("No water supply since 3 days",
          "There has been no water supply to our building since Monday. We are dependent on tankers which are also not arriving regularly."),
         ("Polluted water coming from taps",
          "The water from municipal taps has turned brownish and smells foul. Several residents have complained of stomach issues after using this water."),
         ("Pipeline leakage on main road",
          "There is a major pipeline leakage near the main road junction. Water is flowing continuously onto the road causing wastage and traffic issues."),
         ("Water tanker not arriving on schedule",
          "The water tanker that is supposed to arrive daily has not come for 4 days. Multiple families are struggling without water.")],
    # Waste Management & Sanitation
    2:  [("Garbage not collected for a week",
          "Garbage has not been picked up from our lane for over 7 days. The pile is growing and causing foul smell. Residents are worried about health hazards."),
         ("Overflowing dustbin near market",
          "The municipal dustbin near the vegetable market is overflowing. Garbage is spilling onto the footpath and road. Urgent cleaning required."),
         ("Sewage overflow on road",
          "Sewage is overflowing from the manhole on the main road. The entire road is flooded with waste water. It is creating a major sanitation hazard."),
         ("Blocked drainage causing waterlogging",
          "The drainage near our society is completely blocked due to garbage dumped in it. Every rainfall causes waterlogging for 2-3 hours in the area."),
         ("Open garbage burning in residential area",
          "Residents are burning garbage in an open plot near our colony every evening. The smoke is causing breathing issues for elders and children.")],
    # Roads & Footpaths
    3:  [("Deep potholes on main road causing accidents",
          "There are multiple deep potholes on the stretch near the bus stop. Two-wheelers have already met with accidents. Urgent repair is needed before the monsoon worsens them."),
         ("Broken footpath blocks pedestrians",
          "The footpath tiles are broken and jagged near the school. Children walking to school are at risk of tripping and injuring themselves."),
         ("Road cave-in near junction",
          "A section of the road has caved in near the main junction, approximately 4 feet wide. It is a serious safety hazard for vehicles."),
         ("Waterlogging on road during rain",
          "The road near our locality gets flooded during every rainfall due to poor drainage. Vehicles get stuck and commuting becomes impossible."),
         ("Encroached footpath by shops",
          "Shopkeepers have placed their goods and boards on the footpath, forcing pedestrians to walk on the road. Action needed against encroachment.")],
    # Streetlights & Electricity
    4:  [("Streetlight not working for 2 weeks",
          "The streetlight outside our society gate has not been working for 15 days. The area is completely dark at night and has become unsafe, especially for women."),
         ("Hanging electric wires near school",
          "Low-hanging electric wires near the school entrance are very dangerous. Children could accidentally touch them. Immediate fixing required."),
         ("Frequent power cuts in our ward",
          "We have been experiencing power cuts of 4-6 hours daily for the past month. No advance notice is given. Our businesses and daily life is severely affected."),
         ("Open electrical box on footpath",
          "An electrical distribution box on the footpath has been left open with bare wires exposed. It is a serious electrocution risk to the public."),
         ("Dark zone causing safety concerns",
          "The entire stretch of road near the park has no functional streetlights. It is a dark zone and incidents of snatching have been reported.")],
    # Public Hygiene & Pest Control
    5:  [("Mosquito breeding in stagnant water",
          "Stagnant water has been collecting in an empty plot near our colony and is breeding mosquitoes. Dengue cases have been reported in the area."),
         ("Stray dogs menacing residents",
          "A pack of stray dogs near our society has become aggressive. They have bitten two residents in the past week. Urgent animal control action needed."),
         ("Public toilet extremely dirty",
          "The public toilet near the bus stop has not been cleaned for days. It is unusable and people are forced to use open areas. Health emergency."),
         ("Rodent infestation in market area",
          "Rats have infested the market area and surrounding streets. They are entering shops and homes. We request immediate pest control measures."),
         ("Fogging for mosquito control needed",
          "Dengue cases are rising in our ward. We request immediate fogging of the locality to control mosquito breeding and prevent further spread.")],
    # Parks, Gardens & Public Spaces
    6:  [("Park equipment broken and unsafe",
          "The swings and slides in the children's play area are broken and rusty. A child got injured last week. The equipment needs immediate replacement."),
         ("Garden not maintained for months",
          "The municipal garden in our ward has been neglected for months. Grass is overgrown, benches are broken, and lights are not working."),
         ("Fallen tree blocking park entrance",
          "A large tree has fallen across the park entrance due to last night's storm. It is blocking access and also poses a risk of further collapse."),
         ("Walking track in park damaged",
          "The tiles of the walking track inside the garden are broken and uneven. Senior citizens using it for morning walks are at risk of falling."),
         ("Dangerous tree branches overhanging road",
          "Several large branches of the old tree near the park are hanging dangerously low over the road. One fell during recent rains. Trimming needed urgently.")],
    # Public Health & Hospitals
    7:  [("Medicine stock out at health center",
          "The municipal health center does not have basic medicines like paracetamol and antibiotics. Patients are being turned away and told to buy from private pharmacies."),
         ("Health center closed during working hours",
          "The PMC health center in our area was found closed on two occasions during official working hours without any notice. Residents had to travel far for treatment."),
         ("Vaccination drive not conducted",
          "Our ward has not had a vaccination drive for children in the past 3 months. Several parents are waiting for the scheduled immunization. Please organize a camp."),
         ("Ambulance response very slow",
          "When called for an emergency last week, the ambulance took over 45 minutes to arrive. The delay could have been fatal. The system needs improvement.")],
    # Education & Municipal Schools
    8:  [("Broken toilets in municipal school",
          "The toilets in the municipal school are broken and unusable, especially for girls. Students are forced to hold until they reach home which is affecting attendance."),
         ("Drinking water not available in school",
          "There is no clean drinking water available in the municipal school. The tap is broken and the water purifier has been non-functional for months."),
         ("School building in poor condition",
          "The roof of two classrooms in the municipal school has been leaking during rains. Students cannot attend classes in monsoon. Urgent repair needed."),
         ("Teacher shortage affecting education",
          "Several teachers have been absent without replacement for weeks. Classes are being merged, affecting the quality of education for children.")],
    # Traffic & Transportation
    9:  [("Traffic signal not working at busy junction",
          "The traffic signal at the main junction has been non-functional for 5 days. During peak hours, traffic jams stretch for over 1 km. Accidents are likely."),
         ("Illegal parking blocking road",
          "Vehicles are being parked illegally along the main road causing it to narrow to a single lane. Emergency vehicles cannot pass through."),
         ("Bus stop damaged and unusable",
          "The shelter at our bus stop has been damaged and the roof has collapsed. Commuters are exposed to sun and rain while waiting for buses."),
         ("No bus connectivity to our area",
          "Our colony does not have any PMPML bus connectivity despite being a densely populated area. Residents travel long distances to reach the nearest bus stop."),
         ("Dangerous road junction needs signal",
          "The junction near our colony is uncontrolled and very dangerous. We request installation of a traffic signal or posting of traffic police during peak hours.")],
    # Safety & Law Enforcement
    10: [("Illegal construction without permission",
          "A builder is constructing an additional unauthorized floor in the night hours. The construction has no valid permission and is disturbing residents."),
         ("Noise pollution from commercial area",
          "Shops and restaurants in the commercial area play loud music till midnight every day, violating noise pollution norms. Residents cannot sleep."),
         ("Drug activity in public space",
          "Suspicious activity and drug use has been noticed near the park and dark areas of the ward at night. Request increased police patrolling."),
         ("Unauthorized hawkers blocking area",
          "Unauthorized hawkers have occupied the entire footpath and spill onto the road. They refuse to move and traffic is severely affected."),
         ("Lack of CCTV in our ward",
          "There are no CCTV cameras in our ward. Multiple theft incidents have occurred in the past month. We request installation of cameras for safety.")],
    # Environment & Pollution
    11: [("River / nala pollution by waste dumping",
          "Garbage and industrial waste is being dumped directly into the nala near our area. The water has turned black and the smell is unbearable. Water body is dying."),
         ("Illegal tree cutting in park",
          "Trees inside the municipal garden are being cut illegally at night. We noticed stumps of multiple trees this morning. Request immediate investigation."),
         ("Construction dust choking our colony",
          "A nearby construction site is generating enormous dust without any precautions. The entire colony is covered in dust and residents are suffering respiratory issues."),
         ("Open garbage burning polluting air",
          "A waste dump near our area is being burned openly every evening. The toxic smoke is causing breathing problems and is violating environmental norms.")],
    # Building & Construction Issues
    12: [("Unsafe building structure near school",
          "A partially demolished building near the school has been left in an unsafe state for months. The walls could collapse any time and children are at risk."),
         ("Illegal construction blocking drainage",
          "A new construction in our lane has blocked the natural drainage path. Our entire street now gets flooded during every rain."),
         ("Construction debris dumped on road",
          "Construction debris from a nearby building is being dumped on the public road. This is blocking traffic and is a safety hazard to motorists."),
         ("Unauthorized building modification",
          "A building owner has made unauthorized structural modifications that violate building regulations. The work is done without any permissions.")],
    # Welfare Schemes & Citizen Services
    13: [("Property tax demand notice incorrect",
          "I received a property tax demand notice with incorrect property area and ownership details. Despite visiting the office twice, the correction has not been made."),
         ("Ration card update not processed",
          "I applied for a ration card update 4 months ago but it has still not been processed. My family is missing out on the subsidized rations we are entitled to."),
         ("Birth certificate not issued despite application",
          "We applied for a birth certificate for our newborn 2 months ago. Despite multiple follow-ups, the certificate has not been issued from the ward office.")],
    # Disaster & Emergency Management
    15: [("Flooding in our ward",
          "Our entire ward is flooded due to heavy rainfall. Roads are submerged and residents are stuck in their homes. Drainage is completely insufficient."),
         ("Waterlogging due to blocked drains",
          "Severe waterlogging has occurred due to blocked stormwater drains. Several homes on ground floor have been flooded. Immediate pumping required."),
         ("Tree fall emergency on main road",
          "A large tree has fallen on the main road blocking both lanes completely. One car has been damaged. Emergency crew needed to clear the road.")],
    # Smart City & Infrastructure
    18: [("Public WiFi hotspot not working",
          "The PMC public WiFi hotspot near the municipal office has not been working for weeks. Citizens using it for government services are affected."),
         ("EV charging station request",
          "Our ward has no EV charging infrastructure. With increasing EV adoption, we request installation of at least one public EV charging station."),
         ("Smart pole CCTV camera not working",
          "The smart pole CCTV camera at the main junction is not operational for the past month. This is creating a security gap in the surveillance network.")],
}

STATUSES = ["submitted", "under_review", "assigned", "in_progress", "resolved", "closed"]
STATUS_WEIGHTS = [0.20, 0.20, 0.15, 0.20, 0.15, 0.10]
PRIORITIES = ["low", "medium", "high", "urgent"]
PRIORITY_WEIGHTS = [0.10, 0.45, 0.35, 0.10]

# Ward coordinates (approximate centers)
WARD_COORDS = {
    1:  (18.6020, 73.8800), 2:  (18.5960, 73.9000), 3:  (18.5820, 73.9150),
    4:  (18.5640, 73.9450), 5:  (18.5500, 73.9200), 6:  (18.5570, 73.8800),
    7:  (18.5340, 73.8360), 8:  (18.5600, 73.8100), 9:  (18.5310, 73.7970),
    10: (18.5050, 73.7910), 11: (18.5020, 73.8100), 12: (18.5320, 73.8530),
    13: (18.5180, 73.8640), 14: (18.5380, 73.9020), 15: (18.5100, 73.9300),
    16: (18.4990, 73.9220), 17: (18.4880, 73.9110), 18: (18.4920, 73.8920),
    19: (18.4800, 73.8800), 20: (18.4780, 73.8560), 21: (18.4920, 73.8720),
    22: (18.5120, 73.8790), 23: (18.5160, 73.8580), 24: (18.5210, 73.8590),
    25: (18.5170, 73.8580), 26: (18.5140, 73.8750), 27: (18.5070, 73.8520),
    28: (18.4950, 73.8200), 29: (18.5240, 73.8270), 30: (18.5060, 73.8360),
    31: (18.5100, 73.8100), 32: (18.4880, 73.8010), 33: (18.4620, 73.7930),
    34: (18.4580, 73.8060), 35: (18.4780, 73.8310), 36: (18.4750, 73.8520),
    37: (18.4650, 73.8590), 38: (18.4560, 73.8620), 39: (18.4680, 73.8820),
    40: (18.4580, 73.8990), 41: (18.4490, 73.9100),
}

def random_offset(lat, lng):
    return (
        lat + random.uniform(-0.005, 0.005),
        lng + random.uniform(-0.005, 0.005),
    )

def random_date(start_days_ago=90, end_days_ago=0):
    start = datetime.datetime.now() - datetime.timedelta(days=start_days_ago)
    end   = datetime.datetime.now() - datetime.timedelta(days=end_days_ago)
    delta = (end - start).total_seconds()
    return start + datetime.timedelta(seconds=random.random() * delta)

def next_complaint_id(conn):
    row = conn.execute("SELECT year, seq FROM complaint_id_seq WHERE id=1").fetchone()
    year, seq = row["year"], row["seq"] + 1
    conn.execute("UPDATE complaint_id_seq SET seq=?, year=? WHERE id=1", (seq, year))
    return f"PMC-{year}-{seq:05d}"


def main():
    random.seed(42)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    # Load reference data
    citizens = conn.execute(
        "SELECT id, ward_id FROM users WHERE role='citizen' AND id NOT IN (2,3) ORDER BY id"
    ).fetchall()
    wards = conn.execute("SELECT id, ward_number FROM wards ORDER BY ward_number").fetchall()
    cats  = conn.execute("SELECT id FROM complaint_categories ORDER BY id").fetchall()
    cat_ids = [c["id"] for c in cats]

    def get_subcats(cat_id):
        return [r["id"] for r in conn.execute(
            "SELECT id FROM complaint_sub_categories WHERE category_id=?", (cat_id,)
        ).fetchall()]

    # Corporator user ids (for status changes)
    corp_ids = [r["id"] for r in conn.execute("SELECT id FROM users WHERE role='corporator'").fetchall()] or [None]

    inserted = 0
    for _ in range(100):
        citizen = random.choice(citizens)
        ward    = random.choice(wards)
        cat_id  = random.choice(cat_ids)
        subcats = get_subcats(cat_id)
        sub_id  = random.choice(subcats) if subcats else None

        # Pick title/description from templates, or generate generic
        templates = TEMPLATES.get(cat_id, [])
        if templates:
            title, desc = random.choice(templates)
        else:
            title = f"Issue reported in Ward {ward['ward_number']}"
            desc  = "Citizens have reported a problem in this area that requires immediate attention from the concerned department."

        # Add ward/location flavour to title
        title = title  # keep as-is for realism

        status   = random.choices(STATUSES, STATUS_WEIGHTS)[0]
        priority = random.choices(PRIORITIES, PRIORITY_WEIGHTS)[0]

        coords = WARD_COORDS.get(ward["ward_number"], (18.5204, 73.8567))
        lat, lng = random_offset(*coords)

        created = random_date(90, 0)
        sla_days = {"low": 14, "medium": 7, "high": 3, "urgent": 1}[priority]
        sla_deadline = created + datetime.timedelta(days=sla_days)
        resolved_at  = None
        if status in ("resolved", "closed"):
            resolved_at = created + datetime.timedelta(days=random.randint(1, sla_days + 3))

        rating = None
        if status == "closed":
            rating = random.choices([1,2,3,4,5], [0.05,0.10,0.20,0.35,0.30])[0]

        cid = next_complaint_id(conn)

        conn.execute("""
            INSERT INTO complaints
              (complaint_id, citizen_id, category_id, sub_category_id, title, description,
               location_lat, location_lng, ward_id, status, priority,
               sla_deadline, resolved_at, citizen_rating, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            cid, citizen["id"], cat_id, sub_id, title, desc,
            lat, lng, ward["id"], status, priority,
            sla_deadline.strftime("%Y-%m-%d %H:%M:%S"),
            resolved_at.strftime("%Y-%m-%d %H:%M:%S") if resolved_at else None,
            rating,
            created.strftime("%Y-%m-%d %H:%M:%S"),
            created.strftime("%Y-%m-%d %H:%M:%S"),
        ))
        complaint_row_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # Add status history
        timeline = ["submitted"]
        if status != "submitted":
            progression = {
                "under_review": ["submitted", "under_review"],
                "assigned":     ["submitted", "under_review", "assigned"],
                "in_progress":  ["submitted", "under_review", "assigned", "in_progress"],
                "resolved":     ["submitted", "under_review", "assigned", "in_progress", "resolved"],
                "closed":       ["submitted", "under_review", "assigned", "in_progress", "resolved", "closed"],
            }
            timeline = progression.get(status, ["submitted"])

        t = created
        for i in range(1, len(timeline)):
            t = t + datetime.timedelta(hours=random.randint(4, 48))
            conn.execute("""
                INSERT INTO complaint_status_log
                  (complaint_id, from_status, to_status, changed_by, remarks, created_at)
                VALUES (?,?,?,?,?,?)
            """, (
                complaint_row_id,
                timeline[i-1], timeline[i],
                random.choice(corp_ids),
                f"Status updated to {timeline[i]}.",
                t.strftime("%Y-%m-%d %H:%M:%S"),
            ))

        inserted += 1
        if inserted % 10 == 0:
            print(f"  {inserted}/100 inserted...")

    conn.commit()
    conn.close()
    print(f"\nDone — inserted {inserted} complaints.")

    # Quick summary
    conn2 = sqlite3.connect(DB)
    conn2.row_factory = sqlite3.Row
    total = conn2.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    by_status = conn2.execute(
        "SELECT status, COUNT(*) as cnt FROM complaints GROUP BY status ORDER BY cnt DESC"
    ).fetchall()
    by_cat = conn2.execute("""
        SELECT cc.name, COUNT(*) as cnt FROM complaints c
        JOIN complaint_categories cc ON cc.id=c.category_id
        GROUP BY cc.id ORDER BY cnt DESC LIMIT 5
    """).fetchall()
    print(f"\nTotal complaints in DB: {total}")
    print("By status:", {r["status"]: r["cnt"] for r in by_status})
    print("Top 5 categories:", [(r["name"], r["cnt"]) for r in by_cat])
    conn2.close()


if __name__ == "__main__":
    main()
