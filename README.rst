===========
omnimetrics
===========

.. image:: https://travis-ci.org/jml/omnimetrics.svg?branch=master
    :target: https://travis-ci.org/jml/omnimetrics

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

You can pause the timer, of course, and Procrastinatron will ask for a reason, to subtly encourage you to stay on target. You can also abandon the attempt to work on item, and again Procrastinatron will want to know why. All of these things are logged.

Or, you can choose *not* to do it. When you do this, you must say why you don't want to do it. Procrastinatron keeps a log of this. Each time you are presented with that item again, you also get to see your past excuses. Once there are a sufficient number of excuses (say 3), Procrastinatron suggests that maybe you should just abandon the task.

Procrastinatron only ever shows available tasks. If a task becomes available during a Procrastinatron session, it jumps to the front of the queue. This is intended to facilicate flow through connected tasks.

Once you've done or deferred every available task, Procrastinatron will ask if you want to do another loop round, to tackle the ones you deferred.
