from controller import Supervisor, Motor, DistanceSensor, LED
import random

# --- Inicialização ---
robot = Supervisor()
time_step = int(robot.getBasicTimeStep())

# --- Parâmetros de movimento ---
FORWARD_SPEED = 6.28
REVERSE_SPEED = -4.0
PUSH_SPEED = 5.0
PUSH_TIME = 400   # duração para empurrar em ms
REVERSE_TIME = 250  # duração da ré em ms
TURN_MIN = 0.3   # radianos
TURN_MAX = 2.0   # radianos
SENSOR_LIMIT = 200
ENCODER_DELTA = 0.04

# --- Configuração de dispositivos ---
left_motor = robot.getDevice('left wheel motor')
right_motor = robot.getDevice('right wheel motor')
for m in (left_motor, right_motor):
    m.setPosition(float('inf'))
    m.setVelocity(0)

left_encoder = robot.getDevice('left wheel sensor')
left_encoder.enable(time_step)

led_pan = [robot.getDevice(f'led{i}') for i in range(10)]
for led in led_pan:
    led.set(0)

front_sensors = [robot.getDevice(f'ps{i}') for i in (0, 7)]
for s in front_sensors:
    s.enable(time_step)

# --- Estados ---
IDLE = 0
PUSH = 1
BACK = 2
SPIN = 3
HALT = 4
state = IDLE

# --- Variáveis de controle ---
tick_count = 0
push_start = 0
back_ticks = 0
spin_ticks = 0
target_spin = 0
led_timer = 0
led_flag = 0

# --- Loop principal ---
while robot.step(time_step) != -1:
    sensor_vals = [s.getValue() for s in front_sensors]
    encoder_val = left_encoder.getValue()
    
    if state == IDLE:
        # Andar adiante
        left_motor.setVelocity(FORWARD_SPEED)
        right_motor.setVelocity(FORWARD_SPEED)
        # Se bater, começa a empurrar
        if any(v > SENSOR_LIMIT for v in sensor_vals):
            state = PUSH
            tick_count = 0
            push_start = encoder_val

    elif state == PUSH:
        # Empurra objeto lentamente
        left_motor.setVelocity(PUSH_SPEED)
        right_motor.setVelocity(PUSH_SPEED)
        tick_count += time_step
        if tick_count >= PUSH_TIME:
            # Verifica se deslocou
            if abs(left_encoder.getValue() - push_start) >= ENCODER_DELTA:
                state = HALT
                print("Objeto leve detectado: parando")
            else:
                state = BACK
                back_ticks = 0

    elif state == BACK:
        # Ré para ganhar espaço
        left_motor.setVelocity(REVERSE_SPEED)
        right_motor.setVelocity(REVERSE_SPEED)
        back_ticks += time_step
        if back_ticks >= REVERSE_TIME:
            # Prepara giro aleatório
            angle = random.uniform(TURN_MIN, TURN_MAX)
            target_spin = int(angle * 60)
            spin_ticks = 0
            # Define direção de giro
            if random.choice((True, False)):
                left_motor.setVelocity(-FORWARD_SPEED)
                right_motor.setVelocity(FORWARD_SPEED)
            else:
                left_motor.setVelocity(FORWARD_SPEED)
                right_motor.setVelocity(-FORWARD_SPEED)
            state = SPIN

    elif state == SPIN:
        spin_ticks += 1
        if spin_ticks >= target_spin:
            state = IDLE

    elif state == HALT:
        # Para e pisca LEDs
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
        led_timer += time_step
        if led_timer >= 500:
            led_timer = 0
            led_flag ^= 1
            for led in led_pan:
                led.set(led_flag)
