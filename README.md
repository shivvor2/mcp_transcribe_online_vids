
## Installation

### Installing dependencies
Start a new conda environment
```bash
conda create --name mcp_transcribe_online_vids python=3.12
conda activate mcp_transcribe_online_vids
```

Install FFMPEG and uv
```bash
conda install conda-forge::uv conda-forge::ffmpeg conda-forge::sqlite
```

Install dependencies via uv (to allow CLI deployment of server, see [fastmcp documentation](https://github.com/jlowin/fastmcp?tab=readme-ov-file#running-your-server))
```bash
uv pip install -r requirements.txt
```

### Adding
You are recommended to host your own version of 0x0.st, hosting instructions can be found [here](https://git.0x0.st/mia/0x0)
