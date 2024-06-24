import requests
import json
import hashlib
import time
import os
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

url_pre = "https://ap-east-1.tensorart.cloud"
app_id = "BEkuZGhk8"

def generate_signature(method, url, body, app_id):
    method_str = method.upper()
    url_str = url
    timestamp = str(int(time.time()))
    nonce_str = hashlib.md5(timestamp.encode()).hexdigest()
    body_str = body
    to_sign = f"{method_str}\n{url_str}\n{timestamp}\n{nonce_str}\n{body_str}"
    private_key_content = os.getenv("TENSORART_PRIVATE")
    private_key = serialization.load_pem_private_key(
        private_key_content.encode(),
        password=None,
        backend=default_backend()
    )
    signature = private_key.sign(
        to_sign.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    signature_base64 = base64.b64encode(signature).decode()
    auth_header = f"TAMS-SHA256-RSA app_id={app_id},nonce_str={nonce_str},timestamp={timestamp},signature={signature_base64}"
    return auth_header

def generate_auth_header(method, url, body, app_id):
    return generate_signature(method, url, body, app_id)

def create_job(data):
    body = json.dumps(data)
    auth_header = generate_auth_header("POST", "/v1/jobs", body, app_id)
    response = requests.post(url_pre + "/v1/jobs", json=data, headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': auth_header
    })
    return json.loads(response.text)

def get_job_result(job_id):
    while True:
        time.sleep(1)
        response = requests.get(url_pre + f"/v1/jobs/{job_id}", headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': generate_auth_header("GET", f"/v1/jobs/{job_id}", "", app_id)
        })
        get_job_response_data = json.loads(response.text)
        if 'job' in get_job_response_data:
            job_dict = get_job_response_data['job']
            job_status = job_dict.get('status')
            if job_status == 'SUCCESS':
                return job_dict['successInfo']['images'][0]['url']
            elif job_status == 'FAILED':
                raise Exception("Image generation failed.")

def generate_tensorart_image(prompt):
    txt2img_data = {
        "request_id": hashlib.md5(str(int(time.time())).encode()).hexdigest(),
        "stages": [
            {
                "type": "INPUT_INITIALIZE",
                "inputInitialize": {
                    "seed": -1,
                    "count": 1
                }
            },
            {
                "type": "DIFFUSION",
                "diffusion": {
                    "width": 512,
                    "height": 512,
                    "prompts": [
                        {
                            "text": prompt
                        }
                    ],
                    "negativeprompts": [
                        {
                            "text": "Amputee, Autograph, Bad anatomy, Bad illustration, Bad proportions, Beyond the borders, Blank background, Blurry, Body out of frame, Boring background, Branding, Cropped, Cut off, Cloned face, Deformed, Disfigured, Dismembered, Disproportioned, Distorted, Dehydrated, Draft, Duplicate, Duplicated features, Error, Extra arms, Extra fingers, Extra hands, Extra legs, Extra limbs, Fault, Flaw, Fused fingers, Grains, Grainy, Gross proportions, Hazy, Identifying mark, Improper scale, Incorrect physiology, Incorrect ratio, Indistinct, Kitsch, Jpeg artifacts, Logo, Long neck, Low quality, Low resolution, Lowres, Macabre, Malformed, Malformed limbs, Mark, Misshapen, Missing arms, Missing fingers, Missing hands, Missing legs, Mistake, Morbid, Mutilated, Mutated hands, Mutation, Mutilated, Off-screen, Out of frame, Outside the picture, Pixelated, Poorly drawn face, Poorly drawn feet, Poorly drawn hands, Printed words, Render, Repellent, Replicate, Reproduce, Revolting dimensions, Script, Shortened, Sign, Signature, Split image, Squint, Storyboard, Text, Tiling, Trimmed, Too many fingers, Ugly, Unfocused, Unattractive, Unnatural pose, Unreal engine, Unsightly, Watermark, Written language, Worst quality"
                        }
                    ],
                    "sampler": "DPM++ 2M Karras",
                    "sdVae": "Automatic",
                    "steps": 24,
                    "sd_model": "669456595647770642",
                    "clip_skip": 2,
                    "cfg_scale": 7
                }
            }
        ]
    }

    response_data = create_job(txt2img_data)
    if 'job' in response_data:
        job_dict = response_data['job']
        job_id = job_dict.get('id')
        image_url = get_job_result(job_id)
        return image_url
    else:
        raise Exception("Failed to create image generation job.")