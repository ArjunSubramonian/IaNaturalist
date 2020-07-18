import os
from io import BytesIO
from flask import Flask, request, render_template
from PIL import Image, ImageDraw
import base64
import copy

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorException
from msrest.authentication import CognitiveServicesCredentials

# Go get the values from .env file
from dotenv import load_dotenv
load_dotenv()

# Load the values from environmental variables
# The magic of dotenv
COGSVCS_KEY = os.getenv('COGSVCS_KEY')
COGSVCS_CLIENTURL = os.getenv('COGSVCS_CLIENTURL')

# Create the core Flask app
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # User is requesting the form
        return render_template('form.html')
    elif request.method == 'POST':
        # User has sent us data
        image1 = request.files['image']
        # image2 = copy.deepcopy(image1)
        image2 = image1
        client = ComputerVisionClient(COGSVCS_CLIENTURL, CognitiveServicesCredentials(COGSVCS_KEY))
        try:
            result = client.describe_image_in_stream(image1)
            message = result.captions[0].text
        except ComputerVisionErrorException as e:
            message = str(e.response.text):

        try:
            result = client.detect_objects_in_stream(image2)
            message = str(result)
        except ComputerVisionErrorException as e:
            message += str(e.response.text)

        img = Image.open(image2)
        dctx = ImageDraw.Draw(img)  # create drawing context
        for detection in result.objects:
            w, h = detection.rectangle.w, detection.rectangle.h
            bbox = [(detection.rectangle.x, detection.rectangle.y), (w + detection.rectangle.x, h + detection.rectangle.y)]
            dctx.rectangle(bbox, outline="blue")
        del dctx  # destroy drawing context
        
        output = BytesIO()
        img.save(output, 'jpeg', quality=100)
        output.seek(0)
        img = base64.b64encode(output.getvalue())

        return render_template('result.html', message=message, img=img.decode('ascii'))

