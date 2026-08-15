"""Text-to-speech system with caching and thread-safe playback."""
import hashlib
import asyncio
import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

logger = logging.getLogger(__name__)

# Optional edge-tts
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

LANGUAGE_VOICES = {
    "tr": "tr-TR-AhmetNeural",
    "ru": "ru-RU-SvetlanaNeural",
    "en": "en-US-JennyNeural",
}

AUDIO_CACHE_DIR = Path("audio_cache")


class TTSCache:
    """File-system based audio cache with hash-based filenames."""

    def __init__(self, cache_dir: Path = AUDIO_CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def _get_hash(self, text: str, lang: str, rate: int) -> str:
        key = f"{lang}:{rate}:{text.lower().strip()}"
        return hashlib.md5(key.encode("utf-8")).hexdigest()

    def get_cache_path(self, text: str, lang: str, rate: int = 0) -> Optional[Path]:
        h = self._get_hash(text, lang, rate)
        path = self.cache_dir / f"{h}.mp3"
        if path.exists() and path.stat().st_size > 1024:  # At least 1KB
            return path
        return None

    def save_to_cache(self, text: str, lang: str, rate: int, audio_data: bytes) -> Path:
        h = self._get_hash(text, lang, rate)
        path = self.cache_dir / f"{h}.mp3"
        temp_path = path.with_suffix(".tmp")
        with open(temp_path, "wb") as f:
            f.write(audio_data)
        temp_path.replace(path)
        return path

    def clear_cache(self):
        for f in self.cache_dir.glob("*.mp3"):
            try:
                f.unlink()
            except Exception:
                pass
        for f in self.cache_dir.glob("*.tmp"):
            try:
                f.unlink()
            except Exception:
                pass

    def get_cache_size(self) -> int:
        total = 0
        for f in self.cache_dir.glob("*.mp3"):
            total += f.stat().st_size
        return total


class TTSWorker(QThread):
    """Worker thread for TTS generation to keep GUI responsive."""

    finished_signal = pyqtSignal(bool, str, str)
    progress_signal = pyqtSignal(str)

    def __init__(self, text: str, lang: str, cache: TTSCache, rate: int = 0):
        super().__init__()
        self.text = text
        self.lang = lang
        self.cache = cache
        self.rate = rate
        self._is_running = True

    def run(self):
        if not self._is_running:
            return

        cached = self.cache.get_cache_path(self.text, self.lang, self.rate)
        if cached:
            self.finished_signal.emit(True, str(cached), self.text)
            return

        if not EDGE_TTS_AVAILABLE:
            self.finished_signal.emit(
                False,
                "TTS modülü yüklü değil. 'pip install edge-tts' komutunu çalıştırın.",
                self.text,
            )
            return

        self.progress_signal.emit("Ses hazırlanıyor...")

        try:
            voice = LANGUAGE_VOICES.get(self.lang, LANGUAGE_VOICES["en"])
            rate_str = f"{self.rate:+d}%"

            communicate = edge_tts.Communicate(self.text, voice, rate=rate_str)
            audio_data = bytearray()

            async def collect():
                async for chunk in communicate.stream():
                    if isinstance(chunk, dict) and "data" in chunk:
                        audio_data.extend(chunk["data"])

            # Use a new event loop to avoid conflicts with PyQt's event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(collect())
            finally:
                loop.close()

            if not self._is_running:
                return

            if len(audio_data) == 0:
                self.finished_signal.emit(
                    False,
                    "Ses dosyası oluşturulamadı (boş veri).",
                    self.text,
                )
                return

            path = self.cache.save_to_cache(self.text, self.lang, self.rate, bytes(audio_data))
            self.finished_signal.emit(True, str(path), self.text)

        except Exception as e:
            err_msg = str(e)
            if any(k in err_msg for k in ("getaddrinfo", "Connection", "Timeout", "NameResolutionError", "Network")):
                err_msg = "İnternet bağlantısı yok veya TTS servisi erişilemez."
            self.finished_signal.emit(False, err_msg, self.text)

    def stop(self):
        self._is_running = False
        self.wait(2000)


class TTSManager:
    """Manages text-to-speech: cache, generation, playback."""

    def __init__(self):
        self.cache = TTSCache()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.current_worker: Optional[TTSWorker] = None

    def speak(self, text: str, lang: str, rate: int = 0, on_start=None, on_finish=None, on_error=None):
        if not text or not text.strip():
            if on_error:
                on_error("Seslendirilecek metin boş.")
            return

        # Stop and disconnect previous worker safely
        if self.current_worker is not None:
            try:
                self.current_worker.finished_signal.disconnect()
            except Exception:
                pass
            self.current_worker.stop()
            self.current_worker = None

        # Check cache first (instant playback, no thread needed)
        cached = self.cache.get_cache_path(text, lang, rate)
        if cached:
            self._play_file(str(cached))
            if on_finish:
                on_finish()
            return

        if on_start:
            on_start()

        worker = TTSWorker(text, lang, self.cache, rate)
        self.current_worker = worker

        def handle_result(success: bool, result: str, spoken_text: str):
            # Only process if this is still the current worker
            if self.current_worker is not worker:
                return
            self.current_worker = None
            if success:
                self._play_file(result)
                if on_finish:
                    on_finish()
            else:
                if on_error:
                    on_error(result)
                else:
                    logger.warning(f"TTS Error: {result}")

        worker.finished_signal.connect(handle_result)
        worker.start()

    def _play_file(self, filepath: str):
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(filepath))
        self.player.play()

    def stop(self):
        self.player.stop()
        if self.current_worker is not None:
            try:
                self.current_worker.finished_signal.disconnect()
            except Exception:
                pass
            self.current_worker.stop()
            self.current_worker = None

    @staticmethod
    def get_source_lang(language_pair: str) -> str:
        return language_pair.split("-")[0] if "-" in language_pair else language_pair

    @staticmethod
    def get_target_lang(language_pair: str) -> str:
        parts = language_pair.split("-")
        return parts[1] if len(parts) > 1 else parts[0]
