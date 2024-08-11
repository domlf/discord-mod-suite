import discord
from discord.ext import commands
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class MessageLog(Base):
    __tablename__ = 'message_logs'
    id = Column(Integer, primary_key=True)
    user = Column(String)
    content = Column(Text)
    channel = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    avatar_url = Column(String)  # Added field for avatar URL

class EventLog(Base):
    __tablename__ = 'event_logs'
    id = Column(Integer, primary_key=True)
    event_type = Column(String)
    details = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(engine)

# Discord Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Event listener for message logs
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Include avatar URL in the log entry
    log_entry = MessageLog(
        user=str(message.author),
        content=message.content,
        channel=str(message.channel),
        avatar_url=str(message.author.display_avatar.url)  # Updated field
    )
    session.add(log_entry)
    session.commit()
    
    await bot.process_commands(message)

# Event listener for message edits
@bot.event
async def on_message_edit(before, after):
    details = f'Message edited by {after.author} in {after.channel}. Before: "{before.content}". After: "{after.content}".'
    event_log = EventLog(event_type='Message Edited', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for message deletion
@bot.event
async def on_message_delete(message):
    if message.attachments:
        archive_channel = discord.utils.get(message.guild.channels, name="Deleted archive")
        if archive_channel:
            for attachment in message.attachments:
                await attachment.save(attachment.filename)
                await archive_channel.send(file=discord.File(attachment.filename))

    details = f'Message by {message.author} in {message.channel} was deleted: {message.content}'
    event_log = EventLog(event_type='Message Deleted', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for member join
@bot.event
async def on_member_join(member):
    details = f'{member} joined the server.'
    event_log = EventLog(event_type='Member Join', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for member leave
@bot.event
async def on_member_remove(member):
    details = f'{member} left the server.'
    event_log = EventLog(event_type='Member Leave', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for channel creation
@bot.event
async def on_guild_channel_create(channel):
    details = f'Channel {channel.name} was created.'
    event_log = EventLog(event_type='Channel Created', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for voice state update
@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        details = f'{member} joined voice channel {after.channel.name}.'
        event_log = EventLog(event_type='Voice Channel Join', details=details)
    elif before.channel is not None and after.channel is None:
        details = f'{member} left voice channel {before.channel.name}.'
        event_log = EventLog(event_type='Voice Channel Leave', details=details)
    elif before.channel != after.channel:
        details = f'{member} switched from {before.channel.name} to {after.channel.name}.'
        event_log = EventLog(event_type='Voice Channel Switch', details=details)
    
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for command usage
@bot.event
async def on_command(ctx):
    details = f'Command {ctx.command} was used by {ctx.author} in {ctx.channel}.'
    event_log = EventLog(event_type='Command Used', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for role creation
@bot.event
async def on_guild_role_create(role):
    details = f'Role {role.name} was created.'
    event_log = EventLog(event_type='Role Created', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for role deletion
@bot.event
async def on_guild_role_delete(role):
    details = f'Role {role.name} was deleted.'
    event_log = EventLog(event_type='Role Deleted', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for role assignment and server boosts
@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        details = f'{after.name} boosted the server.'
        event_log = EventLog(event_type='Server Boost', details=details)
        session.add(event_log)
        session.commit()
        logging.info(details)
    
    for role in after.roles:
        if role not in before.roles:
            details = f'Role {role.name} was assigned to {after.name}.'
            event_log = EventLog(event_type='Role Assigned', details=details)
            session.add(event_log)
            session.commit()
            logging.info(details)

# Event listener for emoji update
@bot.event
async def on_guild_emojis_update(guild, before, after):
    added = [e for e in after if e not in before]
    removed = [e for e in before if e not in after]
    if added:
        details = f'Emojis added: {", ".join(e.name for e in added)}.'
        event_log = EventLog(event_type='Emojis Added', details=details)
        session.add(event_log)
        session.commit()
        logging.info(details)
    if removed:
        details = f'Emojis removed: {", ".join(e.name for e in removed)}.'
        event_log = EventLog(event_type='Emojis Removed', details=details)
        session.add(event_log)
        session.commit()
        logging.info(details)

# Event listener for server update
@bot.event
async def on_guild_update(before, after):
    details = f'Server updated. Before: {before.name}, After: {after.name}.'
    event_log = EventLog(event_type='Server Updated', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)

# Event listener for typing start
@bot.event
async def on_typing(channel, user, when):
    details = f'{user} started typing in {channel} at {when}.'
    event_log = EventLog(event_type='User Typing', details=details)
    session.add(event_log)
    session.commit()
    logging.info(details)


# Running the bot
bot.run(os.getenv("DISCORD_TOKEN"))
