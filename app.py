import os
from io import BytesIO
from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# Go get the values from .env file
from dotenv import load_dotenv
load_dotenv()

# Load the values from environmental variables
# The magic of dotenv
COGSVCS_KEY = os.getenv('COGSVCS_KEY')
COGSVCS_CLIENTURL = os.getenv('COGSVCS_CLIENTURL')

img = Image.new("RGB", (100, 100), "#f9f9f9")  # create new Image

# Create the core Flask app
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # User is requesting the form
        return render_template('form.html')
    elif request.method == 'POST':
        # User has sent us data
        image = request.files['image']
        client = ComputerVisionClient(COGSVCS_CLIENTURL, CognitiveServicesCredentials(COGSVCS_KEY))
        result = client.describe_image_in_stream(image)
        message = result.captions[0].text

        result = client.detect_objects_in_stream(image)
        img = Image.open(BytesIO(image))
        dctx = ImageDraw.Draw(img)  # create drawing context
        for detection in result:
            w, h = detection.rectangle.w, detection.rectangle.h
            bbox = [(detection.rectangle.x, detection.rectangle.y), (w - detection.rectangle.x, h - detection.rectangle.y)]
            dctx.rectangle(bbox, fill="#ddddff", outline="blue")
            del dctx  # destroy drawing context
            
        return render_template('result.html', message=message)

@app.route('/fetch_image', methods=['GET'])
def fetch_image():
    output = BytesIO()
    img.convert('RGBA').save(output, format='PNG')
    output.seek(0, 0)

    return send_file(output, mimetype='image/png', as_attachment=False)

