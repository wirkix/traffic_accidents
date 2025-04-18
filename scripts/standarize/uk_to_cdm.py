import pandas as pd
import sys
import os

# Agrega la raíz del proyecto al sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

from scripts.standarize.helpers.encoding_utils import read_csv_utf8_cleaned
# Cargar los datos
# Usa el helper en vez de pd.read_csv directamente
accidents = read_csv_utf8_cleaned("data/raw/uk/Accident_Information.csv")
vehicles = read_csv_utf8_cleaned("data/raw/uk/Vehicle_Information.csv")

# Convertir columnas de fecha y hora
accidents["Date"] = pd.to_datetime(accidents["Date"], errors="coerce")
accidents["Time"] = pd.to_datetime(accidents["Time"], format="%H:%M", errors="coerce").dt.time

# Crear accident_id como índice
accidents["accident_id"] = accidents["Accident_Index"]
vehicles["accident_id"] = vehicles["Accident_Index"]

# Crear vehicle_id como combinación única
vehicles["vehicle_id"] = vehicles["Accident_Index"] + "_" + vehicles["Vehicle_Reference"].astype(str)

# -------------------------------------
# Tabla: accidents_cdm.csv
# -------------------------------------
accidents_cdm = pd.DataFrame({
    "accident_id": accidents["accident_id"],
    "date": accidents["Date"],
    "time": accidents["Time"],
    "latitude": accidents["Latitude"],
    "longitude": accidents["Longitude"],
    "fatalities": accidents["Accident_Severity"].apply(lambda x: 1 if x == 1 else 0),
    "casualties": accidents["Number_of_Casualties"],
    "vehicles_involved": accidents["Number_of_Vehicles"],
    "weather": accidents["Weather_Conditions"],
    "road_type": accidents["Road_Type"],
    "light_conditions": accidents["Light_Conditions"],
    "speed_limit": accidents["Speed_limit"],
    "urban_or_rural": accidents["Urban_or_Rural_Area"],
    "site_conditions": (
        accidents["Carriageway_Hazards"].fillna("").astype(str) + " | " +
        accidents["Special_Conditions_at_Site"].fillna("").astype(str)
    ),
    "country": "UK"
})

# -------------------------------------
# Tabla: vehicles_cdm.csv
# -------------------------------------
vehicles_cdm = pd.DataFrame({
    "vehicle_id": vehicles["vehicle_id"],
    "accident_id": vehicles["accident_id"],
    "vehicle_type": vehicles["Vehicle_Type"],
    "impact_point": vehicles["X1st_Point_of_Impact"],
    "maneuver": vehicles["Vehicle_Manoeuvre"],
    "make": vehicles["make"],
    "model": vehicles["model"],
    "engine_capacity_cc": vehicles["Engine_Capacity_.CC."],
    "age_of_vehicle": vehicles["Age_of_Vehicle"],
    "left_hand_drive": vehicles["Was_Vehicle_Left_Hand_Drive"]
})

# -------------------------------------
# Tabla: persons_cdm.csv (solo conductores)
# -------------------------------------
# Crear person_id como combinación única
persons_cdm = pd.DataFrame({
    "person_id": vehicles["Accident_Index"] + "_" + vehicles["Vehicle_Reference"].astype(str) + "_driver",
    "accident_id": vehicles["accident_id"],
    "vehicle_id": vehicles["vehicle_id"],
    "age_band": vehicles["Age_Band_of_Driver"],
    "sex": vehicles["Sex_of_Driver"],
    "role": "driver"
})

# Crear carpeta de salida si no existe
os.makedirs("data/standarized/uk", exist_ok=True)

# Guardar resultados
accidents_cdm.to_csv("data/standarized/uk/accidents_cdm.csv", index=False)
vehicles_cdm.to_csv("data/standarized/uk/vehicles_cdm.csv", index=False)
persons_cdm.to_csv("data/standarized/uk/persons_cdm.csv", index=False)

print("Conversión completada. Archivos guardados en data/standarized/uk/")
