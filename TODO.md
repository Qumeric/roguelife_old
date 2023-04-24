# TODO

This is un unsorted todo list where I will write every idea I have

## Observation System
* Add more observations, such as movement, pickup etc.
* Make it possible to see observation logs from the game.
* Implement summary function for the log. Use gpt3.5-turbo.

## Components
* Seems like adding update to every component is a sensible design choice? Some will do nothing but it doesn't matter?

## Word generation
* Probably move from dungeons to open world. See existing implementations.
* Add gender.

## Performance
* Handle dead entities more gracefully.

## Bugs
* Observations at the same turn are not always logically ordered. For example, death message may happen before 0 hp message.
* It seems that some instant actions are not actually instant? E.g. LookAround
* Save is broken and throws errors about DuckDBPyConnection which I probably don't need.

## General
* Maybe think about using special game time instead of Python datetime.
* Maybe use some kind of DSL to describe creatures? Shall focus on easy generation of many different ones. Although python is close enough to DSL already lol.
* Add limited integer class. There are many things which can go from 0 to some value and act the same way. They can also be used for rendering in unified fashion.
* Everything has backlink to parent now. Maybe it's a bad idea because it violates composition/encapsulation. And also creates typing issues occasionally.
* Use LangChain and possibly Chroma-langchain (if it's not deprecated)?

## Learning
* Read Reflexion paper lol.

## Generative Agents

### Memory and Retrieval
* Add importance to observations. Using LLMs would be to costly, so implement it in the game.
* Implement relevance score. Use embeddings?
* Maybe reuse https://python.langchain.com/en/latest/use_cases/agent_simulations/characters.html ?
