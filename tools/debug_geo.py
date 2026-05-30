import json
path = "../backend/data/pune-2022-wards.geojson"
features = json.load(open(path, encoding="utf-8"))["features"]
nums = []
for f in features:
    p = f["properties"]
    wn = p.get("wardnum") or p.get("prabhag_number") or p.get("ward_number")
    nums.append(int(wn))

print(f"Total: {len(nums)}")
print(f"Unique: {len(set(nums))}")
print(f"Min: {min(nums)}, Max: {max(nums)}")

# Check for duplicates
from collections import Counter
dupes = {n: c for n, c in Counter(nums).items() if c > 1}
print(f"Duplicates: {dupes}")

# Show all ward numbers
for i, n in enumerate(nums):
    print(f"{i}: ward_number={n}")
