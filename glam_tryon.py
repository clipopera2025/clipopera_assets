import requests

# Your Squarespace image URLs
MEDIA_URL = (
    "https://images.squarespace-cdn.com/content/67e4029aea1fb67dfe0dbfda/"
    "1f3b81df-616d-4a89-b7c3-43bf3e285fe2/model.png?content-type=image%2Fpng"
)
GARMENT_URL = (
    "https://images.squarespace-cdn.com/content/67e4029aea1fb67dfe0dbfda/"
    "90e8be9d-10f8-40f6-b1a8-1a4740513447/shirt.png?content-type=image%2Fpng"
)

# Your Glam AI API key
GLAM_API_KEY = 'BkhUMHs-bSJRtW9VSROlsw'

# Request headers
headers = {
    'Content-Type': 'application/json',
    'X-API-Key': GLAM_API_KEY,
}

# Request payload
json_data = {
    'mask_type': 'overall',
    'media_url': MEDIA_URL,
    'garment_url': GARMENT_URL,
}

# Send the try-on request
response = requests.post('https://api.glam.ai/api/v1/tryon', headers=headers, json=json_data)

# Handle response
if response.ok:
    result = response.json()
    print('✅ Try-On Success!')
    print('🖼️ Result URL:', result.get('result_url'))
else:
    print('❌ Try-On Failed:', response.status_code)
    print(response.text)
