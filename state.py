"""Persistence — JSON log and event helpers."""

import json
import os

DATA_PATH = "dog_log.json"


def load_state():
    if not os.path.exists(DATA_PATH):
        return {"events": []}
    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_state(st):
    tmp = DATA_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
    os.replace(tmp, DATA_PATH)


state = load_state()


def log_event(ev):
    state["events"].append(ev)
    save_state(state)


def last_dog_where(pred):
    for ev in reversed(state["events"]):
        if ev.get("type") == "dog" and pred(ev):
            return ev
    return None

def undo_last_dog_event():
    """Remove and return the most recent event with type == 'dog'.

    Returns the removed event dict, or None if there was no dog event to remove.
    """
    # iterate backwards to find the most recent dog event
    for i in range(len(state["events"]) - 1, -1, -1):
        ev = state["events"][i]
        if ev.get("type") == "dog":
            removed = state["events"].pop(i)
            save_state(state)
            return removed
    return None
