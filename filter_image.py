from PIL import Image
from io import BytesIO
import numpy as np
import torch
from torchvision import models, transforms

# Load the pre-trained MobileNet V2 model
model = models.mobilenet_v2(pretrained=True)
model.eval()

# 预preprocessor function
preprocess = transforms.Compose([
    transforms.Resize(224),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def is_valid_image(response):
    try:
        img = Image.open(BytesIO(response.content))
        img.verify()  # Verify that the image is complete

        img = Image.open(BytesIO(response.content))
        if img.format not in ['JPEG', 'PNG']:
            return False
        if img.size[0] < 100 or img.size[1] < 100:  # Example size check
            return False
        return True
    except Exception:
        return False

def filter_violent_images(response):
    try:
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')
        img = preprocess(img)
        img = img.unsqueeze(0)  # Adding the batch dimension

        with torch.no_grad():
            outputs = model(img)
        _, predicted_class = outputs.max(1)
        predicted_class = predicted_class.item()

        # Determine whether a violent image is a violent image based on the categories output by the model
        # Here the violent image category is assumed to be a specific class, which needs to be adapted to the specific model
        # The 1000 categories of MobileNet V2 can be found in the ImageNet category index.
        # These are sample class indexes and need to be adapted to the actual situation
        violent_classes = [413, 414, 416, 762]  # Firearms, knives and other categories
        if predicted_class in violent_classes:
            return False  # It's a violent image.
        return True  # Nonviolent images
    except Exception as e:
        print(f"Error in processing image: {e}")
        return False