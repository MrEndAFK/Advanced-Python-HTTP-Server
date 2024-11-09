# Advanced-Python-HTTP-Server

# Python HTTP File Server with Basic Authentication and File Upload

This is a multithreaded Python HTTP server that serves files from a specified directory, supports basic authentication, and includes an upload feature. It allows users to upload files via a web form, with the uploads stored in a designated subdirectory (`uploads`). The server also enforces a maximum upload folder size of 10 GB.

## Features

- **Multithreaded Server:** Handles requests in separate threads for better performance.
- **Basic Authentication:** Optional username and password protection.
- **File Upload:** Users can upload files directly through the browser.
- **Directory Listing:** Serves the current directory with an option to upload files.
- **Upload Size Limit:** Limits the `uploads` folder size to 10 GB.
- **Customizable Port:** Allows users to specify the server port.

## Prerequisites

- Python 3.x

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MrEndAFK/Advanced-Python-HTTP-Server
   cd Advanced-Python-HTTP-Server

## Usage

### Starting the Server

**Run the server script:**
        ```bash
        python server.py

**Select the directory to serve:**

The default is the current directory, but you can specify another path if desired.
**Enter the port number (default is 8080):**

You can choose a different port if needed.
**Enable basic authentication (optional):**

Enter y for yes if you want to set a username and password, or press enter for no authentication.
**Auto-open the server in the browser (optional):**

Enter y to automatically open the server URL in your default web browser.

# File Upload Page:
You can add "/upload" on path.

http://localhost:8080/upload