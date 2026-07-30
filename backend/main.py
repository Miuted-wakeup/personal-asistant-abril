import sys
import os
import time

# agrega directorio raiz al path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.logger import setup_logger
from backend.brain_llm import BrainLLM
from backend.ipc_server import notifier

logger = setup_logger("Main")

import json
import random

class AbrilOrchestrator:
    def __init__(self):
        # Máquina de estados principal
        self.state = "IDLE"
        logger.info("Iniciando Abril Orchestrator (Fase 10)")
        self.llm = None
        self.personality = {}
        self._init_modules()

    def _init_modules(self):
        logger.info("Cargando módulos y personalidad...")
        self.llm = BrainLLM()
        
        # Cargar archivo de personalidad (Zero-Latency Fillers)
        personality_path = os.path.join(os.path.dirname(__file__), "personality.json")
        try:
            with open(personality_path, "r", encoding="utf-8") as f:
                self.personality = json.load(f).get("transitions", {})
        except Exception as e:
            logger.warning(f"No se pudo cargar personality.json: {e}")
            self.personality = {"thinking": ["Un momento..."], "executing": ["Voy con ello."]}

    def transition_to(self, new_state):
        """Cambia el estado, actualiza IPC y retorna el tiempo actual para instrumentación."""
        self.state = new_state
        notifier.set_state(new_state)
        return time.perf_counter()

    def get_filler_phrase(self, category):
        phrases = self.personality.get(category, ["..."])
        return random.choice(phrases)

    def run_simulated_loop(self):
        """Bucle interactivo simulando el flujo físico completo."""
        logger.info("Orquestador en línea. Escribe 'salir' para terminar.")
        current_user = "Muted"
        
        while True:
            try:
                # 1. IDLE -> LISTENING (Simulado por el input)
                # En la versión real, openWakeWord nos sacará de IDLE.
                self.transition_to("IDLE")
                
                # Simulamos la espera de Wake Word
                user_input = input(f"\n[{self.state}] Esperando audio (escribe tu petición, {current_user}): ")
                if user_input.lower() in ["salir", "exit"]:
                    break
                
                t_start = self.transition_to("LISTENING")
                # Simulamos grabar audio...
                time.sleep(0.1) # latencia falsa de grabación corta
                
                # 2. LISTENING -> TRANSCRIBING
                t_transcribing = self.transition_to("TRANSCRIBING")
                # En la vida real aquí llamaríamos a Groq Whisper
                # Como es simulado, ya tenemos el texto en user_input
                
                # 3. TRANSCRIBING -> THINKING
                t_thinking = self.transition_to("THINKING")
                
                # ---- ZERO LATENCY FILLER ----
                # Inmediatamente al entrar a pensar, lanzamos un filler para latencia 0
                filler = self.get_filler_phrase("thinking")
                print(f"Abril (Audio Rápido): {filler}")
                # -----------------------------
                
                respuesta = self.llm.generate_response(user_input, user_name=current_user)
                
                # 4. THINKING -> SPEAKING
                t_speaking = self.transition_to("HABLANDO")
                print(f"Abril: {respuesta}")
                
                # Simulamos el tiempo que tarda el TTS en leer la respuesta en voz alta
                time.sleep(1.5)
                
                # Medición de Tiempos (Instrumentación)
                t_end = time.perf_counter()
                
                ms_listen = (t_transcribing - t_start) * 1000
                ms_transcribe = (t_thinking - t_transcribing) * 1000
                ms_think = (t_speaking - t_thinking) * 1000
                ms_speak = (t_end - t_speaking) * 1000
                
                logger.info(f"[Instrumentación] Listen: {ms_listen:.1f}ms | Transcribe: {ms_transcribe:.1f}ms | Think(LLM): {ms_think:.1f}ms | Speak(TTS): {ms_speak:.1f}ms")

            except KeyboardInterrupt:
                break
        
        logger.info("Apagando orquestador.")

if __name__ == "__main__":
    orchestrator = AbrilOrchestrator()
    orchestrator.run_simulated_loop()
