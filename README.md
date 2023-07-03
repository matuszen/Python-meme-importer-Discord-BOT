# Python-meme-importer-Discord-BOT

This script allows you to automate the collection of images and videos from selected webpages and send them to a Discord channel using the Discord application. It can be used to gather media content from various sources on the internet and share them with your friends or community on Discord.

## Prerequisites

Before running this script, make sure you have the following requirements fulfilled:

- Python 3.6 or higher installed on your system
- Required Python packages installed (discord.py, requests, bs4)

## Installation

1. Clone or download the repository to your local machine:

   ```shell
   git clone https://github.com/matuszen/Python-meme-importer-Discord-BOT.git
   ```

2. Install the required Python packages using pip:

   ```shell
   pip install -r requirements.txt
   ```

3. Set up Discord bot and obtain the bot token:

   - Create a new application and bot on the Discord Developer Portal.
   - Copy the bot token generated for your application.

4. Configure the script:
   Open config.py file and replace the placeholder values with your own settings:

   - TOKEN: Replace YOUR_DISCORD_BOT_TOKEN with your Discord bot token obtained in the previous step.
   - CHANNEL_ID: Replace 0 with the ID of the Discord channel where you want to send the media. You can enable developer mode in Discord settings and then right-click on the channel to obtain its ID.
   - WEBPAGES: List the URLs of the webpages from where you want to collect media. This is static object.

5. Run the script

The script will start collecting media from the specified webpages and send them to the configured Discord channel.

## Usage

- Script can be used on server, once runing, automaticly do ordered tasks.
- If any new media is found, it will be downloaded and send to discord channel right away.
- When script finish work, automaticly saves date and hour, becouse when you run this another time, only upload media, which are posted since last script running.
- If you delete data/last_time_upload.pkl file, script will import media only from current day, since midnight.

## Important Note

Please use this script responsibly and respect the terms of service and copyright of the websites you are scraping media from. Make sure you have the necessary permissions or rights to collect and distribute the media content.

## Contributing

Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please create an issue or submit a pull request.

## License

This project is licensed under the MIT License. Feel free to modify and distribute the code as per the terms of the license.

## Acknowledgements

This script utilizes the following open-source libraries:

- discord.py - Python wrapper for the Discord API
- requests - HTTP library for Python
- bs4 - Web scraping library for Python
