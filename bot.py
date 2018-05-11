# -*- coding: UTF8 -*-
import datetime
import requests
from datetime import datetime
import sqlite3
import git
import os

repo = git.cmd.Git(".")

class BotHandler:
    def __init__(self, token):
            self.token = token
            self.api_url = "https://api.telegram.org/bot{}/".format(token)


    def get_updates(self, offset=0, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_first_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[0]
        else:
            last_update = None

        return last_update


token = '586420533:AAEXkkXGBIJb-YjiWXJe9p1WSwVpDAtRACw'
wisdom_bot = BotHandler(token) #Your bot's name

def main():
    #Establish database connection.
    connection = sqlite3.connect('userIds.db')
    database = connection.cursor()

    # Add users from database to users_known list.
    known_users = []
    for row in database.execute("SELECT User_id FROM Users"):
        known_users.append(row[0])
    new_offset = 0

    while True:
        
        all_updates=wisdom_bot.get_updates(new_offset)
        time = str(datetime.now())[11:19]
        if '09:00:00' < time:
            # Sending to the group 'geeks'
            # Setup multiple group handling, through database - pending.
            repo.pull()
            files = os.listdir('.')
            count = ""
            count_file = open("current_tip.txt", "r+")
            for element in count_file:
                count = count + element

            current_tip = "tip" + str(count)
            if current_tip in files:
                message = ""
                current_file = open(current_tip)
                for char in current_file:
                    message = message + char
                wisdom_bot.send_message(-266323148, message)
                count_file.seek(0, 0)
                count_file.write(str(int(count) + 1))
                current_file.close()
                count_file.close()
                repo.add(u=True)
                repo.commit('-m "Update current_tip"')
                repo.push()
            
        if len(all_updates) > 0:
            for current_update in all_updates:
                first_update_id = current_update['update_id']
                if 'text' not in current_update['message']:
                    first_chat_text='New member'
                else:
                    first_chat_text = current_update['message']['text']
                first_chat_id = current_update['message']['chat']['id']
                if 'first_name' in current_update['message']:
                    first_chat_name = current_update['message']['chat']['first_name']
                elif 'new_chat_member' in current_update['message']:
                    first_chat_name = current_update['message']['new_chat_member']['username']
                elif 'from' in current_update['message']:
                    first_chat_name = current_update['message']['from']['first_name']
                else:
                    first_chat_name = "unknown"

                # Check if user is recognised.
                if(first_chat_id in known_users):
                    if first_chat_text == 'Hi':
                        wisdom_bot.send_message(first_chat_id, 'Hello ' + first_chat_name)
                        new_offset = first_update_id + 1
                    
                    # Add a new contact to be recognised by the bot.
                    elif 'contact' in current_update['message']:
                        first_name = current_update['message']['contact']['first_name']
                        if 'user_id' not in current_update['message']['contact']:
                            wisdom_bot.send_message(first_chat_id, "Sorry, {} doesn't have a telegram agccount.".format(first_name))
                            new_offset = first_update_id + 1
                            break
                        new_user_id = (current_update['message']['contact']['user_id'])
                        if new_user_id in known_users:
                            wisdom_bot.send_message(first_chat_id, 'I already know {}'.format(first_name))
                            new_offset = first_update_id + 1
                        else:
                            known_users.append(new_user_id)
                            database.execute("INSERT INTO Users (User_id, NAME) VALUES ({}, '{}')".format(new_user_id, first_name))
                            connection.commit()
                            wisdom_bot.send_message(first_chat_id, first_name + ' can now message me!')
                            new_offset = first_update_id + 1
                            repo.add(u=True)
                            repo.commit('-m "Add new user"')
                            repo.push()
                            
                    else:
                        wisdom_bot.send_message(first_chat_id,"""
                            Here are the things you can do:

Share a contact with me: They can start texting me!!
(please use your mobile app to share a contact)

Thats all I can do.
I am still learning. Stay tuned!!
                        """)
                        new_offset = first_update_id + 1
                else:
                    wisdom_bot.send_message(first_chat_id, "Sorry, I don't know who you are.")
                    new_offset = first_update_id + 1

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()