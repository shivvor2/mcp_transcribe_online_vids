# MCP Transcribe Online Videos

A FastMCP server that allows LLMs to access and transcribe online videos from YouTube and Bilibili using [Replicate](https://replicate.com/) and [0x0.st](https://0x0.st) for temporary file hosting.

## Features

- Transcribe YouTube/ Bilibili videos with timestamped output
- Automatic audio extraction and format conversion
- Cloud-based transcription via WhisperX models
- Temporary file hosting for large files

## Installation

### Prerequisites

- Python 3.12+
- Conda (recommended for environment management)

### Setting Up the Environment

```bash
# Create and activate a conda environment
conda create --name mcp_transcribe_online_vids python=3.12
conda activate mcp_transcribe_online_vids

# Install required system packages
conda install conda-forge::uv conda-forge::ffmpeg conda-forge::sqlite

# Install Python dependencies
uv pip install -r requirements.txt
```

### Configuration

1. Copy the `.env.template` file to `.env`:
   ```bash
   cp .env.template .env
   ```

2. Edit the `.env` file with your credentials:
   - `REPLICATE_API_TOKEN`: Get from [Replicate's API key page](https://replicate.com/account/api-tokens)
   - `ZERO_X_URL`: URL for the 0x0.st instance (default: public instance)
   - `TEMP_FILE_PATH`: Directory for temporary files
   - `LOCAL_FILE_SIZE_LIMIT`: Maximum file size in MB for direct API uploads

## Usage

### Starting the Server

```bash
python main.py
```

### Available Tools

- `get_youtube_transcript(url)`: Transcribe a YouTube video
- `get_bilibili_transcript(url)`: Transcribe a Bilibili video

### Example

```python
from fastmcp import MCPClient
import asyncio

async def get_transcript():
    client = MCPClient("http://localhost:8000")
    async with client:
        transcript = await client.call_tool("get_youtube_transcript",
            {"url": "https://www.youtube.com/watch?v=dQw********"})
        print(transcript)

# Run the async function
asyncio.run(get_transcript())
```

## Deployment Options

For deploying the server in production environments, see [FastMCP transport options](https://gofastmcp.com/servers/fastmcp#transport-options).

To customize the transport, modify the `mcp.run()` call in `main.py`.

## Self-hosting File Storage

It's highly recommended to host your own instance of 0x0.st for file storage. Follow the [hosting instructions](https://git.0x0.st/mia/0x0) to set up your own instance.

## Roadmap

- [ ] Add tools to retrieve video metadata (title, date, description)
- [ ] Add YAML configuration for deployment settings
- [ ] Add more file hosting options (Google Cloud, S3)
- [ ] Complete local transcription option using [WhisperX](https://github.com/m-bain/whisperX)
- [ ] Support for other media sources e.g. Spotify podcasts

## Contributing

1. Install development dependencies:
   ```bash
   pip install pre-commit
   pre-commit install
   ```
2. Run pre-commit checks before submitting code:
   ```bash
   pre-commit run --all-files
   ```

## License

Licensed under the GPL-3.0 License
