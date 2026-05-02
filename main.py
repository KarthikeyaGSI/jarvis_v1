"""
Marketingkolabs - Local Voice Agent Main Entry Point
MIT License

Architecture:
Voice Input -> Wake Word -> Whisper STT -> Intent Parser (LLM) -> JSON Action -> Skill Router -> Execute -> TTS Confirm
With Context Tracking, Safety Confirmations, and Browser Automation
"""
import sys
import time
import logging
from pathlib import Path
from functools import partial

sys.path.insert(0, str(Path(__file__).parent))

from core.stt import STTEngine
from core.intent_parser import IntentParser
from core.tts import TTSEngine
from core.skill_router import SkillRouter
from core.config_validator import load_and_validate_config
from core.context import SessionContext
from core.safety import SafetyManager
from core.wake_word import WakeWordDetector

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('marketingkolabs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Marketingkolabs:
    """
    Main voice agent orchestrator with full system access
    Handles wake word, context tracking, safety confirmations, browser automation
    """

    def __init__(self, config_path: str = "config.yaml"):
        logger.info("Initializing Marketingkolabs with full system access...")

        self.config = load_and_validate_config(config_path)

        self.stt = STTEngine(self.config)
        self.intent_parser = IntentParser(self.config)
        self.tts = TTSEngine(self.config)
        self.router = SkillRouter(self.config)
        self.context = SessionContext(self.config.dict())
        self.safety = SafetyManager(self.config.dict(), self.tts, self.stt)

        self.wake_word = WakeWordDetector(self.config.dict())
        self.is_running = False
        self.is_processing = False

        logger.info("Initialization complete - Full system access enabled")

    def process_voice_command(self, audio_duration: float = 4.0) -> dict:
        """
        Full pipeline with context and safety:
        Record -> Transcribe -> Parse -> Context Resolve -> Safety Check -> Route -> Execute -> Confirm
        """
        if self.is_processing:
            return {'success': False, 'message': 'Already processing'}

        self.is_processing = True
        start_time = time.time()

        try:
            self.tts.speak("Listening...", blocking=False)
            text = self.stt.record_and_transcribe(duration=audio_duration)

            if not text or len(text.strip()) < 2:
                self.tts.speak("Sorry, I didn't catch that.")
                return {'success': False, 'message': 'No speech detected'}

            logger.info(f"Transcribed: '{text}'")

            # Resolve context references like "that", "it"
            context_params = self.context.resolve_reference(text)
            if context_params:
                logger.info(f"Resolved context: {context_params}")

            # Parse intent
            action = self.intent_parser.parse(text)
            logger.info(f"Parsed action: {action}")

            # Merge context into params
            if context_params and 'params' in action:
                action['params'].update(context_params)

            # Update command history
            self.context.add_command(text, action)

            # Safety check for dangerous actions
            if self.safety.requires_confirmation(action.get('skill'), action.get('action')):
                confirmed = self.safety.request_confirmation(
                    f"{action.get('action')} in {action.get('skill')}"
                )
                if not confirmed:
                    self.tts.speak("Action cancelled.")
                    return {'success': False, 'message': 'Cancelled by user'}

            # Execute action
            result = self.router.route(action)

            # Update context based on result
            if result.get('success'):
                self._update_context_from_result(action, result)

            # TTS feedback
            elapsed = (time.time() - start_time) * 1000
            logger.info(f"Total latency: {elapsed:.0f}ms")

            if result.get('success'):
                message = result.get('message', 'Done.')
                if elapsed < 2000:
                    self.tts.speak(message)
                else:
                    self.tts.speak("Done, but took too long.")
            else:
                self.tts.speak(f"Failed: {result.get('message', 'Unknown error')}")

            return result

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            self.tts.speak("An error occurred.")
            return {'success': False, 'message': str(e)}
        finally:
            self.is_processing = False

    def _update_context_from_result(self, action: dict, result: dict):
        """Update session context based on executed action"""
        skill = action.get('skill')
        params = action.get('params', {})

        if skill == 'file_ops' and 'path' in params:
            self.context.update('last_file', params['path'])
        elif skill == 'app_control' and 'app_name' in params:
            self.context.update('last_app', params['app_name'])
        elif skill == 'browser' and 'url' in result.get('data', {}):
            self.context.update('last_url', result['data']['url'])
            self.context.update('last_browser', 'browser')
        elif skill == 'browser' and 'product' in params:
            self.context.update('last_product', params['product'])

    def process_text_command(self, text: str) -> dict:
        """Process text command directly (bypass STT)"""
        return self.process_voice_command(audio_duration=0)

    def run_wake_word_mode(self):
        """Run with wake word detection (hands-free)"""
        def on_wake_word():
            if not self.is_processing:
                self.process_voice_command()

        logger.info("Wake word mode started. Say wake word to activate.")
        self.tts.speak("Voice agent ready. Say the wake word to speak.")

        self.wake_word.start(on_wake_word)

        try:
            while self.is_running:
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.wake_word.stop()

    def run_hotkey_mode(self):
        """Run in hotkey trigger mode"""
        from pynput import keyboard

        def on_activate():
            if not self.is_processing:
                logger.info("Hotkey triggered!")
                self.process_voice_command()

        logger.info("Hotkey mode started. Press Ctrl+Shift+Space to speak.")
        self.tts.speak("Voice agent ready. Press hotkey to speak.")

        with keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+<space>': on_activate
        }) as l:
            self.is_running = True
            l.join()

    def run_terminal_mode(self):
        """Run in interactive terminal mode with full command support"""
        self.tts.speak("Terminal mode activated. Type commands or 'quit' to exit.")
        print("\nMarketingkolabs Terminal Mode - Full System Access")
        print("Commands: voice text, 'browser search X', 'compare A and B', 'research product'")
        print("Type 'quit' to exit, 'context' to see state.\n")

        while True:
            try:
                text = input("You: ").strip()
                if text.lower() in ['quit', 'exit', 'q']:
                    break
                elif text.lower() == 'context':
                    print("Context:", self.context._state)
                    continue
                elif text:
                    self.process_text_command(text)
            except KeyboardInterrupt:
                break
            except EOFError:
                break

        self.tts.speak("Goodbye!")
        print("\nShutting down...")

    def run(self, mode: str = "terminal"):
        """Run the voice agent in specified mode"""
        self.is_running = True

        if mode == "wake_word":
            self.run_wake_word_mode()
        elif mode == "hotkey":
            self.run_hotkey_mode()
        elif mode == "terminal":
            self.run_terminal_mode()
        else:
            logger.error(f"Unknown mode: {mode}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Marketingkolabs - Local Voice Agent with Full System Access")
    parser.add_argument("--mode", choices=["terminal", "hotkey", "wake_word"],
                       default="terminal", help="Run mode")
    parser.add_argument("--init", action="store_true", help="Initialize and pre-load models")
    parser.add_argument("--config", default="config.yaml", help="Config file path")

    args = parser.parse_args()

    agent = Marketingkolabs(config_path=args.config)

    if args.init:
        print("Models loaded. Ready for voice commands.")
    else:
        agent.run(mode=args.mode)
