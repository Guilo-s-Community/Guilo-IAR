#include <webots/robot.h>
#include <webots/motor.h>
#include <webots/distance_sensor.h>
#include <webots/led.h>
#include <webots/supervisor.h>
#include <webots/position_sensor.h>
#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>


#define NUM_LEDS 10
#define NUM_SENSORES 8
#define LIMIAR_SENSOR 250
#define LIMIAR_EMPURRAR 1200
#define LIMIAR_COLISAO_DUPLA 3
#define LIMIAR_COLISAO_DIRECAO 20
#define ANGULO_CURVA 3
#define LIMITE_MOVIMENTO 0.01
#define VELOCIDADE 6.28

int main() {
  wb_robot_init();
  int passo_temporal = (int)wb_robot_get_basic_time_step();

  // Motores
  WbDeviceTag motor_esquerdo = wb_robot_get_device("left wheel motor");
  WbDeviceTag motor_direito = wb_robot_get_device("right wheel motor");
  wb_motor_set_position(motor_esquerdo, INFINITY);
  wb_motor_set_position(motor_direito, INFINITY);

  // Encoder
  WbDeviceTag encoder_esquerdo = wb_robot_get_device("left wheel sensor");
  wb_position_sensor_enable(encoder_esquerdo, passo_temporal);

  // LEDs
  WbDeviceTag leds[NUM_LEDS];
  for (int i = 0; i < NUM_LEDS; i++)
    leds[i] = wb_robot_get_device((char[8]){ 'l','e','d',i+'0','\0' });

  // Sensores de distância
  WbDeviceTag sensores[NUM_SENSORES];
  char nome_sensor[5];
  for (int i = 0; i < NUM_SENSORES; i++) {
    sprintf(nome_sensor, "ps%d", i);
    sensores[i] = wb_robot_get_device(nome_sensor);
    wb_distance_sensor_enable(sensores[i], passo_temporal);
  }

  // Variáveis de controle
  int temporizador_led = 0, estado_led = 0, contador_colisoes = 0;
  double angulo_curva_atual = ANGULO_CURVA;
  int direcao_curva = 1;
  int temporizador_travado = 0, temporizador_empurrao = 0;
  double angulo_inicio_curva = 0;
  bool caixa_leve_detectada = false, travando = false, empurrando = false, virando = false, encontrado = false;

  // Supervisor para caixas
  WbNodeRef root = wb_supervisor_node_get_root();
  WbFieldRef filhos_raiz = wb_supervisor_node_get_field(root, "children");
  int caixas_count = 0;
  WbNodeRef caixas[32];
  double posicoes_iniciais_caixas[32][3];

  int filhos_count = wb_supervisor_field_get_count(filhos_raiz);
  for (int i = 0; i < filhos_count; i++) {
    WbNodeRef no = wb_supervisor_field_get_mf_node(filhos_raiz, i);
    const char *nome_def = wb_supervisor_node_get_def(no);
    if (nome_def && strncmp(nome_def, "CAIXA", 5) == 0) {
      caixas[caixas_count] = no;
      const double *pos = wb_supervisor_node_get_position(no);
      posicoes_iniciais_caixas[caixas_count][0] = pos[0];
      posicoes_iniciais_caixas[caixas_count][1] = pos[1];
      posicoes_iniciais_caixas[caixas_count][2] = pos[2];
      caixas_count++;
    }
  }

  // Funções auxiliares
  void mover_frente() {
    wb_motor_set_velocity(motor_esquerdo, VELOCIDADE);
    wb_motor_set_velocity(motor_direito, VELOCIDADE);
  }
  void empurrar_func() {
    wb_motor_set_velocity(motor_esquerdo, VELOCIDADE);
    wb_motor_set_velocity(motor_direito, VELOCIDADE);
  }
  void virar() {
    wb_motor_set_velocity(motor_esquerdo, direcao_curva * -VELOCIDADE);
    wb_motor_set_velocity(motor_direito, direcao_curva * VELOCIDADE);
  }
  void parar() {
    wb_motor_set_velocity(motor_esquerdo, 0);
    wb_motor_set_velocity(motor_direito, 0);
  }
  void celebrar() {
    wb_motor_set_velocity(motor_esquerdo, -VELOCIDADE);
    wb_motor_set_velocity(motor_direito, VELOCIDADE);
    temporizador_led += passo_temporal;
    if (temporizador_led >= 500) {
      estado_led = 1 - estado_led;
      for (int i = 0; i < NUM_LEDS; i++)
        wb_led_set(leds[i], estado_led);
      temporizador_led = 0;
    }
  }
  void detectar_caixa_leve() {
    for (int i = 0; i < caixas_count; i++) {
      const double *pos = wb_supervisor_node_get_position(caixas[i]);
      double dif_x = fabs(pos[0] - posicoes_iniciais_caixas[i][0]);
      double dif_y = fabs(pos[1] - posicoes_iniciais_caixas[i][1]);
      if (dif_x >= LIMITE_MOVIMENTO || dif_y >= LIMITE_MOVIMENTO) {
        caixa_leve_detectada = true;
        encontrado = true;
        printf("A caixa leve é a %s\n", wb_supervisor_node_get_def(caixas[i]));
        break;
      }
    }
  }

  // Loop principal
  while (wb_robot_step(passo_temporal) != -1) {
    if (!caixa_leve_detectada) {
      detectar_caixa_leve();
      if (encontrado) continue;
    }

    double leituras_sensores[NUM_SENSORES];
    for (int i = 0; i < NUM_SENSORES; i++)
      leituras_sensores[i] = wb_distance_sensor_get_value(sensores[i]);
    double posicao_esquerda = wb_position_sensor_get_value(encoder_esquerdo);

    if (encontrado) {
      celebrar();
      continue;
    }

    bool lateral_travada = false;
    for (int i = 1; i < 7; i++)
      if (leituras_sensores[i] > LIMIAR_SENSOR)
        lateral_travada = true;
    bool frente_obstruida = (leituras_sensores[0] > LIMIAR_SENSOR) || (leituras_sensores[7] > LIMIAR_SENSOR);

    if (virando) {
      double diferenca_angulo = fabs(wb_position_sensor_get_value(encoder_esquerdo) - angulo_inicio_curva);
      if (diferenca_angulo >= angulo_curva_atual) {
        virando = false;
        travando = false;
        empurrando = false;
        mover_frente();
      } else {
        virar();
      }
      continue;
    }

    if (empurrando) {
      temporizador_empurrao += passo_temporal;
      empurrar_func();
      if (temporizador_empurrao >= LIMIAR_EMPURRAR) {
        angulo_inicio_curva = wb_position_sensor_get_value(encoder_esquerdo);
        contador_colisoes++;
        if (contador_colisoes % LIMIAR_COLISAO_DIRECAO == 0)
          direcao_curva *= -1;
        angulo_curva_atual = (contador_colisoes % LIMIAR_COLISAO_DUPLA == 0) ? ANGULO_CURVA * 2 : ANGULO_CURVA;
        empurrando = false;
        virando = true;
      }
      continue;
    }

    if (travando) {
      if (lateral_travada) {
        temporizador_travado += passo_temporal;
      } else {
        temporizador_travado = 0;
        travando = false;
      }
      continue;
    }

    // Estado padrão: movendo
    if (lateral_travada) {
      travando = true;
      temporizador_travado = passo_temporal;
      mover_frente();
    } else if (frente_obstruida) {
      empurrando = true;
      temporizador_empurrao = 0;
      empurrar_func();
    } else {
      mover_frente();
    }
  }

  wb_robot_cleanup();
  return 0;
}