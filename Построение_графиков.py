import matplotlib.pyplot as plt
import pandas as pd


# Открываем файл для записи данных
KSP_PATH = "ksp_first_try_info.csv"
MATH_PATH = "mathod.csv"
POGR_PATH = "pogreshnosti.csv"

# Получение данных из симуляции KSP
data = pd.read_csv(KSP_PATH)
data_math = pd.read_csv(MATH_PATH)
data_pogr = pd.read_csv(POGR_PATH)

# Получение данных из КСП
time_data_ksp = data['Time']
altitude_data_ksp = data['Altitude']
vertical_velocity_data_ksp = data['Vertical Velocity']
horizontal_velocity_data_ksp = data['Horizontal Velocity']
total_velocity_data_ksp = data['Total Velocity']



# получение данных из матмодели
time_data = data_math['Time']
altitude_data = data_math['Altitude']
vertical_velocity_data = data_math['Vertical Velocity']
horizontal_velocity_data = data_math['Horizontal Velocity']
total_velocity_data = data_math['Total Velocity']

# получение данных погрешностей
time_pogr = data_pogr["Time"]
speed_pogr = data_pogr["Total Velocity"]
altitude_pogr = data_pogr["Altitude"]
abs_porg_alt = data_pogr["pogr_altitude"]
abs_pogr_speed = data_pogr["pogr_speed"]


# Построение графиков
plt.figure(figsize=(15, 15))

# График высоты
plt.subplot(3, 2, 1)
plt.plot(time_data, altitude_data, color = 'blue')
plt.plot(time_data_ksp, altitude_data_ksp, color='orange', label="Высота (м)")
plt.plot(time_pogr, altitude_pogr, color='red')
plt.title('Высота от времени')
plt.xlabel('Время (с)')
plt.ylabel('Высота (м)')


# График скорости
plt.subplot(3, 2, 2)
plt.plot(time_data, total_velocity_data, color='blue')
plt.plot(time_data_ksp, total_velocity_data_ksp, color='orange', label="Скорость (м/с)")
plt.plot(time_pogr, speed_pogr, color='red')
plt.title('Скорость от времени')
plt.xlabel('Время (с)')
plt.ylabel('Скорость (м/с)')


plt.tight_layout()
plt.show()