###
#
# Filename: highlighter.py
# Author: Derek Steffan
# 
# This file contains a couple different functions for 
# finding the highlights of a given time series of 
# message data for one Twitch broadcast, as well as a
# few other functions for finding the start and end 
# times of the clips that contain all the highlights,
# which are primarily useful for generating the final
# highlight reel with moviepy.
#
###

import pandas as pd
import numpy as np
import scipy.stats
from datetime import timedelta



# This function flags highlights for a given time series by
# calculating the z-score of rolling standard deviation.
# Standard deviation is chosen over rolling mean because 
# stdev cannot be less than zero, and all I care about here
# are the postive spikes in messages per second.
def highlight_by_stdev(df, threshold = 4, roll = 5):

    z_score = _scale_data(df, roll)

    # return (z_score >= threshold).astype(int)
    return (z_score >= threshold).astype(int)



# This function flags highlights for a given time series by
# calculating the probability of the next observed value
# using the Markov property. Because the "mps" is interpreted
# as a probability, it will be bounded between 0 and 1 with 
# anomalies having a very low probability (i.e. close to 0).

# Highlighting this way leads to many more clips being flagged,
# as such you may want to decrease the sensitvity even further
# or decrease the length of the start and end times when 
# calling the get_highlights_ funtions. 

# Also note that this may take a minute or two to run.
def highlight_by_probability(df, sensitivity = 0.05, roll = 5):

    z_score = _scale_data(df, roll)

    # Initial mean and stdev for the normal distribution
    # are based off the scaled data.
    mu = z_score.mean()
    sig = z_score.std()

    mc_prob = []

    # Iterate through every second and calculate how likely 
    # the current "mps" is, given the last value of "mps"
    # using a normal distribution.
    for score in z_score:
        mc_prob.append(scipy.stats.norm(mu, sig).pdf(score))
        mu = score
    
    mc_prob = pd.Series(mc_prob, index = df.index)

    return (mc_prob <= sensitivity).astype(int)



# This function takes a time series that has been labeled as 
# having distinct highlights and will return the start and
# end times for generating a clip around that highlight, by 
# defualt 15 seconds before and after, as a list of tuples.

# If two consecutive clips' ending and start times overlap,
# the two are "blobbed" together into one clip and the total 
# time is extended to match the second clip's end time.

# This function assumes a data frame passed in with an index
# from 0 to len(df) in order; see get_highlights_timestamp 
# for passing in a dataframe with datetime indices. Moviepy 
# has an easier time with integers, but timestamps are easier 
# for plotting with the rest of the time series data. Pass in 
# df.reset_index(drop = True) to quickly convert the index.
def get_highlights_index(df, before_time = 15, after_time = 15, target_col = "highlight"):
    
    # Find the indices designated as a highlight
    timestamps = df[df[target_col] == 1].index
    
    all_clips = []
    i = 0
    
    # Iterate over each highlighted index
    while i < len(timestamps):
        
        # Find the start and end times of the clip
        start = timestamps[i] - before_time
        end   = timestamps[i] + after_time

        try:
            
            # If the start of the next clip occurs before the 
            # end of the current clip, increase the length of 
            # the current clip to include the next end time
            # and ignore the next index.
            while timestamps[i + 1] - before_time <= end:

                # Update the end time
                end = timestamps[i + 1] + after_time

                # Cause the next clip to be skipped
                i += 1
        
        # try/except logic exists to ensure that the while 
        # loop does not go over the index of timestamps. 
        # This is only an issue for the last clip in timestamp.
        except IndexError:
            pass
        
        # Append the start and end times as a tuple
        all_clips.append((start, end))

        i += 1
        
    return all_clips



# This function is the same logic as before but supports pandas 
# dataframes with datetime indexes and returns timestamps instead.
def get_highlights_timestamp(df, before_time = 15, after_time = 15, target_col = "highlight"):
        
    timestamps = df[df[target_col] == 1].index
    
    all_clips = []
    i = 0
    
    while i < len(timestamps):
        
        start = timestamps[i] - timedelta(seconds = before_time)
        end   = timestamps[i] + timedelta(seconds = after_time)

        try:
            
            while timestamps[i + 1] - timedelta(seconds = before_time) <= end:

                end = timestamps[i + 1] + timedelta(seconds = after_time)

                i += 1
        
        except IndexError:
            pass
        
        all_clips.append((start, end))

        i += 1
        
    return all_clips



# Simple function to tell you some stats about your highlight reel.
# Will work for ranges generated by either of the above functions.
def clip_stats(all_clips):

    total = 0
    
    for highlight in all_clips:
        
        # Clips are in integer format
        if type(highlight[0]) == np.int64:
            total += highlight[1] - highlight[0]
            
        # Clips are in timestamp format
        else:
            total += (highlight[1] - highlight[0]).seconds

    # output = str(int(total / 60)) + ":"
    # if (total % 60) < 10
    #     output += "0"
    # output += str(total % 60)

    print(len(all_clips), "distinct clips")
    print(f"{int(total / 60)}:{total % 60} total minutes of video")



# Helper function to find the z_score of 
# the rolling standard deviation.
def _scale_data(df, roll = 5):
    stdev = df["mps"].rolling(roll).std()
    return stdev - stdev.mean() / stdev.std()