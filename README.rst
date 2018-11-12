===========
omnimetrics
===========

The goal is to gather metrics from OmniFocus so I can get a sense of

 - how heavy my workload is
 - whether I am making progress

But in reality this is a bunch of scripts to do stuff with OmniFocus.

Assumptions
===========

- OmniFocus 3

Brainstorm
==========

What questions do I want answered?

- I want some kind of warning when I've taken too much on

  - this probably means too many actions?

- I want to know whether I've had a productive day / week or not

  - productive == lots of things completed
  - winning == more things completed than added
  - unproductive == lots of things added

- I want some kind of split between "Work" and "Personal" domains

- How realistic is my plan for "today"?

  - will the things there take a while

Procrastinatron
---------------

It's way too easy to get paralysed by choice when looking at a todo list.

The perfect todo list would show you the **one** task that you should and can do right now.

This tool queries OmniFocus to get a set of all the available tasks to you right now. It then shows you **only one**.

You can then choose to do it. If so, the procrastinatron starts a timer. When you are done, the timer stops, and the task is removed from your todo list.

Or, you can choose *not* to do it. When you do this, you must say why you don't want to do it.
