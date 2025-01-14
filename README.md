# Get Vercel Source Code

## Instructions

1 - Install the dependecies.

```
pip install requests python-dotenv
```

2 - Get your Vercel token at https://vercel.com/account/tokens, copy `.env.sample` as `.env` and update the value:

```
VERCEL_TOKEN = ""
# Optionally if using a team account
VERCEL_TEAM = ""
```

3 - Run the script and wait until complete.

```
python <VERCEL DEPLOYMENT URL or ID> <DESTINATION>
```

For example, `python main.py https://your-deployment-url.vercel.app /path/to/destination`.

Or using the id directly, `python fetch_vercel_source.py dpl_id /path/to/destination`.
