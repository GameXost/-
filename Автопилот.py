import krpc
import time
import csv
from math import sqrt
import numpy as np


# Подключаемся к игре
conn = krpc.connect(name='Автопилот Протон-К')
vessel = conn.space_center.active_vessel

# Начальные значения работы ступеней
stage_2, stage_3, stage_1 = True, True, True

# Создаем файл для записи данных
PATH = 'ksp_first_try_info.csv'
with open(PATH, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Altitude", "Vertical Velocity", "Horizontal Velocity", "Total Velocity", "Drag", "Displacement"])

    # Подготовка к запуску
    vessel.control.sas = False
    vessel.control.rcs = False
    vessel.control.throttle = 1.0

    print('Запуск через 3...')
    time.sleep(1)
    print('2...')
    time.sleep(1)
    print('1...')
    time.sleep(1)

    # Счетчик времени
    start_time = conn.space_center.ut

    # Начальная позиция для расчета смещения
    initial_position = vessel.position(vessel.orbit.body.reference_frame)

    # Длина вектора
    initial_position_vec_length = np.linalg.norm(initial_position)

    vessel.auto_pilot.engage()
    vessel.control.activate_next_stage()

    print(f"Пуск!\nВремя старта: {start_time:.2f} с")


    # Основной цикл полета
    while True:
        #Вычисление оставшегося топлива у ступеней
        fuel_1 = vessel.resources_in_decouple_stage(-1, cumulative=False).amount("LiquidFuel")
        fuel_2 = vessel.resources_in_decouple_stage(4, cumulative=False).amount('LiquidFuel')
        fuel_3 = vessel.resources_in_decouple_stage(5, cumulative=False).amount("LiquidFuel")

        # Настоящее время
        ut = conn.space_center.ut

        # Прошедшее время
        elapsed_time = ut - start_time

        # Сбор данных
        altitude = vessel.flight().mean_altitude
        speed = vessel.flight(vessel.orbit.body.reference_frame).speed
        drag_x, drag_y, drag_z = vessel.flight().drag
        drag = sqrt(drag_x ** 2 + drag_y ** 2 + drag_z ** 2)

        # Текущее положение для расчета смещения
        current_position = vessel.position(vessel.orbit.body.reference_frame)

        # Расчет смещения
        current_position = current_position / np.linalg.norm(current_position) * initial_position_vec_length
        horizontal_displacement = np.linalg.norm(current_position - initial_position)

        # Получение скоростей по осям
        vertical_speed = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed
        horizontal_speed = vessel.flight(vessel.orbit.body.reference_frame).horizontal_speed

        # Записываем данные в файл
        writer.writerow(
            [elapsed_time, altitude, vertical_speed, horizontal_speed, speed, drag, horizontal_displacement])

        # Наклон ракеты в зависимости от высоты
        vessel.auto_pilot.target_roll = 0
        if altitude < 250_000:
            target_pitch = 90 * (1 - altitude / 250_000)
            vessel.auto_pilot.target_pitch_and_heading(target_pitch, 90)
        else:
            vessel.auto_pilot.target_pitch_and_heading(0, 90)
        #Обновление угла ракеты
        vessel.auto_pilot.target_pitch_and_heading(target_pitch, 90)

        # Проверка на оставшееся топливо, если топлива нет, ступень отсоединяется
        if fuel_3 < 1.0 and stage_3 == True:
            time.sleep(1)
            vessel.control.activate_next_stage()
            stage_3 = False

        if fuel_2 < 1.0 and stage_2 == True:
            vessel.control.activate_next_stage()
            time.sleep(1)
            stage_2 = False
            vessel.control.activate_next_stage()

        if fuel_1 < 1.0 and stage_1 == True:
            time.sleep(1)
            vessel.control.activate_next_stage()
            stage_1 = False
            print('hui')

        # Проверка на достижение заданной высоты
        if altitude > 350_000:
            vessel.control.throttle = 0.0
            print('Достигнута заданная высота')
            break


        time.sleep(0.1)