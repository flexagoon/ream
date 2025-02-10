<h1 align="center">ream</h1>

<p align="center">
    <i>/rim/</i> noun<br/>
    a large quantity of written matter
</p>

---

**`ream`** is a tool that lets you easily export all of your important Telegram
chats.

It is a standalone re-implementation of Telegram Desktop's export
functionality. The output from **`ream`** must be fully equivalent to the
output from Telgram Desktop, and **any difference in the resulting json (except
for filenames) is treated as a bug.**

> [!WARNING]
> **`ream`** is only meant to be used for downloading private chats.
> 
> Using it to export channels or groups may produce incomplete output or even
> get your account rate-limited.

## Installation

- Install [Poetry](https://python-poetry.org)
- Clone this repository
- Run `poetry install` to get the dependencies

## Configuration

First, you have to [follow this
instruction](https://core.telegram.org/api/obtaining_api_id) to obtain Telegram
API credentials.

To run **`ream`**, you must create a configuration file named `ream.toml` with
the following contents:

```toml
[api] # Your API credentials
app_id = 123456
app_hash = "abcdefg01234"

[export]
max_file_size = 5000000000 # Max size for files to be downloaded
chats = [ 123456, 7891234 ] # A list of chat ids to download
path = "exports" # A directory in which your chat exports will be saved
batch_size = 100 # How many messages to download at once. Higher values make
                 # the export faster, but increase the risk of getting rate
                 # limited.

[ream]
log_level = "ERROR" # Optional: log level for the application, defaults to INFO
```

## Running

```bash
poetry run ream.py
```

The first time you run the program, It'll ask you to enter your phone number
and login code.

**`ream`** may throw an error after you log in. If that happens, you need to
confirm the data export request that you got on your Telgram account, and try
running **`ream`** again.

Incremental exports are supported, which means that **`ream`** will only export
messages that aren't already present in the `export.json` file for a given
chat. You can run **`ream`** as a scheduled job without having to deal with
duplicate data.
