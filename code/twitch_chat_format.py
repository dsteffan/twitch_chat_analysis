###
#
# Filename: twitch_chat_format.py
# Author: Derek Steffan
# 
# This script contains a couple methods to help with formatting Twitch 
# chat messages logged by twitch_chat_scrape.py. 
#
# The first function will split up previously recorded chat messages 
# from a .log file genereated by twitch_chat_scrape.py, returning the 
# formatted chat messages as a pandas dataframe.
#
# The second function will take a dataframe generated by twitch_chat_format
# and return a series with the number of messages for every second.
#
# The twitch_chat_format function was made with the help of this article:
# https://learndatasci.com/tutorials/how-stream-text-data-twitch-sockets-python/
#
###

import pandas as pd
import re
from datetime import datetime

# This function accepts a relative file path as an argument and returns a dataframe 
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



# This function takes in a dataframe with a datetime index 
# and returns a series with every second and the number 
# of chat messages recorded in that second.
def messages_per_second(df):

    mes_per_sec = []

    # Create a range for each second in the recorded broadcast.
    # This is done instead of using df.index because every second
    # does not necessarily have an associated observation.
    date_range = pd.date_range(
        
        # Start and end the range within the observations;
        # because time does not flow backwards, .min and .max
        # will point to the first and last observations.
        start = df.index.min(),                     
        end = df.index.max(),
        freq = "S",   # Increment the range by second
        closed = "right" # Discard the first second of observations
    ) 

    # Find the total amount of minutes of video, rounded.
    total = round((date_range.max() - date_range.min()).seconds / 60)

    print(f"Processing {total} minutes of chat messages...")

    for sec in date_range:
        
        try:
            # Double brackets around .loc forces it to return a dataframe.            
            # Append the length of the dataframe, i.e. number of messages.
            mes_per_sec.append(df.loc[[str(sec)]].shape[0])
        
        # If the key is not found, then there are no messages for that second
        except KeyError:
            mes_per_sec.append(0)

        # Print out a checkpoint for every ten minutes of messages
        delta = sec - date_range.min()
        if delta.seconds % 600 == 0 and delta.seconds != 0:
            print(f"{delta.components.hours * 60 + delta.components.minutes}",
                  f"out of {total} minutes of messages processed.")

    print(f"{total} out of {total} minutes of messages processed.")
    print("...All messages processed.")

    return pd.Series(data = mes_per_sec, index = date_range)



# Function to remove all messages sent by the automated 
# chat bot, as well as all commands sent to it
def filter_bot_messages(df, bot_name):
    
    # Removing messages sent by the chat bot.
    df = df[df["username"] != bot_name]
    
    # Commands issued to the chat bot begin with "!"
    df = df[[not message.startswith("!") for message in df["message"]]]
    
    return df