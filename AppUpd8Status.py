import telebot
import subprocess
import logging
import os
from datetime import datetime

# Bot setup
token = "token"
chat_id = "chat_id"
authorized_user_id = "user_id"
bot = telebot.TeleBot(token) 

# Send message
def send_message(message):
    bot.send_message(chat_id, message)

# Check autorization
def is_authorized_user(user_id):
    return user_id == authorized_user_id

# Update docker image
def update_image():
    try:
        # Change dir to location where docker-comose is located
        os.chdir("appDir/")

        # Pull latest image
        subprocess.run(["docker-compose", "pull"])

        # Get container ID
        container_id = subprocess.check_output(["docker-compose", "ps", "-q", "--filter", "service=web"]).decode("utf-8").strip()

        if container_id:
            # Get current version ID
            current_version = subprocess.check_output(["docker", "inspect", "--format='{{.Image}}'", container_id]).decode("utf-8").strip()

            try:
                # Get latest version ID
                subprocess.run(["docker-compose", "pull"])
                latest_version = subprocess.check_output(["docker", "inspect", "--format='{{.Image}}'", container_id]).decode("utf-8").strip()
            except Exception as e:
                # Pull exception
                logging.error("Image pull error: {}".format(e))
                return

            # Update ONLY if images are different
            if current_version != latest_version:
                # Get latest version
                subprocess.run(["docker-compose", "pull"])

                # Stop and remove old container
                subprocess.run(["docker-compose", "down"])

                # Start new container
                subprocess.run(["docker-compose", "up", "-d"])

                # Get dangling images
                command = ["docker", "images", "--filter", "dangling=true", "-q", "--no-trunc"]
                image_ids = subprocess.check_output(command).decode("utf-8").strip().split("\n")

                # Remove old images
                for image_id in image_ids:
                    command = ["docker", "rmi", image_id]
                    subprocess.run(command)
                    
                # Send success message
                message = "Image got successfully updated and started with version {} .".format(latest_version)
                if is_authorized_user(authorized_user_id):
                   send_message(message)
                logging.info("Image update to version {} successful.".format(latest_version))
                return
            else:
                # Send message about lack of updates
                message = "No image updates available."
                if is_authorized_user(authorized_user_id):
                   send_message(message)
                logging.info("No image updates available.")
                exit()

    except Exception as e:
        # Update error message
        message = "Image update failed: {}".format(e)
        if is_authorized_user(authorized_user_id):
           send_message(message)
        logging.error("Image update failed: {}".format(e))
        exit()

# Start update
update_image()

# Start bot
bot.polling()
