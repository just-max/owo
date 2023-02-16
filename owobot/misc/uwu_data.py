# This is stolen and merged from owoifier https://github.com/FernOfSigma/owoifier/tree/main/owoifier
# and https://github.com/Daniel-Liu-c0deb0t/uwu/blob/uwu/src/lib.rs
# special thanks goes to https://www.reddit.com/r/creepyasterisks/top/?t=year

import re

prefixes = (
    "OwO",
    "OwO what's this?",
    "*nuzzles*",
    "*blushes*",
    "*notices bulge*",
    "K-Konichiwa",
    "*blush*",
    "*heart goes doki-doki*",
    "*boops your nose*",
    "giggles",
    "*gives you headpats*",
    "*wags tail*",
    "*pets you*",
    "*tips fedora*",
)


# first entry is what to replace (may be a regular expression)
# second entry is what to replace with (may be function accepting regular expression match and returning string)
# (optional, required if second entry is a regular expression) third entry is used to score owo-ness of messages
mappings0 = (
    ("r", "w"),
    ("l", "w"),
    ("na", "nya"),
    ("ni", "nyi"),
    ("nu", "nyu"),
    ("ne", "nye"),
    ("no", "nyo"),
    ("ove", "uv"),
    ("small", "smol"),
    ("cute", "kawaii~"),
    ("fluff", "floof"),
    ("love", "luv"),
    ("stupid", "baka"),
    ("what", "nani"),
    ("meow", "nya~"),
    ("ee", "ew"),
    ("at", "awt"),
    ("oops", "oopsie woopsie"),
)
mappings = tuple((re.compile(m[0]), m[1], re.compile(m[-1])) for m in mappings0)


int_emote = (
    "rawr x3",
    "OwO",
    "UwU",
    "o.O",
    "-.-",
    ">w<",
    "(⑅˘꒳˘)",
    "(ꈍᴗꈍ)",
    "(˘ω˘)",
    "(U ᵕ U❁)",
    "σωσ",
    "òωó",
    "(///ˬ///✿)",
    "(U ﹏ U)",
    "( ͡o ω ͡o )",
    "ʘwʘ",
    ":3",
    "XD",
    "nyaa~~",
    "mya",
    ">_<",
    "😳",
    "🥺",
    "😳😳😳",
    "rawr",
    "^^",
    "^^;;",
    " (ˆ ﻌ ˆ)♡",
    " ^•ﻌ•^",
    " /(^•ω•^)",
    " (✿oωo)",
    "^w^",
    "(◕ᴥ◕)",
    "ʕ•ᴥ•ʔ",
    "ʕ￫ᴥ￩ʔ",
    # these do funny things with markdown
    # "(*^ω^)",
    "(◕‿◕✿)",
    # "(*^.^*)",
    # "(*￣з￣)",
    "(つ✧ω✧)つ",
    "(/ =ω=)/",
    ">///<",
    "-w-",
    "QwQ",
)

sowwy = (
    "sowwy",
    "owo nowww",
    "nowo",
    "owupsie",
    "I'm sowwwyy ~~",
    "nani?",
    "s-s-sadwy you cwannot dow that",
    "i w-want to compwy, mwaster, but i cwannot",
    "Baka!",
)

good_owo_spirit = (
    "umu",
    "owo",
    "uwu",
    "~~~",
    "senpai",
    "oni",
    "chan",
    "nicole",
    "desu",
    "nowu",
    "desu",
    "haj",
    "wolf",
    "neko",
    "kon",
)
