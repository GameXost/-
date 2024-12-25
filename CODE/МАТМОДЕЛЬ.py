import numpy as np
import csv
from scipy.integrate import odeint
from math import exp, sqrt


# Константы
g = 9.81  # ускорение свободного падения (м/с²)
rho_0 = 1.225  # плотность воздуха на уровне моря (кг/м³)
G = 6.67430e-11  # Гравитационная постоянная
M_kerbin = 5.2915793e22  # Масса Кербина в кг
R_kerbin = 600000  # Радиус Кербина в метрах
A = 10.0  # Площадь поперечного сечения ракеты, m² (примерное значение)
C_d = 3.3  # Коэффициент аэродинамического сопротивления

M = 0.029 # молярная масса воздуха
R = 8.314 # универсальная газовая постоянная



# Масса и характеристики ступеней
stages = [
	{"wet_mass": 531_300, "fuel_mass": 248400, "thrust": 8_274_000, "burn_time": 93, "ejection_force": 285, "area": 10},
	{"wet_mass": 175_700, "fuel_mass": 97200, "thrust": 3_000_000, "burn_time": 130, "ejection_force": 280, "area": 4},
    {"wet_mass": 39_600, "fuel_mass": 16200, "thrust": 623_920, "burn_time": 78, "ejection_force": 277, "area": 4},
]


# Функция для расчета плотности воздуха в зависимости от высоты
def air_density(h):
    if h < 86:
        T=temp_alt(h)+273
        return (rho_0*exp(-(g*M*h)/(R*T)))
    return 0

# Функция для расчета угла наклона (pitch) в зависимости от высоты
def calculate_pitch(altitude):
    if altitude < 250_000:
        return 90 * (1 - altitude / 250_000)  # Чем выше высота, тем меньше наклон
    return 0



# Функция для расчета гравитационного ускорения
def gravitational_acceleration(height):
    r = R_kerbin + height
    return G * M_kerbin / r ** 2

#вычисление темпратуры
def temperature():
    Temp = [20]
    temp0=20
    for i in range(1,86):
        if i<=11:
            temp0-=6.5
            Temp.append(temp0)
        if 11 < i <= 20:
            Temp.append(temp0)
        if 20 < i <= 32:
            temp0 += 1
            Temp.append(temp0)
        if 32 < i <= 47:
            temp0 += 2.8
            Temp.append(temp0)
        if 47 < i <= 51:
            Temp.append(temp0)
        if 51 < i <= 71:
            temp0 -=2.8
            Temp.append(temp0)
        if 71 < i <= 85:
            temp0 -= 2
            Temp.append(temp0)

    return Temp

Temp = temperature()
def temp_alt(altitude):
    return Temp[int(altitude // 1000)]


# Для системы уравнений
def equations(y, time, stage_index):
    # Распаковка состояний
    x_coord, horizontal_velocity, y_coord, vertical_velocity = y

    # Данные текущей ступени
    stage = stages[stage_index]
    fuel_mass = stage["fuel_mass"]
    thrust = stage["thrust"]
    burn_time = stage["burn_time"]
    drain_speed = fuel_mass / burn_time
    ejection_force = stage["ejection_force"]
    area = stage["area"]

    #Вычисление некоотрых значений
    cur_mass = start_mass - drain_speed * time
    vel = sqrt(pow(horizontal_velocity, 2) + pow(vertical_velocity, 2))
    pitch = calculate_pitch(y_coord)

    # Расчет гравитационного ускорения и сопротивления
    force_gravity = cur_mass * gravitational_acceleration(y_coord)
    air_density_value = air_density(y_coord)
    drag_force = 0.5 * C_d * air_density_value * vel ** 2 * area

    # Расчет ускорений
    radius = R_kerbin + y_coord
    centrifugal_force = (cur_mass * horizontal_velocity ** 2) / radius

    #вертикальное
    acceleration_vertical = ((thrust - drag_force) * np.sin(np.radians(pitch))- force_gravity) / cur_mass

    #горизонтальное
    acceleration_horizontal = ((thrust - drag_force) * np.cos(np.radians(pitch)) + centrifugal_force) / cur_mass


    # Обновление значений
    dxcoord = horizontal_velocity
    dhorizontal_velocity = acceleration_horizontal
    dycoord = vertical_velocity
    dvertical_velocity = acceleration_vertical

    #Проеверка на отстыковку ступени
    if fuel_mass - drain_speed * time <= 0:

        # После окончания сжигания топлива применяем выброс
        dhorizontal_velocity += ((ejection_force) / cur_mass) * np.cos(np.radians(pitch))
        dvertical_velocity += ((ejection_force) / cur_mass) * np.sin(np.radians(pitch))

    return [dxcoord, dhorizontal_velocity, dycoord, dvertical_velocity]


# Начальные условия
start_mass = stages[0]["wet_mass"]
initial_conditions = [0, 0, 90, 0]
# x_coord, horizontal_velocity, y_coord, vertical_velocity

# Время интегрирования
time_span = (0, stages[0]["burn_time"])
time_eval = np.linspace(time_span[0], time_span[1], 1000)

# Решение системы уравнений для первой ступени
result_first_stage = odeint(equations, initial_conditions, time_eval, args=(0,))
time_first_stage = time_eval

# Время второй ступени
start_mass = stages[1]["wet_mass"] + stages[2]["wet_mass"]
time_span = (0, stages[1]["burn_time"])
time_eval = np.linspace(time_span[0], time_span[1], 1000)

# Решение для второй ступени
result_second_stage = odeint(equations, result_first_stage[-1, :], time_eval, args=(1,))
time_second_stage = time_eval

# время для третьей ступени
start_mass = stages[2]["wet_mass"]
time_span = (0, stages[2]["burn_time"])
time_eval = np.linspace(time_span[0], time_span[1], 1000)

# Решение для третьей ступени
result_third_stage = odeint(equations, result_second_stage[-1, :], time_eval, args=(2,))
time_third_stage = time_eval


# Объединение результатов
time_second_stage += time_first_stage[-1]
time_third_stage += time_second_stage[-1]
time = np.concatenate([time_first_stage, time_second_stage, time_third_stage])

x_coords = np.concatenate([result_first_stage[:, 0], result_second_stage[:, 0], result_third_stage[:, 0]])
x_velocities = np.concatenate([result_first_stage[:, 1], result_second_stage[:, 1], result_third_stage[:, 1]])
y_coords = np.concatenate([result_first_stage[:, 2], result_second_stage[:, 2], result_third_stage[:, 2]])
y_velocities = np.concatenate([result_first_stage[:, 3], result_second_stage[:, 3], result_third_stage[:, 3]])

total_velocity = []
for i in range(len(x_velocities)):
    total_velocity.append((x_velocities[i] ** 2 +  y_velocities[i] ** 2) ** 0.5)



PATH = 'mathod.csv'
with open(PATH, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time","Altitude","Vertical Velocity","Horizontal Velocity","Total Velocity","Displacement"])
    for i in range(len(time)):
        writer.writerow([time[i], y_coords[i], y_velocities[i], x_velocities[i], total_velocity[i]] )