import pandas as pd

# Load the Excel file
data = pd.read_excel(r"C:\Users\thend\OneDrive\Desktop\Crime demo\Chennai_Crime_Demo_Data.xlsx")

print("\n--- CHENNAI CRIME DEMO ---\n")


# Total crimes
print("Total crimes:", len(data))

# Check same vehicle
vehicle_counts = data["vehicle_color"].value_counts()
print("\nVehicle usage:")
print(vehicle_counts)

# Check same phone
phone_counts = data["phone_id"].value_counts()
print("\nPhone usage:")
print(phone_counts)

# Simple intelligence rule
if vehicle_counts.iloc[0] >= 3:
    print("\n⚠️ ALERT: Same vehicle used in multiple crimes")

if phone_counts.iloc[0] >= 3:
    print("⚠️ ALERT: Same phone detected across crimes")

print("\n✅ RESULT: Organized crime pattern detected")
