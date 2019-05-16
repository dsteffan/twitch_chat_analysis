# Data Directory README
---

The `.log` files containing the raw data scraped from Twitch and the formatted `.csv` files, organized into three subdirectories that are discussed in detail here.

```
.
├── formatted/
├── highlighted/
└── logs/
```

- **logs/**

> As the raw messages are scraped from Twitch in real time, they are written to a `.log` file in this directory that contains the message along with a timestamp that is sensitive down to the second.


- **formatted/**

> After the logs have been parsed and formatted into a pandas dataframe, they are saved here as a `.csv` to be used throughout the notebooks.


- **highlighted/**

> After the logs have been parsed and formatted into a pandas dataframe, they are saved here to be used throughout the notebooks.