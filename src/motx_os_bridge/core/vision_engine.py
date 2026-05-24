"""
Vision Engine - OCR, capture écran et reconnaissance UI.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
import json
import re


@dataclass
class ScreenRegion:
    """Représente une région de l'écran."""
    x: int
    y: int
    width: int
    height: int
    label: str


@dataclass
class UIElement:
    """Représente un élément UI détecté."""
    element_type: str  # button, text, input, etc.
    text: str
    position: Tuple[int, int]
    size: Tuple[int, int]
    confidence: float


class VisionEngine:
    """Moteur de vision pour OCR, capture d'écran et reconnaissance UI."""
    
    def __init__(self):
        self.screenshots: List[Path] = []
        self.ocr_cache: Dict[str, str] = {}
        self.ui_elements_cache: List[UIElement] = []
        
        # Vérification des dépendances
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie si les dépendances nécessaires sont disponibles."""
        self.has_pil = self._try_import('PIL')
        self.has_pytesseract = self._try_import('pytesseract')
        self.has_pyautogui = self._try_import('pyautogui')
        self.has_cv2 = self._try_import('cv2')
        
        if not self.has_pil:
            print("⚠️ PIL/Pillow non installé - Capture d'écran limitée")
        if not self.has_pytesseract:
            print("⚠️ pytesseract non installé - OCR non disponible")
        if not self.has_pyautogui:
            print("⚠️ pyautogui non installé - Contrôle souris/clavier limité")
    
    def _try_import(self, module_name: str) -> bool:
        """Tente d'importer un module."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    async def capture_screen(self, region: Optional[ScreenRegion] = None, save_path: Optional[str] = None) -> Path:
        """Capture une capture d'écran."""
        if not self.has_pil:
            raise Exception("PIL/Pillow non disponible pour la capture d'écran")
        
        try:
            from PIL import ImageGrab
            
            if region:
                bbox = (region.x, region.y, region.x + region.width, region.y + region.height)
                screenshot = ImageGrab.grab(bbox=bbox)
            else:
                screenshot = ImageGrab.grab()
            
            if save_path:
                path = Path(save_path)
            else:
                path = Path("logs") / f"screenshot_{len(self.screenshots)}.png"
                path.parent.mkdir(parents=True, exist_ok=True)
            
            screenshot.save(path)
            self.screenshots.append(path)
            
            return path
            
        except Exception as e:
            raise Exception(f"Erreur de capture d'écran: {str(e)}")
    
    async def ocr_image(self, image_path: str, lang: str = "eng") -> str:
        """Extrait le texte d'une image via OCR."""
        if not self.has_pytesseract:
            raise Exception("pytesseract non installé - OCR non disponible")
        
        try:
            import pytesseract
            from PIL import Image
            
            # Vérifier le cache
            cache_key = f"{image_path}_{lang}"
            if cache_key in self.ocr_cache:
                return self.ocr_cache[cache_key]
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=lang)
            
            self.ocr_cache[cache_key] = text
            return text
            
        except Exception as e:
            raise Exception(f"Erreur OCR: {str(e)}")
    
    async def ocr_screen(self, region: Optional[ScreenRegion] = None, lang: str = "eng") -> str:
        """Effectue l'OCR directement sur l'écran."""
        screenshot_path = await self.capture_screen(region)
        return await self.ocr_image(str(screenshot_path), lang)
    
    async def detect_ui_elements(self, image_path: Optional[str] = None) -> List[UIElement]:
        """Détecte les éléments UI dans une image ou sur l'écran."""
        if not self.has_cv2:
            # Fallback: OCR basique
            return await self._detect_ui_elements_ocr(image_path)
        
        try:
            import cv2
            import numpy as np
            
            if image_path:
                image = cv2.imread(image_path)
            else:
                from PIL import ImageGrab
                screenshot = ImageGrab.grab()
                image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Détection basique de contours
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            elements = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 20 and h > 10:  # Filtre les petits éléments
                    element_type = self._classify_element(w, h)
                    elements.append(UIElement(
                        element_type=element_type,
                        text="",
                        position=(x, y),
                        size=(w, h),
                        confidence=0.7
                    ))
            
            self.ui_elements_cache = elements
            return elements
            
        except Exception as e:
            # Fallback en cas d'erreur
            return await self._detect_ui_elements_ocr(image_path)
    
    async def _detect_ui_elements_ocr(self, image_path: Optional[str] = None) -> List[UIElement]:
        """Détection UI basée sur OCR (fallback)."""
        if not self.has_pytesseract:
            return []
        
        try:
            import pytesseract
            from PIL import Image
            
            if image_path:
                image = Image.open(image_path)
            else:
                from PIL import ImageGrab
                image = ImageGrab.grab()
            
            # Utiliser les données de bounding box de Tesseract
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            elements = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    elements.append(UIElement(
                        element_type='text',
                        text=data['text'][i],
                        position=(data['left'][i], data['top'][i]),
                        size=(data['width'][i], data['height'][i]),
                        confidence=data['conf'][i] / 100.0
                    ))
            
            return elements
            
        except Exception as e:
            raise Exception(f"Erreur détection UI: {str(e)}")
    
    def _classify_element(self, width: int, height: int) -> str:
        """Classifie un élément UI selon ses dimensions."""
        ratio = width / height if height > 0 else 1
        
        if ratio > 3:
            return "button"
        elif ratio < 0.3:
            return "icon"
        elif height > 100:
            return "container"
        else:
            return "text"
    
    async def find_text_on_screen(self, text: str, region: Optional[ScreenRegion] = None) -> Optional[Tuple[int, int]]:
        """Trouve la position d'un texte sur l'écran."""
        ocr_text = await self.ocr_screen(region)
        
        # Recherche basique (améliorable avec des coordonnées précises)
        if text.lower() in ocr_text.lower():
            # Retourne le centre de la région ou (0, 0) par défaut
            if region:
                return (region.x + region.width // 2, region.y + region.height // 2)
            return (0, 0)
        
        return None
    
    async def click_at_position(self, x: int, y: int):
        """Clique à une position spécifique."""
        if not self.has_pyautogui:
            raise Exception("pyautogui non installé")
        
        try:
            import pyautogui
            pyautogui.click(x, y)
        except Exception as e:
            raise Exception(f"Erreur clic: {str(e)}")
    
    async def click_on_text(self, text: str):
        """Clique sur un texte trouvé sur l'écran."""
        position = await self.find_text_on_screen(text)
        if position:
            await self.click_at_position(*position)
        else:
            raise Exception(f"Texte '{text}' non trouvé")
    
    async def extract_text_regions(self, image_path: str) -> Dict[str, Tuple[int, int, int, int]]:
        """Extrait les régions de texte d'une image."""
        if not self.has_pytesseract:
            raise Exception("pytesseract non installé")
        
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(image_path)
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            regions = {}
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    text = data['text'][i]
                    regions[text] = (data['left'][i], data['top'][i], 
                                   data['width'][i], data['height'][i])
            
            return regions
            
        except Exception as e:
            raise Exception(f"Erreur extraction régions: {str(e)}")
    
    def get_screenshots(self) -> List[Path]:
        """Retourne la liste des captures d'écran."""
        return self.screenshots
    
    def clear_cache(self):
        """Efface les caches OCR et UI."""
        self.ocr_cache.clear()
        self.ui_elements_cache.clear()
