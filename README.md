# Using Twitch Chat to Automate Stream Highlights 
---

Twitch is a website where anyone can broadcast what they are doing to anyone else in the world that has access to the internet. Although Twitch allows streaming of any subject from programming to facepainting, it started out as a website for exclusively streaming video games, and this is still where most of its audience comes from. A big difference between watching gameplay on YouTube and a Twitch stream is that YouTube videos are edited and cut down, while Twitch is literally just a live stream, where no editing can take place. A streamer can broadcast for as long as they want sometimes up to eight hours or more. This results in a lot of unedited video that may or may not be worth watching all the way through. A busy person might wish to just skim through the video and watch only the highlights, however they would need to know beforehand where in the video these highlights occurred. To find these locations, I will utilize Twitch chat.

## Problem Statement
---

>Due to their unedited nature, Twitch streams can be exceptionally long and may not be 100% filled with entertainment. For someone that does not have a lot of time on their hands, they may not be able to watch their favorite streamers live and are not willing to look through hours of VOD content to find the most entertaining segments of the stream.

## Solution
---

The key distinction between watching a live twitch broadcast and a video on YouTube is the chat feature. As the streamer is playing the game, everyone that is tuned in to the stream can talk in the chat room to everyone else watching the broadcast. So instead of hiring and paying a video editor to make highlight reels for me, I am going to crowdsource my video editing to twitch chat. To do this I’m going to leverage a unique property of twitch chat. As the number of people in a twitch chat increase, say at around 2 thousand or so, the chat begins to resemble a crowd in a sports stadium; individual conversations are drowned out by the ambient noise, but group ideas are still collectively expressed, often in reaction to what is happening on the field. Say the home team makes a pivotal score; the crowd reacts by cheering. Or say the opposing team takes the field; the crowd reacts with booing. The same is true of twitch chat; the content of the chat is highly correlated to what is happening in the broadcast. In the context of twitch chat, "cheers" and "boos" look a lot like this: 

![](./assets/images/mps_one_game.png)

>This plot shows the general shape of the message-per-second data.

When looking at a time series plot of the message per second data, potential highlights take the form of spikes in the ambient noise. These spikes are  often triggered in reaction to something happening in the stream itself. This makes the data ideal for an anomaly detection analysis, where the highlights are the anomalies.




### Terminology:

- **Twitch** - Streaming platform where anyone can stream almost anything, barring illegal activity.

- **Twitch Chat** - The collected messages of everyone watching the stream. People may talk to each other or to the streamer and all the messages will be collected here. Generally civil in the smaller streams of less than 1,000 viewers but quickly becomes unruly past that.

- **VOD** - Video On Demand. After a streamer is finished streaming, they may choose to save a recording of their stream on Twitch's server for a time. Anyone can then go back and watch the VOD and read the chat as it occured when it was live streamed.

- **Socket** -  A python object that can continuously receive string data from a server, in this case the Twitch server. It generally has no trouble scraping from Twitch but will have issues if the chat is too busy.

- **OAuth Token** - A long sequence of random numbers and text that serves as a password to connect to the Twitch server using the socket. If you wish to run the scraping code on your own machine, you will need to generate your own OAuth token [here](https://twitchapps.com/tmi/).

- **AdmiralBulldog** - A popular Twitch streamer with an average concurrent viewership between 4,000 to 8,000. This makes his chat ideal for our purposes as it is busy enough to model with but not too busy that the socket will have trouble. The main stream game he plays on stream is *Dota 2*, a game in which a typical match lasts between 30 to 60 minutes. When I refer to "a single game," I am talking about one match of *Dota 2*.

- **Emote** - The primary way in which emotion is conveyed in twitch chat. They take the form of small pictures, sometimes of a face making an expression, sometimes of small phrases or popular memes.

- **"LUL, OMEGALUL, LULW, PepeLaugh"** - Some emotes that Twitch chat uses to convey laughter.

- **"Pog, PogU, PogChamp"** - Some emotes that Twitch chat uses to convey excitement.

- **Markov Chain** - A sequence of events where the probability of the next event occurring is determined entirely by the current event.

- **Latent Dirichlet Allocation** - A topic modeling technique that looks at which words appear next to each other frequently in an attempt to find the words that are associated with certain topics.

### Warning
---

A word of warning regarding Twitch chat: Twitch chat primarily patronized by anonymous people on the internet. While Twitch has banned offensive slurs of every variety, this does not prevent people from saying things that are incredibly unkind or incredibly stupid. If you decide to look through the raw logs in this repository or go onto twitch yourself, prepare to have your: 

- feelings hurt
- sensibilities offended
- braincells disintegrated

Abandon hope all ye who enter here.


## Directory Outline and Structure

```
.
├── assets/
├── code/
├── data/
├── presentation.pdf
└── report.md
```

- **assets/**

> Images to go with the presentation and technical report, as well as the completed highlight reels. (Note: the .mp4 files are too large for GitHub and currently do not exist in this remote repository. However, I assure you they exist on my personal computer and are *very* entertaining. Dropbox link TBA.)

- **code/**

> Scripts and Jupyter notebooks used to perform the scrape of Twitch chat and its subsequent analysis.

- **data/**

> The `.log` files containing the raw data scraped from Twitch and the formatted `.csv` files, organized into three subdirectories that are discussed in detail within their own subdirectory readme.

- **presentation.pdf**

> The slides that go with the presentation of this repository, aimed at a non- to semi-technical audience. Currently a work in progress.

- **report.md**

> Technical report that goes into further depth about my process of gathering, analyzing, and reporting. 