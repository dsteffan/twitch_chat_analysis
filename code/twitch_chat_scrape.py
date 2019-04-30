###
#
# Filename: twitch_chat_format.py
# Author: Derek Steffan
# 
# This script will monitor and record all the twitch chat messages for a 
# given channel and time interval or number of messages.
#
# To run this code, you will need to generate a Twitch IRC oauth token at:
# https://twitchapps.com/tmi/ 
#
# This script was made with the help of this article:
# https://learndatasci.com/tutorials/how-stream-text-data-twitch-sockets-python/
#
###

import socket as sock
import logging
import time
from emoji import demojize



def twitch_chat_scrape(nickname, token, channel, minutes, path = "./chat.log", n_messages = None):

    # Description of arguments:

    # nickname
    # This is the nickname that your request will use. It is 
    # reccommended that you use the same name as your twitch account.
    
    # token
    # This is the authorization token required to stream messages 
    # from the Twitch IRC server. 
    
    # channel
    # This is the Twitch channel from which the chat will be logged

    # minutes
    # Number of minutes for which to log chat messages. Further
    # funtionality described below. 

    # path
    # The relative path to where the .log file will be saved. Note that
    # if running in a Jupyter notebook, the filepath will not change 
    # unless you restart the kernel.

    # n_messages
    # If left as None, then the method will log chat for the specified
    # amount of time as is the default. However, if 'n_messages' is passed
    # as an int, then the method will collect chat messages equal to n
    # instead of running for a certain amount of time. The 'minutes' 
    # argument will then become the interval at which checkpoints are recorded.



    # This URL will refer the socket to the Twitch chat server, where
    # we will make requests using the python 'socket' object.
    server = "irc.chat.twitch.tv"
    port = 6667

    # Connecting to the server and sending our authentication 
    # credentials over the socket.
    socket = sock.socket()
    socket.connect((server, port))

    # The strings need to be encoded with 'utf-8' so that
    # they can be sent over the socket.
    socket.send(f"PASS {token}\n".encode("utf-8"))
    socket.send(f"NICK {nickname}\n".encode("utf-8"))
    socket.send(f"JOIN #{channel}\n".encode("utf-8"))

    # Configuring the logging object that will be used to continuously
    # write chat messages to a .log file.
    # Format of the log messages is current time, followed by three
    # semicolons, followed by the raw message itself.
    # 'filemode = "w"' will overwrite the .log file if the filepath 
    # matches an existing .log file.
    logging.basicConfig(level = logging.DEBUG,
                        format = '%(asctime)s ;;; %(message)s',
                        datefmt = '%Y-%m-%d_%H:%M:%S',
                        filename = path,
                        filemode = "w")
                        #handlers = logging.FileHandler('../data/chat.log', encoding='utf-8'))

    # "Start logging" message
    logging.info(f"START OF RECORDED CHAT MESSAGES FROM CHANNEL: {channel.upper()}\n")



    #### socket.recv(2048).decode('utf-8') ####
    # The first time .recv is called, the Twitch server will return a 
    # welcome message and a "connecting to channel" message. These will 
    # be filtered out by the regex if using the twitch_chat_format script. 
    # Additionally, the Twitch server may return more than one chat message 
    # per call, resulting in multiple messages with the same timestamp. 
    # This too will be handled by the formatting script. 



    # Instantiate start time and number of checkpoints, which are used by both loops
    then = time.time()
    elapsed = 0
    n_check = 1

    # Actual scrape is conducted inside a try/except statement so that 
    # execution can be interrupted by the user prematurely.
    try:

        # If n_messages is None, then the if statement will evaluate to False 
        # and the 'while' loop will run. If n_messages is an int, then the 'for'
        # loop will run instead.
        if n_messages:

            for i in range(n_messages):

                # Making one call to the server, returning one chat message.
                response = socket.recv(2048).decode('utf-8')

                # Responding to the Twitch IRC server's ping so that
                # they do not shut down the connection prematurely.
                if response.startswith('PING'):
                    socket.send("PONG\n".encode('utf-8'))

                # If the response is not null, remove emojis and write to .log file.
                # Demojize will turn an emoji back into plain text, i.e. :thumbs_up:
                elif len(response) > 0:
                    logging.info(demojize(response))
                
                # Update total time elapsed
                elapsed = time.time() - then

                # Print out a checkpoint at an interval specified by 'minutes' argument.
                # Unlike the while loop, this can potentially print out many checkpoints
                # if the interval is too small or if the chat is too slow.
                if (elapsed) / 60 > (minutes * n_check):
                    print("-" * 40)
                    print(f"Checkpoint number {n_check}")
                    print(f"{i + 1} messages collected after {round((elapsed) / 60, 2)} minutes.")
                    n_check += 1

                

        else:

            # Instantiate logging variable for the while loop
            n_messages = 0
            
            # Python time objects log seconds, but time argument is in minutes
            while elapsed < (minutes * 60):

                # Making one call to the server, returning one chat message.
                response = socket.recv(2048).decode('utf-8')

                # Responding to the Twitch IRC server's ping so that
                # they do not shut down the connection prematurely.
                if response.startswith('PING'):
                    socket.send("PONG\n".encode('utf-8'))
                
                # If the response is not null, remove emojis and write to .log file.
                # Demojize will turn an emoji back into plain text, i.e. :thumbs_up:
                elif len(response) > 0:
                    logging.info(demojize(response))


                # Print checkpoint if time elapsed is (roughly) equal to a
                # ten percent interval of the total time.
                checkpoint = ((minutes * 60) / 10) * n_check
                if elapsed > checkpoint:
                    print("-" * 40)
                    print(f"Checkpoint number {n_check} at {round(elapsed / 60, 2)} minutes.")
                    print(f"{n_messages} messages logged!")
                    n_check += 1

                # Update total messages logged and time elapsed for the 
                # next iteration of the loop.
                n_messages += 1
                elapsed = time.time() - then



    # If the user ends the loop prematurely, print out time and message data.
    # Known bug: If the for loop is interrupted, it will print out the number 
    # of messages that it was supposed to log, not how many it actually logged.
    except KeyboardInterrupt:

        # Print total messages
        print("-" * 40)
        print(f"Scrape interrupted by user after {round(elapsed / 60, 2)} minutes.")
        print(f"{n_messages} messages logged!")
        print("-" * 40)

        # "End logging" message
        logging.info(f"RECORDING INTERRUPTED BY USER\n")

    # If the loop runs to completion, print out time and message data.
    else:

        # Print total messages
        print("-" * 40)
        print(f"Scrape complete after {round(elapsed / 60, 2)} minutes.")
        print(f"{n_messages} messages logged!")
        print("-" * 40)

        # "End logging" message
        logging.info(f"END OF RECORDED CHAT MESSAGES FROM CHANNEL: {channel.upper()}\n")

    # Close the socket and end the connection to the Twitch server.
    socket.close()