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
* Add trees. They should spawn apples sometimes.

## Performance
* Handle dead entities more gracefully.

## Bugs
* Observations at the same turn are not always logically ordered. For example, death message may happen before 0 hp message.

## General
* Maybe think about using special game time instead of Python datetime.
* Maybe use some kind of DSL to describe creatures? Shall focus on easy generation of many different ones. Although python is close enough to DSL already lol.
* Add limited integer class. There are many things which can go from 0 to some value and act the same way. They can also be used for rendering in unified fashion.