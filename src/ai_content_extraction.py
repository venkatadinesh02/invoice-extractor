import openai
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Set API key securely via environment variable or directly here
openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key")

def clean_json_output(result):
        # Remove triple backticks and optional "json" hint
        return re.sub(r"^```(?:json)?|```$", "", result.strip(), flags=re.IGNORECASE).strip()

def extract_invoice_data_with_gpt(ocr_text: str):
    prompt = f"""
You are an intelligent document parser.

Based on the following OCR-extracted invoice text, dynamically infer and extract all relevant key-value fields.

Return a JSON object with only the fields that are clearly present in the text. Avoid including fields not found.

If there is a table of line items, include it under a "line_items" key as a list of items with inferred columns.

Respond ONLY with JSON output. No explanation or text.

OCR Text:
\"\"\"{ocr_text}\"\"\"
"""

    try:
        # Use new client-based syntax
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful invoice parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        result = response.choices[0].message.content
        result = clean_json_output(result)
        return json.loads(result)

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON", "raw_output": result}
    except Exception as e:
        return {"error": str(e)}
