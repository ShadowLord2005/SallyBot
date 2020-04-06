import os
import random
import json
import discord
from discord.ext import commands
from discord.utils import get
import dotenv
import re
import giphy_client
from giphy_client.rest import ApiException
import requests
import instaloader
from bs4 import BeautifulSoup
import urllib.parse
import asyncio

os.chdir(os.path.dirname(os.path.abspath(__file__)))
if not os.path.isfile("data/friends.txt"):
    with open("data/friends.txt", "w") as file:
        file.write("689579955012632586")  # adds Tim Rodaway, creator, as first friend

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GIPHY_TOKEN = os.getenv("GIPHY_TOKEN")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


# Sets how often the translator occurs, defaulting to 10
try:
    with open("data/translation_frequency.txt", "r") as freq_file:
        translator_frequency = int(freq_file.readline())
except FileNotFoundError:
    with open("data/translation_frequency.txt", "w") as freq_file:
        freq_file.write("15")
    translator_frequency = 15
print(f"Translation Frequency set to {translator_frequency}")


# USEFUL FUNCTIONS
def search_gifs(query):
    try:
        return giphy_client.DefaultApi().gifs_search_get(GIPHY_TOKEN, query, limit=10, rating='g')
    except ApiException as e:
        return f"Exception when calling DefaultApi->gifs_search_get: {e}\n"


def gif_response(emotion):
    gifs = search_gifs(emotion)
    lst = list(gifs.data)
    gif = random.choices(lst)
    return gif[0].url


def translator(text_to_translate, dialect="geordie"):
    text_for_url = urllib.parse.quote(text_to_translate)
    url = f"http://www.whoohoo.co.uk/main.asp?string={text_for_url}&pageid={dialect}&topic=translator"
    x = requests.post(url, timeout=1)
    if x.status_code == 200:
        soup = BeautifulSoup(x.text, features="html.parser")
        translation = soup.find_all('form')[1].b.get_text(strip=True)
        return translation
    else:
        print(f"POST Request returned a status code of {x.status_code} for {url}")
        return None


# BASIC TEXT COMMANDS
bot = commands.Bot(command_prefix=commands.when_mentioned_or("?Sally"), case_insensitive=True)


async def status():
    while True:
        with open("data/activities.json", "r") as activities_file:
            activities = json.load(activities_file)
            single_activity = activities[str(random.choice(range(len(activities))))]
            if single_activity["type"] == "watching":
                activity = discord.Activity(name=single_activity["name"], type=discord.ActivityType.watching)
            elif single_activity["type"] == "listening":
                activity = discord.Activity(name=single_activity["name"], type=discord.ActivityType.listening)
            elif single_activity["type"] == "playing":
                activity = discord.Activity(name=single_activity["name"], type=discord.ActivityType.playing)
            else:
                activity = discord.Activity(name="The Sea", type=discord.ActivityType.watching)
            await bot.change_presence(activity=activity)
            print(f"*****\nStatus Changed\nType: {single_activity['type']}\nName: {single_activity['name']}")
        await asyncio.sleep(10)


@bot.command(name="hi", brief="I'll say hi", help="Say hi to me and I'll say hi back",
             aliases=["hello", "hey"])
async def hi(ctx):
    print(f"*****\nCommand: hi\nCalled by: {ctx.author}")
    await ctx.send(f'Hi {ctx.author.mention}!')


@bot.command(name="leo", brief="I'll talk about Leo", help="Leo is my best friend, let's talk about him!",
             aliases=["<@689751502700675072>", "<@!689751502700675072>", "<@&689751502700675072>"])  # Leo's user ID
async def leo(ctx):
    print(f"*****\nCommand: leo\nCalled by: {ctx.author}")
    await ctx.send("Leo is my Best Friend! We go on all our adventures together but he has to protect me, as other "
                   "SSAGO-ers like to steal me! :frowning:")


@bot.command(name="git", brief="Link to my Git repo", help="Get a link to the magic code behind me", aliases=["github"])
async def git(ctx):
    print(f"*****\nCommand: git\nCalled by: {ctx.author}")
    await ctx.send("Here's the git repo that contains all my inner code. I may look like the best teddy Seahorse you've"
                   " ever seen but there's a computer behind me!\nhttps://github.com/trodaway/SallyBot")


