# notes for ai-secretary project

## for icloud.py

```
principal = client.principal()
for calendar in principal.calendars():
    print(calendar.get_display_name())
```

- `client` is the person that u welcome, that person is me.
- `client.principal()` is my apartment (my account).
- `principal.calendars()` asked for all the room in my apartment and returns all the rooms as a list.
- `calendar.get_display_name()` is the name of the chosen room in my apartment, only one room.

**Why parentheses on `principal()`?**
- With `()`, it is a method, and method does something.
- Without `()`, it is an attribute: a value that's already there, like a sign on a door. For example: `message.text` & `response.model`
