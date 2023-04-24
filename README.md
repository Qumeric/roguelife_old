# Roguelife
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Important
**This repo was abandoned. It was replaced by two separate repos: [Trip](https://github.com/Qumeric/Trip) (engine) and [Roguelife](https://github.com/Qumeric/Roguelife) (new game repo)**

Roguelike with [Generative Agents](https://arxiv.org/pdf/2304.03442.pdf).

Very early stage, work in progress.

## Idea / Origin Story
Generative Agents paper inspired me to create something similar but more hopefully more interesting.

I decided to use roguelike environment because it seemed to be the simplest possible approach.

Agents wake up on an island and try to survive.

My ultimate goal is to make agents cooperate and create alliances which will compete for resources.

Roguelife was based on the [TCOD Tutorial](https://rogueliketutorials.com/tutorials/tcod/v2/).

After some tinkering, I realised that strictly following Generative Agents is prohibitatively resource intensive (one simulation day in Smallvile cost 1000$ and it still was too simple/small-scale for my ambition).

So I decided to follow another approach: convert the 2d game world to text and represent it to agents as a [text adventure](https://en.wikipedia.org/wiki/Interactive_fiction).

At the moment, I have no idea how well it will work, but I am currently focused on developing the game engine for it.


## Usage
You will need OpenAI account for it.

Install requirements
```
pip install -r requirements
```

create `.env` file:
```
OPENAI_ORG=<HERE IS YOUR ORG>
OPENAI_API_KEY=<HERE IS YOUR SECRET KEY>
```

Now you can run it with simple `python main.py`.

Be careful because it will make paid requests.
