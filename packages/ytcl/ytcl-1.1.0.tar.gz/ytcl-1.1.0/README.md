# ytcl
ytcl is a command-line frontend for
[ytdl-server](https://gitlab.com/adralioh/ytdl-server).

Its syntax is based on youtube-dl/yt-dlp, and it shares many of the same
arguments.

[TOC]

## Installation
ytcl requires [Python](https://www.python.org/) 3.7+.

If you're using an Arch-based distro, ytcl is available in the
[AUR](https://aur.archlinux.org/packages/ytcl/).

Install from [PyPI](https://pypi.org/project/ytcl/):
```bash
pip3 install ytcl
```

Install from source:
```bash
git clone 'https://gitlab.com/adralioh/ytcl.git'
pip3 install ./ytcl
```

If you want color output to work on Windows, you can also optionally install
[Colorama](https://github.com/tartley/colorama):
```bash
pip3 install 'ytcl[windows_color]'
```

## Usage
First, you must set the `$YTDL_SERVER` env-var to the URL of the ytdl-server
so that ytcl can connect to it:
```bash
export YTDL_SERVER=http://ytdl-server.example.com
```

### Create a job
Download videos by creating a job:
```bash
ytcl create 'https://youtu.be/dQw4w9WgXcQ'
```

You can pass most arguments that youtube-dl accepts. Example:
```bash
ytcl create -f 'bestaudio/best' --extract-audio 'https://youtu.be/dQw4w9WgXcQ'
```

You can also start a job without waiting for it to finish:
```bash
ytcl -d create 'https://youtu.be/dQw4w9WgXcQ'
```

Run `ytcl create --help` for an exhaustive list of arguments.

### Get the status of a job
You can check the status of a job using the job ID:
```bash
ytcl get 'b7cce5f7-9f7c-47ed-ae13-2acf7c32cc29'
```

> The job ID is obtained from the output of the command where you create the
  job.

The above command will run until the job finishes. If you just want to get the
complete current status of the job, you can change the output format:
```bash
ytcl -f all get 'b7cce5f7-9f7c-47ed-ae13-2acf7c32cc29'
```

JSON output is also supported:
```bash
ytcl -f json get 'b7cce5f7-9f7c-47ed-ae13-2acf7c32cc29'
```

### Cancel a job
You can also cancel a running job:
```bash
ytcl cancel 'b7cce5f7-9f7c-47ed-ae13-2acf7c32cc29'
```

The above command will wait until the job is cancelled. You can also exit
immediately without waiting:
```bash
ytcl -d cancel 'b7cce5f7-9f7c-47ed-ae13-2acf7c32cc29'
```

### Basic authentication
If the ytdl-server uses basic authentication, you can provide the credentials
via the `$YTDL_SERVER_USERNAME` and `$YTDL_SERVER_PASSWORD` env-vars:
```bash
export YTDL_SERVER_USERNAME=user
export YTDL_SERVER_PASSWORD=password
```

If only the username is provided, you will be prompted for the password
interactively.

## Exit codes
ytcl exits with the following exit codes when an error occurs:

| Code | Description                                                          |
| ---: | -------------------------------------------------------------------- |
|    2 | Invalid argument                                                     |
|   10 | Unspecified error                                                    |
|   11 | ytcl tried to use a ytdl_opt that is blacklisted by the ytdl-server when creating a job |
|   12 | ytcl tried to use a custom_opt that is blacklisted by the ytdl-server when creating a job |
|   13 | ytcl tried to cancel a job that has already completed                |
|   14 | The job failed                                                       |
|   15 | ytcl received an error response from the ytdl-server                 |
|   16 | The URL of the ytdl-server wasn't provided. This can be set via the `$YTDL_SERVER` env-var |
