import torch
from PIL import Image
import re
import cv2
import numpy as np

class OCR:
    # Constantes
    CONFIANZA_MINIMA_CARACTER = 0.5

    def __init__(self, device=None):
        # Dispositivo para inferencia
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        # Cargar el modelo
        self.parseq = torch.hub.load('baudm/parseq', 'parseq', pretrained=True, trust_repo=True).eval()
        self.parseq = self.parseq.to(self.device)
        # Transform del modelo
        from strhub.data.module import SceneTextDataModule
        self.img_transform = SceneTextDataModule.get_transform(self.parseq.hparams.img_size)

    def ocr_parseq(self, img: Image.Image):
        """
        Entrada:
        - img: Imagen en formato PIL.Image.Image
        
        Salida:
        - Texto reconocido en la imagen
        - Confianza de cada caracter (desde el primer caracter hasta EOS)
        """
        img = self.img_transform(img).unsqueeze(0).to(self.device)

        with torch.no_grad():
            logits = self.parseq(img)
            prediccion = logits.softmax(-1)
            label, confidence = self.parseq.tokenizer.decode(prediccion)

        return label[0], confidence[0]
    
    def solo_numeros(self, text: str) -> str:
        """Devuelve los dígitos de la cadena de entrada"""
        numeros = re.sub(r"[^0-9]", "", text or "")
        return numeros
    
    def preprocesar_imagen(self, img, scale=4) -> np.ndarray:
        """Devuelve la imagen `img` preprocesada para mejorar la precisión del OCR."""
        # Por si acaso no hay nada que procesar
        h, w = img.shape[:2]
        if h == 0 or w == 0:
            return None
        
        # Se escala la imagen para mejorar la precisión del OCR
        img_resized = cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

        # Se convierte a escala de grises
        img_gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

        # Se aplica CLAHE para mejorar el contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        img_clahe = clahe.apply(img_gray)

        # Se aplica un filtro de suavizado para reducir el ruido
        img_blur = cv2.GaussianBlur(img_clahe, (3, 3), 0)

        return img_blur
    
    def obtener_numero_dorsal(self, img, preprocesar=False) -> str | None:
        """Dada una imagen, devuelve el número de dorsal reconocido"""
        # Preprocesar la imagen
        if not preprocesar:
            img_preprocesada = img
        else:
            img_preprocesada = self.preprocesar_imagen(img)
            img_preprocesada = cv2.cvtColor(img_preprocesada, cv2.COLOR_GRAY2RGB)

        if img_preprocesada is None:
            return None
        
        # Convertir la imagen a PIL.Image.Image para usarla con PARSeq
        img_pil = Image.fromarray(img_preprocesada)

        # Obtener la detección de PARSeq
        texto, conf = self.ocr_parseq(img_pil)

        # Sólo confiar si la confianza es suficientemente alta en todos los caracteres y hay 1 o 2 números solo
        if len(texto) == 0: # Sólo se detecta EOS
            return None
        elif len(texto) == 1:
            if conf[0] < self.CONFIANZA_MINIMA_CARACTER:
                return None
        elif len(texto) == 2:
            if conf[0] < self.CONFIANZA_MINIMA_CARACTER or conf[1] < self.CONFIANZA_MINIMA_CARACTER:
                return None
        else:
            return None # Más de 2 caracteres detectados, no es válido para un dorsal
        
        # Si ha detectado "O" o "o", que a veces se confunde con 0, lo cambio por 0
        texto = texto.replace("O", "0")
        texto = texto.replace("o", "0")
        
        # Si sólo se han detectado números, devolverlos
        len_numeros = sum(c.isdigit() for c in texto)
        if len_numeros == len(texto):
            digitos = self.solo_numeros(texto)
        else:
            return None # Si se han detectado caracteres no numéricos, no es válido para un dorsal
    
        return digitos

    def obtener_texto_completo(self, img) -> str | None:
        """Dada una imagen, devuelve el texto completo reconocido (no sólo números) y pone la confianza con 2 decimales en el texto, por ejemplo: "2(0.97)1(0.45)" """
        # Preprocesar la imagen
        img_preprocesada = self.preprocesar_imagen(img)
        if img_preprocesada is None:
            return None
        
        # Convertir la imagen a PIL.Image.Image para usarla con PARSeq
        img_rgb = cv2.cvtColor(img_preprocesada, cv2.COLOR_GRAY2RGB)
        img_pil = Image.fromarray(img_rgb)

        # Obtener la detección de PARSeq
        texto, conf = self.ocr_parseq(img_pil)
        
        # Formatear el texto con las confianzas
        texto_formateado = ""
        for i, (char, confianza) in enumerate(zip(texto, conf)):
            texto_formateado += f"{char}({confianza:.2f})"
        
        return texto_formateado

    @classmethod
    def obtener_bbox(cls, x1, x2, y1, y2, img, scale=1):
        """
        Entradas:
        - x1, x2, y1, y2: Coordenadas del bounding box
        - img: Imagen
        - scale: Factor de escala para ampliar el bounding box (por ejemplo, 1.2 para ampliarlo un 20%)

        Salida:
        - El recorte de la imagen del bounding box ampliado
        """

        h, w = img.shape[:2]

        # Calcular el centro del bounding box
        centro_x = (x1 + x2) / 2
        centro_y = (y1 + y2) / 2

        # Calcular el ancho y alto del bounding box original
        ancho = x2 - x1
        alto = y2 - y1

        # Calcular el ancho y alto del bounding box ampliado
        ancho_nuevo = ancho * scale
        alto_nuevo = alto * scale

        # Calcular las coordenadas del bounding box ampliado
        x1_nuevo = int(max(centro_x - ancho_nuevo / 2, 0))
        y1_nuevo = int(max(centro_y - alto_nuevo / 2, 0))
        x2_nuevo = int(min(centro_x + ancho_nuevo / 2, w))
        y2_nuevo = int(min(centro_y + alto_nuevo / 2, h))
        
        # Devolver el recorte de la imagen del bounding box ampliado
        return img[y1_nuevo:y2_nuevo, x1_nuevo:x2_nuevo]