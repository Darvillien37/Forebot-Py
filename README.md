![Python package](https://github.com/Darvillien37/Forebot-Py/workflows/Python%20package/badge.svg)
# Forebot-Py
Forebot but now in Python!!

## Usage
Checkout this repo, and create a '.env' file in the root.
Ensure that the .env has the following variables:
1. DISCORD_TOKEN=<YOUR TOKEN HERE>
2. PREFIX=<BOTS PREFIX HERE>
3. RESOURCE_FOLDER=<THE LOCATION TO THE RESOURCE FOLDER>
4. DATA_FOLDER=<THE LOCATION TO THE DATA FOLDER>

## Resource Folder
The resource folder should have a structure like so:
```
.
├── foreman
|   ├── Images_here.png/.jpg (images)
|   └── Vids.mjpg (videos)
└── chaz
    ├── Images_here.png/.jpg (images)
    └── Vids.mjpg (videos)
```

## Data folder
The path MUST exist, but the files will be created if not.