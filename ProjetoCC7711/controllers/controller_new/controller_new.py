from controller import Supervisor, DistanceSensor, Motor, LED

robo = Supervisor()
passo_temporal = int(robo.getBasicTimeStep())


# CONFIGURAÇÕES DO ROBÔ
_velocidade = 6.28
_limiar_sensor = 250
_limiar_empurrar = 1200  
_limiar_colisao_dupla = 2    
_limiar_colisao_direcao = 15  
_angulo_curva = 2.4
_limite_movimento = 0.01
_tempo_parado = 2000       
_motor_esquerdo = robo.getDevice('left wheel motor')
_motor_direito = robo.getDevice('right wheel motor')
_motor_esquerdo.setPosition(float('inf'))
_motor_direito.setPosition(float('inf'))
encoder_esquerdo = robo.getDevice('left wheel sensor')
encoder_esquerdo.enable(passo_temporal)
leds = [robo.getDevice(f'led{i}') for i in range(10)]
estado_led = 0
temporizador_led = 0
contador_colisoes = 0
angulo_curva_atual = _angulo_curva
direcao_curva = 1
nomes_sensores = [f"ps{i}" for i in range(8)]
sensores = [robo.getDevice(nome) for nome in nomes_sensores]
for sensor in sensores:
    sensor.enable(passo_temporal)

temporizador_travado = 0
travado = False

# DEFINIÇÃO DOS ESTADOS
MOVENDO = 0
EMPURRANDO = 1
VIRANDO = 2
ENCONTRADO = 3

ESTADO = MOVENDO
angulo_inicio_reversao = 0
angulo_inicio_curva = 0
caixa_leve_detectada = False
temporizador_empurrao = 0

# IDENTIFICAÇÃO DAS CAIXAS
caixas = []
posicoes_iniciais_caixas = []
filhos_raiz = robo.getRoot().getField("children")

for i in range(filhos_raiz.getCount()):
    no = filhos_raiz.getMFNode(i)
    nome_def = no.getDef()
    if nome_def and nome_def.startswith("CAIXA"):
        caixas.append((nome_def, no))
        posicoes_iniciais_caixas.append(no.getPosition())


while robo.step(passo_temporal) != -1:
    if not caixa_leve_detectada:
        for indice, (nome_caixa, caixa) in enumerate(caixas):
            posicao = caixa.getPosition()
            posicao_inicial = posicoes_iniciais_caixas[indice]
            dif_x = abs(posicao[0] - posicao_inicial[0])
            dif_y = abs(posicao[1] - posicao_inicial[1])
            if dif_x >= _limite_movimento or dif_y >= _limite_movimento:
                caixa_leve_detectada = True
                ESTADO = ENCONTRADO
                print(f"A caixa leve é a {nome_caixa}")
                break

    leituras_sensores = [sensor.getValue() for sensor in sensores]
    posicao_esquerda = encoder_esquerdo.getValue()
    
    if ESTADO == MOVENDO:
        lateral_travada = any(leituras_sensores[i] > _limiar_sensor for i in range(1, 7))
        if lateral_travada:
            temporizador_travado += passo_temporal
        else:
            temporizador_travado = 0

        if temporizador_travado >= _tempo_parado:
            temporizador_travado = 0
            travado = True
            temporizador_empurrao = 0
            ESTADO = EMPURRANDO
            _motor_esquerdo.setVelocity(_velocidade)
            _motor_direito.setVelocity(_velocidade)
            continue

    if ESTADO == MOVENDO:
        if leituras_sensores[0] > _limiar_sensor or leituras_sensores[7] > _limiar_sensor:
            temporizador_empurrao = 0
            ESTADO = EMPURRANDO
            _motor_esquerdo.setVelocity(_velocidade)
            _motor_direito.setVelocity(_velocidade)
        else:
            _motor_esquerdo.setVelocity(_velocidade)
            _motor_direito.setVelocity(_velocidade)

    elif ESTADO == EMPURRANDO:
        temporizador_empurrao += passo_temporal
        _motor_esquerdo.setVelocity(_velocidade)
        _motor_direito.setVelocity(_velocidade)
        if temporizador_empurrao >= _limiar_empurrar:
            angulo_inicio_reversao = posicao_esquerda
           
            contador_colisoes += 1

            if contador_colisoes % _limiar_colisao_direcao == 0:
                direcao_curva *= -1

            angulo_curva_atual = _angulo_curva * 2 if contador_colisoes % _limiar_colisao_dupla == 0 else _angulo_curva


            angulo_inicio_curva = encoder_esquerdo.getValue()
            ESTADO = VIRANDO
            _motor_esquerdo.setVelocity(direcao_curva * -_velocidade)
            _motor_direito.setVelocity(direcao_curva * _velocidade)

    elif ESTADO == VIRANDO:
        diferenca_angulo = abs(encoder_esquerdo.getValue() - angulo_inicio_curva)
        if diferenca_angulo >= angulo_curva_atual:
            ESTADO = MOVENDO
            _motor_esquerdo.setVelocity(_velocidade)
            _motor_direito.setVelocity(_velocidade)
        else:
            _motor_esquerdo.setVelocity(direcao_curva * -_velocidade)
            _motor_direito.setVelocity(direcao_curva * _velocidade)

    elif ESTADO == ENCONTRADO:
        _motor_esquerdo.setVelocity(-_velocidade)
        _motor_direito.setVelocity(_velocidade)
        temporizador_led += passo_temporal
        if temporizador_led >= 500:
            estado_led = 1 - estado_led
            for led in leds:
                led.set(estado_led)
            temporizador_led = 0