# Generate image using dall.e api
import requests  
import os  

from openai_client import OpenAIClient # openai connector class

# Initialize OpenAI Client
openai_client_obj = OpenAIClient()
client = openai_client_obj.get_client()

# setting up images sub-folder in the current path
images_folder = "images"
images_dir = os.path.join(os.curdir,images_folder)

if not os.path.isdir(images_dir):
    os.mkdir(images_dir)

# generating the images

image_prompt = "A cyberpunk motorcyclist dreaming of a funky bikes with neon lights riding fast on nightly lighted streets, digital art"

# convert these to radio options on frontend
image_dimension = "1024x1024" #supported sizes are 256x256, 512x512, or 1024x1024
quality="hd" # support quality is hd or standard
style="vivid" #supported styles is vivid or natural

model_response = client.images.generate(
    model="dall-e-3",
    size = image_dimension,
    prompt=image_prompt,
    n=1,
    response_format="url",
    quality=quality,
    style=style
)

# image is generated, now saving the image

generated_image_name = "generated_image.png"
generated_image_filepath = os.path.join(images_dir,generated_image_name)
generated_image_url = model_response.data[0].url
generated_image = requests.get(generated_image_url).content

with open(generated_image_filepath,"wb") as image_file:
    image_file.write(generated_image)

# print the image
print(generated_image_filepath)
