###
#
# Filename: twitch_chat_format.py
# Author: Derek Steffan
# 
# This script will split up previously recorded chat messages from a .log
# file genereated by twitch_chat_scrape.py, returning the formatted
# chat messages as a pandas dataframe.
#
# This script was made with the help of this article:
# https://learndatasci.com/tutorials/how-stream-text-data-twitch-sockets-python/
#
###

import pandas as pd
import re
from datetime import datetime

# This method accepts a relative file path as an argument and returns a dataframe 
# of formatted text with username, message, and channel, with a datetime object
# as the index. 
def twitch_chat_format(path):

    # Open .log file specified by path
    with open(path, 'r', encoding='utf-8') as log:
        
        # Split every individual message.
        chat = log.read().split('\n')
        
        # Instantiate the dictionary; this will be converted into data frame later.
        # I find dictionaries faster and easier to work with than dataframes
        # specifically when building one from scratch.
        msg_dict = {"time": [], "username": [], "channel": [], "message": []}
        
        # Loop through all chat messages except the first and last, 
        # which which are messages about the logging start and end times.
        for msg in chat:

            # If 'msg' is an emtpy string, ignore it and continue
            if not msg:
                continue

            # Sometimes, the request will get "backed up" and log multiple
            # messages with the same time stamp. To ensure these messages
            # are not lost, they are all recorded as having the first 
            # timestampe from the "jam". 'time_logged' will not update
            # and it will be used as the timestamp for the next message in 
            # the list until another valid timestamp comes along.
            try:

                # Split on three semicolons, the predefined marker between 
                # the time gathered and the actual message content
                time_logged = datetime.strptime(msg.split(";;;")[0].strip(), 
                                                '%Y-%m-%d_%H:%M:%S')

            # Splitting sometimes returns an empty string; datetime will 
            # throw an error but this ensures execution will not end.
            except ValueError:
                # Because there are no leading semicolons, the message is 
                # not split and is just stripped instead.
                username_message = msg.strip()

            
            else:
                # Just in the offchance the chat message contained three semicolons
                # in a row, they are rejoined here and stripped of whitespace.
                username_message = ";;;".join(msg.split(";;;")[1:]).strip()

            # Using regex to isolate the user, channel, and chat message.
            # Format of the logs after the ";;;" is:
            # :username!username@username.tmi.twitch.tv PRIVMSG #channel :message
            # The regex grabs only the first mention of username and ignores 
            # the rest up until "PRIVMSG". Twitch only allows alphanumericvcharacters 
            # and underscores in their usernames so only these characters are 
            # referenced, while every character is pulled from the message iself.
            try:
                username, channel, message = re.search(r":([A-z\d_]+)!.+PRIVMSG #([A-z\d_]+) :(.+)", 
                                                        username_message).groups()
            
                # Append these values into the dictionary.
                msg_dict["username"].append(username)
                msg_dict["channel"].append(channel)
                msg_dict["message"].append(message)
                msg_dict["time"].append(time_logged)

            # Continue if no regex match is found; eg. one of the start or end 
            # logging messages or the intro messages when connecting to the IRC
            except AttributeError:
                continue



    # Convert dictionary to a dataframe and set datetime object to the index.
    return pd.DataFrame(msg_dict).set_index("time")