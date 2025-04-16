import random
# Fun spinner messages for loading states
SPINNER_MESSAGES = [
    "Consulting the data oracles…",
    "Warming up the algorithms…",
    "Doing math in public—please hold.",
    "Fetching facts from the digital void…",
    "This is your data on a coffee break ☕",
    "Manifesting your metrics…",
    "Plotting world domination... just kidding (or are we?)",
    "Giving your data a pep talk…",
    "Crunching numbers like a breakfast cereal.",
    "The data is shy. We're coaxing it out.",
    "Let's all pretend this isn't an awkward silence…",
    "Just you, me, and this dramatic pause.",
    "Cue elevator music…",
    "Avoiding eye contact with the loading bar…",
    "Your data is fashionably late.",
    "This awkward silence brought to you by the data gods.",
    "While we wait, think of your favorite spreadsheet.",
    "Your data is buffering. Like our small talk.",
    "Even your data needs a moment.",
    "Dramatic pause… data's on its way."
]

def get_random_spinner_message():
    """Return a random spinner message from the list."""
    return random.choice(SPINNER_MESSAGES)
