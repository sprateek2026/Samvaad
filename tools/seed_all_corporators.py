"""
Full reseed script:
1. Delete all representatives
2. Insert 164 corporators with corrected names + avatar URLs
3. Insert 41 MLA rows + 41 MP rows with avatar URLs
4. Update wards table with all fallback data

Source: MP_MLA_Corporator.md (user-provided, Jan 2026 PMC election results)
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.config import DATABASE_PATH

DB = os.path.join(os.path.dirname(__file__), "..", "backend", DATABASE_PATH)
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

AVATAR_BASE = "https://ui-avatars.com/api/?name={}&background=6366f1&color=fff&size=128"

def avatar(name):
    return AVATAR_BASE.format(name.replace(" ", "+"))

# ── Corporator data: (ward_number, A_name, A_party, B_name, B_party, C_name, C_party, D_name, D_party) ──
corporators = [
    (1,  "Ashwini Rahul (Appa) Bhandare", "BJP",  "Dangat Sangita Sandeep", "BJP",  "Rekha Chandrakant Tingre", "NCP",  "Anil (Bobby) Vasantrao Tingre", "BJP"),
    (2,  "Dhende Nandini Siddharth", "NCP",  "Ravi (Harshal) Ramesh Tingre", "NCP",  "Shital Ajay Sawant", "NCP",  "Suhas Vijay Tingre", "NCP"),
    (3,  "Dr. Shreyas Pritam Khandve", "BJP",  "Anil Dilip Satav", "BJP",  "Aishwarya Surendra Pathare", "BJP",  "Dabhade Ramdas Dattatray", "BJP"),
    (4,  "Shri. Bansode Shailjeet Jaywant", "BJP",  "Ratnamala Sandeep Satav", "BJP",  "Bharane Trupti Santosh", "BJP",  "Surendra Bapusaheb Pathare", "BJP"),
    (5,  "Narayan Mohan Galande", "BJP",  "Galande Shweta Mukund", "BJP",  "Galande Kavita Mahendra", "BJP",  "Mulik Yogesh Tukaram", "BJP"),
    (6,  "Adv. Avinash Raj Salve", "Congress",  "Saira Hanif Sheikh", "Congress",  "Ashwini Daniel Landge", "Congress",  "Vishal Hari Malke", "Congress"),
    (7,  "Nisha Manwatkar", "BJP",  "Anjali Vinodanna Orse", "NCP",  "Adv. Nikam Nilesh Narayan", "NCP",  "Datta Bahirat", "NCP"),
    (8,  "Parshuram Balkrishna Wadekar", "BJP",  "Bhakti Ajit Gaikwad", "BJP",  "Chhajed Sapna Anand", "BJP",  "Chandrashekhar (Sunny) Vinayak Nimhan", "BJP"),
    (9,  "Chimte Rohini Sudhir", "BJP",  "Chandere Baburao Dattoba", "NCP",  "Kokate Mayuri Rahul", "BJP",  "Amol Ratan Balwadkar", "NCP"),
    (10, "Kiran Dagde Patil", "BJP",  "Pawar Rupali Sachin", "BJP",  "Varape Alpana Ganesh", "BJP",  "Vedepatil Dilip Tukaram", "BJP"),
    (11, "Harshwardhan Deepak Mankar", "NCP",  "Dokh Deepali Santosh", "Congress",  "Butala Manisha Sandeep", "BJP",  "Adv. Ramchandra (Chandusheth) Atmaram Kadam", "Congress"),
    (12, "Amruta Ram Mhetre (Zadpe)", "BJP",  "Shri. Apoorva Dattatray Khade", "BJP",  "Sau. Pooja Pratul Jagade", "BJP",  "Ekabote Nivedita Gajanan", "BJP"),
    (13, "Nilesh Suresh Alhat", "BJP",  "Sumayya Maheboob Nadaf", "Congress",  "Vaishali Nagnath Bhalerao", "Congress",  "Arvind Shinde", "Congress"),
    (14, "Himali Navnath Kamble", "BJP",  "Dhayarkar Kishor Vishnu", "BJP",  "Kawade Surekha Chandrakant", "NCP",  "Gaikwad Umesh Dnyaneshwar", "BJP"),
    (15, "Abnave Nanda Anil", "BJP",  "Dr. Dada Kodre", "BJP",  "Ghule Sarika Amit", "BJP",  "Ajit Dattatraya Ghule", "BJP"),
    (16, "Bankar Vaishali Sunil", "NCP",  "Ujwala Jangale", "BJP",  "Nitin Gavvade", "Shiv Sena-UBT",  "Dilip Tupe", "BJP"),
    (17, "Londhe Khandu Satish", "BJP",  "Hemlata Nilesh Magar", "NCP",  "Payal Viraj Tupe", "BJP",  "Prashant (Mama) Tupe", "BJP"),
    (18, "Adv. Kedari Sahil Shivaji", "Congress",  "Kalinda Muralidhar Punde", "BJP",  "Komal Samir Shendkar", "BJP",  "Jagtap Prashant Sudam", "Congress"),
    (19, "Tasleem Shaikh", "Congress",  "Asiya Maniyar", "Congress",  "Kashif Sayyad", "Congress",  "Gafoor Pathan", "NCP-SP"),
    (20, "Aaba (Rajendra) Y. Shilimkar", "BJP",  "Divekar Tanvi Prashant", "BJP",  "Deshpande Mansi Manoj", "BJP",  "Gaurav Ganesh Ghule", "NCP"),
    (21, "Vairage Prasannajit Bharat", "BJP",  "Shilimkar Siddhi Avinash", "BJP",  "Chorbele Manisha Pravin", "BJP",  "Bhimale Srinath Yashwant", "BJP"),
    (22, "Mrunal Pandurang (Bappu) Kamble", "BJP",  "Rafiq Abdul Rahim Sheikh", "Congress",  "Archana Tushar Patil", "BJP",  "Vivek Mahadev Yadav", "BJP"),
    (23, "Javale Pallavi Chandrashekhar", "BJP",  "Andekar Sonali Vanraj", "NCP",  "Andekar Lakshmi Udayakant", "NCP",  "Dhanwade Vishal Gorakh", "BJP"),
    (24, "Bahirat Kalpana Dilip", "BJP",  "Ujwala Ganesh Yadav", "BJP",  "Devendra (Chhotu) Wadke", "BJP",  "Bidkar Ganesh Madhukar", "BJP"),
    (25, "Sau. Swapnali Nitin Pandit", "BJP",  "Raghavendra (Bappu) Mankar", "BJP",  "Swarada Gaurav Bapat", "BJP",  "Tilak Kunal Shailesh", "BJP"),
    (26, "Ganesh Bugaji Kalyankar", "NCP",  "Malwade Sneha Namdev", "BJP",  "Aishwarya Samrat Thorat", "BJP",  "Ajay Appasaheb Khedekar", "BJP"),
    (27, "Mahesh (Amar) Vilas Awale", "BJP",  "Smita Vaste", "BJP",  "Gaud Lata Raghunath", "BJP",  "Shr. Dheeraj Ramachandra Ghate", "BJP"),
    (28, "Rithe Vrushali Anand", "BJP",  "Gadade Priya Shivaji", "NCP",  "Suraj Nathuram Lokhande", "NCP",  "Adv. Prasanna (Dada) Ghanshyam Jagtap", "BJP"),
    (29, "Pande Sunil Namdev", "BJP",  "Adv. Sawalekar Mitali Kuldeep", "BJP",  "Khardekar Manjushree Sandeep", "BJP",  "Joshi Puneeth Srikant", "BJP"),
    (30, "Dudhane Swapnil Devaram", "NCP",  "Barate Reshma Santosh", "BJP",  "Tejashree Mahesh Pawale", "BJP",  "Barate Rajesh Kisan", "BJP"),
    (31, "Mathwad Dinesh Mahadev", "BJP",  "Jyotsna Jagannath Kulkarni", "BJP",  "Vasanti Navnath Jadhav", "BJP",  "Sutar Prithviraj Shashikant", "BJP"),
    (32, "Bhosale Harshada Shantanu", "BJP",  "Barate Bharatbhushan Sharadchandra", "BJP",  "Wanjale Sayali Rameshbhai", "BJP",  "Dodke Sachin Shivajirao", "BJP"),
    (33, "Dhanashree Dattatray Kolhe", "BJP",  "Anita Tukaram Ingle", "NCP-SP",  "Nanekar Subhash Muralidhar", "BJP",  "Sopan (Kaka) Chavan", "NCP-SP"),
    (34, "Charwad Haridas Krishna", "BJP",  "Komal Sarang Navale", "BJP",  "Jayshree Satyawan Bhumkar", "BJP",  "Raju Murlidhar Laygude", "BJP"),
    (35, "Gosavi Jyoti Kishor", "BJP",  "Manjusha Deepak Nagpure", "BJP",  "More Sachin Raosaheb", "BJP",  "Shrikant Shashikant Jagtap", "BJP"),
    (36, "Veena Ganesh Ghosh", "BJP",  "Bhosale Shailaja Arun", "BJP",  "Sai Prashant Thopte", "BJP",  "Mahesh Nanasaheb Wable", "BJP"),
    (37, "Balabhau (Kishor) Uttam Dhankawade", "BJP",  "Tapkir Varsha Vilas", "BJP",  "Badak Tejashree Sachin", "BJP",  "Arun Bhagwan Rajwade", "BJP"),
    (38, "Smita Sudhir Kondhare", "NCP",  "Beldare Sandeep Balasaheb", "BJP",  "Beldare Seema Yuvraj", "NCP",  "Chorghe Pratibha Rohidas", "BJP"),
    (39, "Varsha Bhimrao Sathe", "BJP",  "Pratik Prakash Kadam", "NCP",  "Dhadve Rupali Dinesh", "BJP",  "Bala (Pramod) Premchand Oswal", "BJP"),
    (40, "Archana Amit Jagtap", "BJP",  "Kamthe Vrushali Sunil", "BJP",  "Kadam Tushar Puja", "BJP",  "Tilekar Ranjana Kundalik", "BJP"),
    (41, "Atul Tarawade", "BJP",  "Bandal Nivrutti Dnyanoba", "NCP",  "Shweta Sachin Ghule", "BJP",  "Snehal Dagde", "BJP"),
]

# ── MLA mapping: (constituency, mla_name, party, [ward_numbers...]) ──
mla_map = [
    ("Vadgaon Sheri",      "Bapusaheb Tukaram Pathare",   "NCP-SP", [1, 2, 3, 4, 5, 6]),
    ("Shivajinagar",       "Siddharth Shirole",           "BJP",    [7, 8, 9, 11, 12, 29]),
    ("Kothrud",            "Chandrakant Patil",           "BJP",    [10, 31, 32, 35]),
    ("Pune Cantonment (SC)","Sunil Kamble",               "BJP",    [13, 14, 21, 22]),
    ("Kasba Peth",         "Hemant Rasane",               "BJP",    [20, 23, 24, 25, 26]),
    ("Parvati",            "Madhuri Misal",               "BJP",    [27, 28, 30, 36]),
    ("Khadakwasla",        "Bhimrao Tapkir",              "BJP",    [33, 34, 37, 38, 39, 40, 41]),
    ("Hadapsar",           "Chetan Tupe",                 "NCP-SP", [15, 16, 17, 18, 19]),
]

# ── MP ──
mp_name = "Murlidhar Mohol"
mp_party = "BJP"
mp_constituency = "Pune"

# ═══════════════════════════════════════════════════════════════════
print("Step 1: Clear existing representatives")
cur.execute("DELETE FROM representatives")
print(f"  Deleted {cur.rowcount} rows")

# ═══════════════════════════════════════════════════════════════════
print("\nStep 2: Insert corporators with corrected names + avatars")
labels = ['A', 'B', 'C', 'D']
inserted = 0
for row in corporators:
    wn = row[0]
    cur.execute("SELECT id FROM wards WHERE ward_number = ?", (wn,))
    wid = cur.fetchone()["id"]
    for i, label in enumerate(labels):
        name = row[1 + i * 2]
        party = row[2 + i * 2]
        cur.execute(
            """INSERT INTO representatives (ward_id, type, name, party, label, photo_path)
               VALUES (?, 'corporator', ?, ?, ?, ?)""",
            (wid, name, party, label, avatar(name))
        )
        inserted += 1
    if wn == 38:
        for wn_inner in [38]:
            cur.execute("SELECT id FROM wards WHERE ward_number = ?", (wn_inner,))
            wid = cur.fetchone()["id"]
            cur.execute(
                """INSERT INTO representatives (ward_id, type, name, party, label, photo_path)
                   VALUES (?, 'corporator', ?, ?, ?, ?)""",
                (wid, "Vyankoji Khopde", "BJP", "E", avatar("Vyankoji Khopde"))
            )
            inserted += 1
        print(f"  Ward {wn}: inserted 5 corporators")
    elif wn % 5 == 0:
        print(f"  Ward {wn}: inserted 4 corporators")
print(f"  Total: {inserted} corporators")

# ═══════════════════════════════════════════════════════════════════
print("\nStep 3: Insert MLA entries with avatars")
mla_inserted = 0
for constituency, mla_name, party, ward_nums in mla_map:
    for wn in ward_nums:
        cur.execute("SELECT id FROM wards WHERE ward_number = ?", (wn,))
        wid = cur.fetchone()["id"]
        cur.execute(
            """INSERT INTO representatives (ward_id, type, name, party, constituency, photo_path)
               VALUES (?, 'mla', ?, ?, ?, ?)""",
            (wid, mla_name, party, constituency, avatar(mla_name))
        )
        mla_inserted += 1
print(f"  Inserted {mla_inserted} MLA entries")

# ═══════════════════════════════════════════════════════════════════
print("\nStep 4: Insert MP entries with avatars")
mp_inserted = 0
for wn in range(1, 42):
    cur.execute("SELECT id FROM wards WHERE ward_number = ?", (wn,))
    wid = cur.fetchone()["id"]
    cur.execute(
        """INSERT INTO representatives (ward_id, type, name, party, constituency, photo_path)
           VALUES (?, 'mp', ?, ?, ?, ?)""",
        (wid, mp_name, mp_party, mp_constituency, avatar(mp_name))
    )
    mp_inserted += 1
print(f"  Inserted {mp_inserted} MP entries")

# ═══════════════════════════════════════════════════════════════════
print("\nStep 5: Update wards table with fallback data")
for row in corporators:
    wn = row[0]
    cur.execute("""
        UPDATE wards SET
            corporator_a_name = ?, corporator_a_party = ?,
            corporator_b_name = ?, corporator_b_party = ?,
            corporator_c_name = ?, corporator_c_party = ?,
            corporator_d_name = ?, corporator_d_party = ?
        WHERE ward_number = ?
    """, (row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], wn))

# Build ward_number -> (mla_name, constituency, party) lookup
mla_lookup = {}
for constituency, mla_name, party, ward_nums in mla_map:
    for wn in ward_nums:
        mla_lookup[wn] = (mla_name, constituency, party)

for wn in range(1, 42):
    mla_name, mla_const, mla_party = mla_lookup[wn]
    cur.execute("""
        UPDATE wards SET
            mla_name = ?, mla_constituency = ?, mla_party = ?,
            mp_name = ?, mp_constituency = ?, mp_party = ?
        WHERE ward_number = ?
    """, (mla_name, mla_const, mla_party, mp_name, mp_constituency, mp_party, wn))

print("  Wards table updated for all 41 wards")

# ═══════════════════════════════════════════════════════════════════
conn.commit()

print("\n=== Verification ===")
all_reps = cur.execute("SELECT type, label, ward_id, name FROM representatives ORDER BY ward_id, type, label").fetchall()
print(f"Total representative rows: {len(all_reps)}")

corp_count = sum(1 for r in all_reps if r["type"] == "corporator")
mla_count = sum(1 for r in all_reps if r["type"] == "mla")
mp_count = sum(1 for r in all_reps if r["type"] == "mp")
print(f"  Corporators: {corp_count}  MLA: {mla_count}  MP: {mp_count}")

if corp_count == 165 and mla_count == 41 and mp_count == 41:
    print("ALL DATA CORRECT ✅")
else:
    print("DATA MISMATCH ❌")

conn.close()
print("\nDone!")
