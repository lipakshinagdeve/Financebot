"""
OCR service for receipt processing.
"""

import pytesseract
from PIL import Image
import openai
import json
from datetime import datetime
from config.settings import OPENAI_API_KEY, EXPENSE_CATEGORIES

openai.api_key = OPENAI_API_KEY

class OCRService:
    """Receipt OCR processing"""
    
    def extract_text(self, image: Image.Image) -> str:
        """Extract text from image using Tesseract"""
        try:
            if image.mode != 'RGB':
                image = image.convert('RGB')
            return pytesseract.image_to_string(image)
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")
    
    def parse_receipt(self, text: str) -> dict:
        """Parse receipt text using AI"""
        try:
            prompt = f"""Extract expense data from this receipt text.
Return ONLY valid JSON with these keys:
- amount: number only (no currency symbols)
- date: YYYY-MM-DD format (if not found, use today's date)
- category: one of {EXPENSE_CATEGORIES}
- description: brief description

Receipt text:
{text}

Return only JSON, no other text."""
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a receipt parser. Return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            result = result.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(result)
            
            # Validate and return
            return {
                'amount': float(data.get('amount', 0)),
                'date': datetime.strptime(
                    data.get('date', datetime.now().strftime('%Y-%m-%d')), 
                    '%Y-%m-%d'
                ),
                'category': data.get('category', 'Others'),
                'description': data.get('description', 'Receipt expense')
            }
        except Exception as e:
            raise Exception(f"AI parsing failed: {str(e)}")
    
    def process_receipt(self, image: Image.Image):
        """Complete receipt processing"""
        try:
            text = self.extract_text(image)
            if not text.strip():
                return False, None, "No text found in image"
            
            data = self.parse_receipt(text)
            return True, data, None
        except Exception as e:
            return False, None, str(e)

# Global instance
ocr_service = OCRService()