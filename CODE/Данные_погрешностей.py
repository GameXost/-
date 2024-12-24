import pandas as pd
import csv


KSP_PATH = "ksp_first_try_info.csv"
MATH_PATH = "mathod.csv"
POGR_PATH = "pogreshnosti.csv"

data = pd.read_csv(KSP_PATH)
data_math = pd.read_csv(MATH_PATH)

time_ksp = data["Time"]
time_math = data_math["Time"]

#Получение данных скорости
speed_ksp = list(data["Total Velocity"])
speed_math = list(data_math["Total Velocity"])

#Получение данных высоты
altitude_ksp = list(data["Altitude"])
altitude_math = list(data_math["Altitude"])

#Определение времени(посекундно)
list_int_ksp = [int(i) for i in list(time_ksp)]
list_int_math = [int(i) for i in list(time_math)]

#Списки для погрешностей
delta_speed=[]
delta_altitude=[]
abs_speed = []
abs_altitude = []

for i in range(276):
    # Составление данных для графиков
    if i in list_int_ksp and i in list_int_math:
        in1=list_int_ksp.index(i)
        in2 = list_int_math.index(i)
        delta_speed.append(abs(speed_ksp[i]-speed_math[i]))
        delta_altitude.append(abs(altitude_ksp[i]-altitude_math[i]))
        try:
            abs_speed.append((abs(speed_ksp[i]-speed_math[i])) / speed_math[i])
            abs_altitude.append((abs(altitude_ksp[i]-altitude_math[i])) / altitude_math[i])
        except ZeroDivisionError:
            abs_speed.append(abs(speed_ksp[i + 1] - speed_math[i + 1]) / (speed_math[i + 1]))
            abs_altitude.append(abs(altitude_ksp[i + 1] - altitude_math[i + 1]) / (altitude_math[i + 1]))

# Запись в файл данных погрешностей
with open(POGR_PATH, "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Time", "Total Velocity", "Altitude", "pogr_speed", "pogr_altitude"])
    for i in range(273):
        d_s = delta_speed[i]
        d_a = delta_altitude[i]
        a_s = abs_speed[i]
        a_a = abs_altitude[i]
        writer.writerow([i, d_s, d_a, a_s, a_a])

