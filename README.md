# OCR-from-scratch
Implementation of OCR from scratch using Python and TensorFlow

# 1. Running the Server

## 1.1 Setting up the environment

### Install [Node.js](https://nodejs.org/en/).

The application is developed on version 10 LTS. Other versions may continue to support but are untested.

#### Install the required Node packages:

    npm install formidable socketio gm
    
#### Install the GraphicsMagick DLL for the `gm` Node package.

[Windows Download](https://sourceforge.net/projects/graphicsmagick/files/graphicsmagick-binaries/1.3.31/GraphicsMagick-1.3.31-Q8-win64-dll.exe/download)

### Install Python

Python 3.6.X is required. As of yet, TensorFlow works with Python 3.6.X.

[Python Downloads](https://www.python.org/downloads)

#### Install respective Python packages

    python -m pip install tensorflow opencv image numpy

## 1.2 Running the Server

Clone the Git repository, enter the directory and run the server

    git clone https://github.com/usamamuneeb/OCR-from-scratch.git
    cd OCR-from-scratch
    node server.js

# 2. Accessing the frontend

The frontend can be accessed at port 8000 of the machine running the server application.

If using on local system, open a browser and point to:

    http://localhost:8000
