"""
Marketingkolabs Autonomous Agent - 24/7 Local AI Agent
Runs continuously, learns from interactions, and proactively assists
"""
import sys
import time
import threading
import signal
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.stt import STTEngine
from core.intent_parser import IntentParser
from core.tts import TTSEngine
from core.skill_router import SkillRouter
from core.config_validator import load_and_validate_config
from core.context import SessionContext
from core.safety import SafetyManager
from core.memory import AgentMemory
from core.proactive import ProactiveAgent
from core.p2p_sync import P2PSync
from core.tray_app import TrayApp
from autostart import AutostartManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MarketingkolabsAgent:
    """
    Main autonomous agent - runs 24/7 locally
    Self-contained, no external dependencies
    """

    def __init__(self, config_path: str = "config.yaml", service_mode: bool = False):
        logger.info("=" * 60)
        logger.info("Marketingkolabs Autonomous Agent Starting...")
        logger.info("24/7 Local AI Agent - No Cloud Dependencies")
        logger.info("=" * 60)

        self.service_mode = service_mode
        self.is_running = False
        self.is_voice_mode_active = False

        # Load configuration
        self.config = load_and_validate_config(config_path)

        # Initialize all components
        self.stt = STTEngine(self.config)
        self.intent_parser = IntentParser(self.config)
        self.tts = TTSEngine(self.config)
        self.router = SkillRouter(self.config)
        self.context = SessionContext(self.config.dict())
        self.safety = SafetyManager(self.config.dict(), None, None)
        self.memory = AgentMemory("agent_memory.db")
        self.proactive = ProactiveAgent(self.router, self.memory, self.context, self.config.dict())
        self.p2p = P2PSync()
        self.tray = TrayApp(self, self.config.dict())

        # Set references
        self.safety.set_engines(self.tts, self.stt)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("All components initialized successfully")

    def start(self):
        """Start the autonomous agent"""
        self.is_running = True

        # Welcome message
        if not self.service_mode:
            self.tts.speak("Marketingkolabs autonomous agent is now online and ready to assist you 24/7")

        # Start proactive agent
        self.proactive.start()
        logger.info("Proactive agent started")

        # Start P2P sync
        try:
            self.p2p.start()
            logger.info("P2P sync started")
        except Exception as e:
            logger.warning(f"P2P sync failed to start: {e}")

        # Start system tray
        if not self.service_mode:
            tray_thread = threading.Thread(target=self.tray.run, daemon=True)
            tray_thread.start()
            logger.info("System tray started")

        logger.info("=" * 60)
        logger.info("Agent is now running 24/7 - Fully autonomous")
        logger.info("Voice commands: Active")
        logger.info("Proactive monitoring: Active")
        logger.info("Memory system: Active")
        logger.info("=" * 60)

        # Main loop
        try:
            while self.is_running:
                # Check for pending suggestions
                suggestions = self.proactive.get_pending_suggestions()
                if suggestions and not self.service_mode:
                    for suggestion in suggestions[:1]:  # One at a time
                        self._handle_suggestion(suggestion)

                # Periodic memory cleanup
                self.memory.clear_old_data(days=30)

                # Sleep to prevent CPU spinning
                time.sleep(5)

        except KeyboardInterrupt:
            self.shutdown()

    def _handle_suggestion(self, suggestion: dict):
        """Handle proactive suggestion"""
        message = suggestion.get('message', '')
        action = suggestion.get('action')

        logger.info(f"Proactive suggestion: {message}")

        if action:
            # Auto-execute safe actions
            if action.get('skill') in ['clipboard', 'browser']:
                logger.info(f"Auto-executing: {action}")
                result = self.router.route(action)
                self.memory.store_conversation(
                    "proactive_suggestion",
                    action,
                    result,
                    self.context._state
                )

    def process_voice_command(self, audio_duration: float = 4.0) -> dict:
        """Process voice command with full context and learning"""
        start_time = time.time()

        try:
            self.tts.speak("Listening...", blocking=False)
            text = self.stt.record_and_transcribe(duration=audio_duration)

            if not text or len(text.strip()) < 2:
                return {'success': False, 'message': 'No speech detected'}

            logger.info(f"Voice command: '{text}'")

            # Record in memory
            self.memory.learn_pattern('voice_command', {'text': text})

            # Parse and execute
            result = self._process_command(text)

            # Store conversation
            self.memory.store_conversation(
                text,
                result.get('action', {}),
                result,
                self.context._state
            )

            return result

        except Exception as e:
            logger.error(f"Voice command error: {e}")
            return {'success': False, 'message': str(e)}

    def _process_command(self, text: str) -> dict:
        """Process any command (voice or text)"""
        # Resolve context
        context_params = self.context.resolve_reference(text)

        # Parse intent
        action = self.intent_parser.parse(text)

        if context_params and 'params' in action:
            action['params'].update(context_params)

        # Update context
        self.context.add_command(text, action)

        # Safety check
        if self.safety.requires_confirmation(action.get('skill'), action.get('action')):
            confirmed = self.safety.request_confirmation(
                f"{action.get('action')} in {action.get('skill')}"
            )
            if not confirmed:
                return {'success': False, 'message': 'Cancelled by user'}

        # Execute
        result = self.router.route(action)

        # Update context from result
        if result.get('success'):
            self._update_context(action, result)

        # TTS feedback
        elapsed = (time.time() - time.time()) * 1000
        if result.get('success'):
            self.tts.speak(result.get('message', 'Done'))
        else:
            self.tts.speak(f"Failed: {result.get('message', 'Unknown error')}")

        return result

    def _update_context(self, action: dict, result: dict):
        """Update session context"""
        skill = action.get('skill')
        params = action.get('params', {})

        if skill == 'file_ops' and 'path' in params:
            self.context.update('last_file', params['path'])
        elif skill == 'app_control' and 'app_name' in params:
            self.context.update('last_app', params['app_name'])
        elif skill == 'browser' and 'url' in result.get('data', {}):
            self.context.update('last_url', result['data']['url'])
        elif skill == 'browser' and 'product' in params:
            self.context.update('last_product', params['product'])

    def toggle_voice_mode(self):
        """Toggle voice mode"""
        self.is_voice_mode_active = not self.is_voice_mode_active
        state = "activated" if self.is_voice_mode_active else "deactivated"
        self.tts.speak(f"Voice mode {state}")
        logger.info(f"Voice mode {state}")
        return self.is_voice_mode_active

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down Marketingkolabs Agent...")
        self.is_running = False

        self.proactive.stop()
        self.p2p.stop()

        self.tts.speak("Marketingkolabs agent shutting down. Goodbye!")
        time.sleep(1)

        logger.info("Agent shutdown complete")
        sys.exit(0)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}")
        self.shutdown()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Marketingkolabs Autonomous Agent")
    parser.add_argument("--mode", choices=["interactive", "service"], default="interactive",
                       help="Run mode: interactive (with UI) or service (background)")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--enable-autostart", action="store_true", help="Enable autostart on boot")
    parser.add_argument("--disable-autostart", action="store_true", help="Disable autostart")

    args = parser.parse_args()

    # Handle autostart
    if args.enable_autostart:
        manager = AutostartManager()
        if manager.enable():
            print("Autostart enabled successfully")
        else:
            print("Failed to enable autostart")
        sys.exit(0)

    if args.disable_autostart:
        manager = AutostartManager()
        if manager.disable():
            print("Autostart disabled successfully")
        else:
            print("Failed to disable autostart")
        sys.exit(0)

    # Start agent
    agent = MarketingkolabsAgent(config_path=args.config, service_mode=(args.mode == "service"))
    agent.start()
