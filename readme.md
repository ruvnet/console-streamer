# Live Console YouTube Streamer

This is a Python script that streams the output of a console to a live stream on YouTube. It uses the Google YouTube API to create a new live broadcast and stream the console output to the live event.

## Prerequisites

To use this script, you'll need:

- A Google Cloud Platform project with the YouTube API enabled
- A Google account with access to the YouTube API
- A `client_secret.json` file with your Google API credentials
- Python 3.x installed on your local machine

## Installation

1. Clone this repository to your local machine.
2. Create a virtual environment and activate it.
3. Install the required Python packages: `pip install -r requirements.txt`
4. Configure your `client_secret.json` file with your Google API credentials.
5. Set up Replit Secrets to store your Google API credentials (optional, if using Replit).
6. Run the script: `python main.py`

## Usage

When you run the script, it will create a new live broadcast on YouTube and start streaming the console output to the live event. You can view the live stream on YouTube by navigating to the live event URL.

## License

This project is licensed under the MIT License - see the LICENSE file for details.