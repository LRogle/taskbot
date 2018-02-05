#!/usr/bin/env python

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import subprocess
import telegram
import shlex
import os
import ParsingFunctions


# -------------------------BOT_COMMAND----------------------------
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(
        'Hi {},\nthis is TaskWarriorBot,\ntype /help for more information'.format(update.message.from_user.first_name))
    try:
        os.mkdir('{}{}'.format(os.getenv('PATH_TASK_BOT'), update.message.from_user.id))
    except:
        pass


def help(bot, update):
    """Send a message when the command /help is issued."""
    text = ('some basic operation:\n'
            '<b>view</b> - show task created\n'
            '<b>phone</b> - customized configuration of "view"\n'
            '<b>add task_description</b> - add task to the list\n'
            '<b>del task_id</b> - delete selected task\n'
            '<b>see task_id</b> - show all task information\n'
            '<b>NOTE:</b> if you are using this Bot in a group you must type as first word /cmd')
    send_msg_html(bot, update, text)


def cmd(bot, update):
    """Call the TaskBot in a chatgroup when the command /cmd is issued and executes the command identified by the following arguments."""
    processes_message(bot, update)


def custom_keyboard(bot, update):
    buttonrow1 = telegram.KeyboardButton('phone')
    buttonrow2 = [telegram.KeyboardButton('deleted'), telegram.KeyboardButton('recurring')]
    buttonrow3 = [telegram.KeyboardButton('waiting'), telegram.KeyboardButton('completed')]
    keyboard = [[buttonrow1], buttonrow2, buttonrow3]
    kb = telegram.ReplyKeyboardMarkup(keyboard)
    kb.resize_keyboard
    bot.sendMessage(chat_id=update.message.chat_id, text="You enabled the custom keyboard", reply_markup=kb)


def remove_keyboard(bot, update):
    remove_kb = telegram.ReplyKeyboardRemove()
    bot.sendMessage(chat_id=update.message.chat_id, text="You removed the custom keyboard", reply_markup=remove_kb)


# ----------------------------------------------------------------

# Eneable logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO,
                    filename='logfile.log')


def send_long_HTML(bot, update, message_list):
    """Allows Bot to send a long message composed by more messages."""
    for flowing_message in message_list:
        send_msg_html(bot, update, flowing_message)


def show_task_completed(bot, update):
    """Show in a message all completed tasks and their related details."""
    all_task_list = ParsingFunctions.parsin_json()
    task_list = all_task_list[1]
    message_list = ParsingFunctions.select_output(task_list)
    send_long_HTML(bot, update, message_list)


def show_task_deleted(bot, update):
    """Show in a message all deleted tasks and their related details."""
    all_task_list = ParsingFunctions.parsin_json()
    task_list = all_task_list[2]
    message_list = ParsingFunctions.select_output(task_list)
    send_long_HTML(bot, update, message_list)


def show_task_recurring(bot, update):
    """Show in a message all recurring tasks and their related details."""
    all_task_list = ParsingFunctions.parsin_json()
    task_list = all_task_list[3]
    message_list = ParsingFunctions.select_output(task_list)
    send_long_HTML(bot, update, message_list)


def show_task_waiting(bot, update):
    """Show in a message all waiting tasks and their related details."""
    all_task_list = ParsingFunctions.parsin_json()
    task_list = all_task_list[4]
    message_list = ParsingFunctions.select_output(task_list)
    send_long_HTML(bot, update, message_list)


def show_task_info(task):
    """Create the output for send all informations of the task identified. return string"""
    message_out = ParsingFunctions.select_output(task)[0]
    return message_out


def create_command_handler(bot, update, filtered_command_list):
    """takes the message_filtered and creates the command that must be eventually execute"""
    logger.info('{} User: {}'.format(filtered_command_list, update))
    new_filtered_command = []
    for scan in filtered_command_list:
        if scan != 'execute' and scan != 'config':
            new_filtered_command.append(scan)
    try:
        if filtered_command_list[1] == "see":
            send_msg_html(bot, update, show_task_info(ParsingFunctions.find_task(new_filtered_command[0])))
    except:
        pass
    if len(filtered_command_list) == 0:
        send_msg_html(bot, update, 'Error! no command found')
    if new_filtered_command[0].lower() == "view":
        new_filtered_command = ['task']
        run_command(bot, update, new_filtered_command)
    elif new_filtered_command[0].lower() == "see":
        try:
            send_msg_html(bot, update, show_task_info(ParsingFunctions.find_task(new_filtered_command[1])))
        except IndexError:
            send_msg_html(bot, update, '"see" function must have id_task as argument')
    elif new_filtered_command[0].lower() == "completed":
        show_task_completed(bot, update)
    elif new_filtered_command[0].lower() == "deleted":
        show_task_deleted(bot, update)
    elif new_filtered_command[0].lower() == "recurring":
        show_task_recurring(bot, update)
    elif new_filtered_command[0].lower() == "waiting":
        show_task_waiting(bot, update)
    else:
        new_filtered_command.insert(0, 'task')
        new_filtered_command[1] = new_filtered_command[1].lower()
        run_command(bot, update, new_filtered_command)


def filter_user_command(original_command, update):
    """Removes from the string some operators and eventual args for control the command line. return string"""
    args = shlex.split(original_command)
    if update.message.chat.type == 'group':
        args.pop(0)
    filtered_command = [shlex.quote(scan) for scan in args]
    return filtered_command


def processes_message(bot, update):
    """Reads the message and filters it. passes the message filtered to the command handler."""
    redirected_task(update)
    message_input = update.message.text
    filtered_message = filter_user_command(message_input, update)
    create_command_handler(bot, update, filtered_message)


def redirected_task(update):
    """Changes the working directory of each user or group to separate the tasks for each user or group."""
    args = ("task config data.location '{}{}'".format(os.getenv('PATH_TASK_BOT'), update.message.chat.id))
    subprocess.run(args=args, shell=True)


def run_command(bot, update, command_list):
    """Executes the command in the shell and send the output as a message."""
    cmd = ' '.join(command_list)
    result = subprocess.run(args=cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
    print(result.returncode)
    send_msg_markdown(bot, update, result.stdout)


def send_msg_markdown(bot, update, text):
    """Takes text as argument and send a message to the user in Markdown format."""
    bot.send_message(chat_id=update.message.chat.id,
                     text='```\n{}\n```'.format(text),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def send_msg_html(bot, update, text):
    """Takes text as argument and send a message to the user in HTML format."""
    bot.send_message(chat_id=update.message.chat.id,
                     text=text,
                     parse_mode=telegram.ParseMode.HTML)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""

    # Create the EventHandler and pass it your bot's token.
    token = os.getenv('TASK_TELEGRAM_BOT_TOKEN')
    port = os.getenv('PORT')
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("cmd", cmd))
    dp.add_handler(CommandHandler("custom_keyboard", custom_keyboard))
    dp.add_handler(CommandHandler("remove_keyboard", remove_keyboard))

    # on message correctly received start our code for process the message
    dp.add_handler(MessageHandler(Filters.text, processes_message))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



    # add handlers
    updater.start_webhook(listen="0.0.0.0",
                        port=port,
                        url_path=token)
    updater.bot.set_webhook("https://<appname>.herokuapp.com/" + token)
    updater.idle()

if __name__ == '__main__':
    main()
