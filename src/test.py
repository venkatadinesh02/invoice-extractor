import os
from google.cloud import vision_v1
from google.cloud.vision_v1 import types

# Set credentials path
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'C:/Users/venke/PycharmProjects/invoice-extractor/invoice-extractor-463809-bc85bf31cdf3.json'

def extract_text(file_path):
    client = vision_v1.ImageAnnotatorClient()

    if file_path.endswith('.pdf'):
        # For PDF files (multi-page supported)
        with open(file_path, 'rb') as f:
            pdf_content = f.read()

        mime_type = 'application/pdf'
        input_config = types.InputConfig(content=pdf_content, mime_type=mime_type)

        request = types.AnnotateFileRequest(
            input_config=input_config,
            features=[types.Feature(type_=vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION)]
        )

        response = client.batch_annotate_files(requests=[request])
        full_text = ''

        for resp in response.responses:
            for page_response in resp.responses:
                full_text += page_response.full_text_annotation.text

    else:
        # For image files (JPG, PNG, JPEG, etc.)
        with open(file_path, 'rb') as image_file:
            content = image_file.read()

        image = types.Image(content=content)
        response = client.document_text_detection(image=image)

        full_text = response.full_text_annotation.text

    return full_text
