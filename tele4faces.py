import requests
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters

bot = Bot("YOUR_TELEGRAM_BOT_TOKEN")

SEARCH4FACES_API_KEY = "YOUR_SEARCH4FACES_API_KEY"

SEARCH4FACES_API_URL = "https://search4faces.com/api/json-rpc/v1"

def detect_faces(image_data):
    payload = {
        "jsonrpc": "2.0",
        "method": "detectFaces",
        "id": "some-id",
        "params": {"image": image_data}
    }
    headers = {
        "Content-Type": "application/json",
        "x-authorization-token": SEARCH4FACES_API_KEY
    }
    response = requests.post(SEARCH4FACES_API_URL, json=payload, headers=headers)
    return response.json()["result"]["faces"]

def search_similar_faces(image_id, face_data):
    payload = {
        "jsonrpc": "2.0",
        "method": "searchFace",
        "id": "some-id",
        "params": {
            "image": image_id,
            "face": face_data,
            "source": "vk_wall",  # You can change this based on your needs
            "results": 10  # Maximum number of profiles to return
        }
    }
    headers = {
        "Content-Type": "application/json",
        "x-authorization-token": SEARCH4FACES_API_KEY
    }
    response = requests.post(SEARCH4FACES_API_URL, json=payload, headers=headers)
    return response.json()["result"]["profiles"]

def handle_photo(update, context):
    photo = update.message.photo[-1]  # Get the last photo sent by the user
    photo_file = bot.get_file(photo.file_id)
    photo_url = photo_file.file_path
    photo_data = requests.get(photo_url).content

    faces = detect_faces(photo_data)

    for face in faces:
        similar_profiles = search_similar_faces(face["image"], face)

        for profile in similar_profiles:
            message = f"Profile: {profile['profile']}\n"
            message += f"Photo: {profile['photo']}\n"
            message += f"Name: {profile['first_name']} {profile['last_name']}\n"
            message += f"Age: {profile['age']}\n"
            message += f"City: {profile['city']}, {profile['country']}\n"
            update.message.reply_text(message)

def main():
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