@bot.command(name="rally", brief="I'll talk about Viking Rally", help="Find out more about Viking Rally")
async def rally(ctx):
    print(f"*****\nCommand: rally\nCalled by: {ctx.author}")
    await ctx.send("My friends from NUSSAGG and DUSAGG are hosting Viking Rally in November 2021! Please come join us "
                   "for a weekend of great fun in the Toon and surrounding areas. Its a canny place to be! Find out "
                   "more about SSAGO's raid of the North East on the [SSAGO Website](https://viking-rally.ssago.org/)")


@bot.command(name="credits", brief="My credits", help="Find out who makes me work (or not work!)")
async def _credits(ctx):
    print(f"*****\nCommand: credits\nCalled by: {ctx.author}")
    try:
        with open("data/contributors.txt", "r") as contributors_file:
            contributors = "\n".join(contributors_file.readline().replace(", ", ",").split(","))
            await ctx.send(f"I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. I have the following "
                           f"people to thank for my creation:\n>>> {contributors}")
    except FileNotFoundError:
        await ctx.send("I'm SallyBot, a mascot from Geordie land, and I belong to NUSSAGG. Unfortunately my memory's "
                       "currently a little fuzzy as to who made me.")


@bot.command(name="fact", brief="Get a seahorse fact", help="I'll provide one of my many facts about seahorses")
async def fact(ctx):
    print(f"*****\nCommand: fact\nCalled by: {ctx.author}")
    try:
        with open("data/facts.json", "r") as fact_file:
            facts = json.load(fact_file)
            single_fact = facts[str(random.choice(range(len(facts))))]
            await ctx.send(single_fact)
    except FileNotFoundError:
        await ctx.send("I don't seem to know any facts at the minute :tired_face:. Please try again later!")


@bot.command(name="joke", brief="Get a seahorse joke", help="I'll provide one of my many jokes about seahorses")
async def joke(ctx):
    print(f"*****\nCommand: joke\nCalled by: {ctx.author}")
    try:
        with open("data/jokes.json", "r") as joke_file:
            jokes = json.load(joke_file)
            single_joke = jokes[str(random.choice(range(len(jokes))))]
            await ctx.send(single_joke)
    except FileNotFoundError:
        await ctx.send("I don't seem to know any jokes at the minute :tired_face:. Please try again later!")


@bot.command(name="friend", brief="Befriend me", help="Ask about being my friend", aliases=["befriend"])
async def friend(ctx):
    print(f"*****\nCommand: friend\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as friends_file:
            line = friends_file.readline()
            multiple_friends = line.split(",")
            for single_friend in multiple_friends:
                friend_list.append(single_friend)
        print(friend_list)
        if str(ctx.author.id) in friend_list:
            await ctx.send(f"{ctx.author.mention} you're already my friend!")
        else:
            with open("data/friends.txt", "a") as friends_file:
                friends_file.write(f",{ctx.author.id}")
            await ctx.send(f"{ctx.author.mention} you're now my friend!")
    except FileNotFoundError:
        await ctx.send(f"My memory's a little fuzzy right now. Please try asking me again later!")


@bot.command(name="friends", brief="Friend list", help="Discover who I am friends with")
async def friends(ctx):
    print(f"*****\nCommand: friends\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as friends_file:
            line = friends_file.readline()
            multiple_friends = line.split(",")
            for single_friend in multiple_friends:
                friend_list.append(single_friend)
        print(friend_list)
        if len(friend_list) == 0:
            await ctx.send(f"Unfortunately I don't have any friends at the moment. {ctx.author.mention}, perhaps you "
                           f"could befriend me")
        # else:
        #     await ctx.send(f"My friends are:\n>>> {chr(10).join([f'<@{i}>' for i in friend_list if i is not ''])}")
        else:
            friend_list_names = []
            for i in friend_list:
                if i != '':
                    name = bot.get_user(int(i)).name
                    friend_list_names.append(name)
            await ctx.send(f"My friends are:\n>>> {chr(10).join([i for i in friend_list_names])}")
    except FileNotFoundError:
        await ctx.send(f"My memory's a little fuzzy right now. Please try asking me again later!")


@bot.command(name="say", hidden=True, brief="Echoes what you say", help="Get Sally to say what you want her to say")
async def say(ctx, *, arg: str):
    print(f"*****\nCommand: say\nCalled by: {ctx.author}")
    await ctx.send(arg)


@bot.command(name="steal", brief="Try and steal me", help="You can try and steal me, but will you succeed?")
async def steal(ctx):
    print(f"*****\nCommand: steal\nCalled by: {ctx.author}")
    try:
        friend_list = []
        with open("data/friends.txt", "r") as friends_file:
            line = friends_file.readline()
            multiple_friends = line.split(",")
            for single_friend in multiple_friends:
                if single_friend != '':
                    friend_list.append(int(single_friend))
        # if a NUSSAGG member tries to steal
        if 692795798416523356 in [role.id for role in ctx.author.roles]:
            await ctx.send(f"{ctx.author.mention} you can't steal me, you're part of my club")
        # if a friend tries to steal, un-friend them
        elif ctx.author.id in friend_list:
            friend_list.remove(ctx.author.id)
            with open("data/friend.txt", "w") as f:
                f.write(",".join(friend_list))
            await ctx.send(f"{ctx.author.mention} you were meant to be my friend")
        # if someone else tries to steal, they fail
        else:
            await ctx.send("Better luck next time, I swam away")
    except FileNotFoundError:
        await ctx.send("Better luck next time, I swam away")


@bot.command(name="frequency", hidden=False, brief="Change how often I translate",
             help="Set the frequency of my translations. Set me to 0 to stop")
async def frequency(ctx, arg):
    global translator_frequency
    translator_frequency = int(arg)
    with open("data/translation_frequency.txt", "w") as freq:
        freq.write(str(translator_frequency))
    print(f"***** Translator frequency set to: {translator_frequency} *****")
    if translator_frequency == 0:
        await ctx.send("I'll stop translating")
    elif translator_frequency == 1:
        await ctx.send("I'll translate every message!")
    else:
        await ctx.send(f"There's now a 1 in {translator_frequency} chance of me translating a message")


@bot.command(name="instagram", brief="Link to my Instagram", help="Get a link to mine and Leo's Instagram")
async def instagram(ctx):
    print(f"*****\nCommand: instagram\nCalled by: {ctx.author}")
    with ctx.channel.typing():
        # displays the latest instagram photo on Sally and Leo's profile
        insta = instaloader.Instaloader()
        insta.login("nussaggsallyandleo", INSTAGRAM_PASSWORD)
        profile = instaloader.Profile.from_username(insta.context, "nussaggsallyandleo")
        posts = profile.get_posts()
        post = next(posts)
        print(post)
        image_path = "nussaggsallyandleo_latest_insta.jpg"
        if os.path.exists(image_path):
            os.remove(image_path)
        with open(image_path, "wb") as f:
            f.write(requests.get(post.url).content)
        await ctx.send(f"<@689751502700675072> and I are on Instagram; you can find us at "
                       f"https://www.instagram.com/nussaggsallyandleo/. As a taster, here's our latest pic...\n\n>>> "
                       f"{post.caption}",
                       file=discord.File(image_path))
    os.remove(image_path)


@bot.event
async def on_message(message):
    # ctx = bot.get_context(message)
    channel = message.channel
    print(f"*****\nContent: {message.content}\nAuthor: {message.author}\nAuthor ID: {message.author.id}\nChannel: "
          f"{channel.name}")
    ctx = await bot.get_context(message)

    # stops it replying to itself
    if (message.author == bot.user) or (message.content == ""):
        print("Trigger: It's me!")
        return

    # reacts to all of Leo's messages
    else:
        if message.author.id == 689751502700675072:
            print("Trigger: It's Leo!")

            if re.match("^Ro+a+r$", message.content) is not None:  # reacts to Leo's roars
                print("Trigger: Leo Roared")
                choice = random.choice(range(3))
                if choice == 0:
                    print("Response: argh")
                    count = message.content.count("o")
                    await channel.send(
                        f"{'a' * count + 'r' * int(count / 2) + 'g' * int(count / 2) + 'h' * int(count / 2)}")
                elif choice == 1:
                    with channel.typing():
                        print("Response: scream")
                        await channel.send(gif_response("scream"))
                else:
                    print("Response: shush")
                    await channel.send(":shushing_face:")

            else:  # any of Leo's messages that aren't roars
                print("Trigger: add a reaction")
                try:
                    sally_emoji = get(bot.emojis(), id="689616621576257557")
                    await message.add_reaction(sally_emoji)  # only works on SSAGO server
                except discord.errors.HTTPException:
                    await message.add_reaction(u"\U0001F929")  # back-up, if not on the SSAGO server

        elif re.match("^<@[&!]?693216082567233667>$", message.content) is not None:
            await channel.send("Wey aye, aareet, that's wor!")

        # translates every 'x' to geordie
        elif translator_frequency != 0:  # set it to 0 to stop it from translating
            if random.randrange(translator_frequency) == 0 and \
                    re.match("^<@[&!]?693216082567233667>.*$", message.content) is None:
                translated_text = translator(message.content)
                if translated_text is not None and not (translated_text == message.content or
                                                        translated_text.rstrip(".") == message.content):
                    await channel.send(f"In the Toon we'd say that like:\n>>> {translated_text}")

    print("Pre-regex")

    # Hi
    if re.match(r"(?i)^<@[&!]?693216082567233667> (hi|hello|hey|wye aye|aareet|alreet)[!.?]?$", message.content) is \
            not None:
        print("*****\nRegex- Hi")
        await hi(ctx)

    # Leo
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (<@[&!]?689751502700675072>|leo (the)? lion)[!.?]?$",
                  message.content) is not None:
        print("*****\nRegex- Leo")
        await leo(ctx)

    # Git
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (git(hub)?|brains?)[!.?]?$", message.content) is not None:
        print("*****\nRegex - Git")
        await git(ctx)

    # Rally
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((viking|autumn|ssago) )?rally[!.?]?$", message.content) is not \
            None:
        print("*****\nRegex - Rally")
        await rally(ctx)

    # Credits
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (cred(it)?s?|contrib(utor)?s?)[!.?]?$", message.content) is not \
            None:
        print("*****\nRegex - Credits")
        await _credits(ctx)

    # Facts
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((sea[ -]?horse) )?facts?[!.?]?$", message.content) is not None:
        print("*****\nRegex - Facts")
        await fact(ctx)

    # Jokes
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((sea[ -]?horse) )?jokes?[!.?]?$", message.content) is not None:
        print("*****\nRegex - Jokes")
        await joke(ctx)

    # Friend
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (friend|befriend|(((let('s| us) be)|can we be|((do )?(yo)?u )?want "
                  "to be) friends?))[.!?]?$", message.content) is not None:
        print("*****\nRegex - Friend")
        await friend(ctx)

    # Friends
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((who are your )?friends|friends?[ -]?list|who are you friends "
                  r"with)[!.?]?$", message.content) is not None:
        print("*****\nRegex - Friends")
        await friends(ctx)

    # Steal
    elif re.match(r"(?i)^<@[&!]?693216082567233667> steal[!.?]?$", message.content) is not None:
        print("*****\nRegex - Friends")
        await steal(ctx)

    # Frequency
    elif re.match(r"(?i)^<@[&!]?693216082567233667> ((set|translat(e|or)|geordie) )*freq(uency) \d+[!?.]?$",
                  message.content) is not None:
        print("*****\nRegex - Friends")
        value = re.match(r"(?i)^<@[&!]?693216082567233667> ((set|translat(e|or)|geordie) )*freq(uency) \d+[!?.]?$",
                         message.content).string.split()[-1].replace("!", "").rstrip("!?.")
        await frequency(ctx, value)

    # Instagram
    elif re.match(r"(?i)^<@[&!]?693216082567233667> (instagram|insta|nussaggsallyandleo)[!.?]?$", message.content) is \
            not None:
        print("*****\nRegex - Insta")
        await instagram(ctx)

    else:
        await bot.process_commands(message)  # runs commands first


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("I don't understand that command. Type `@SallyBot help` to learn what I can do")
        return
    raise error


@bot.event
async def on_ready():
    print("I'm connected and ready to go!")

    bot.loop.create_task(status())  # sets custom statuses for the bot


bot.run(TOKEN)
