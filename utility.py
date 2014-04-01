# Convert duration objects into human-readable form
def duration_to_plain_english(duration):
    duration_mins, duration_secs = divmod(duration.seconds, 60)
    duration_hours, duration_mins = divmod(duration_mins, 60)

    duration_text = ""

    if duration.days > 0:
        if duration.days == 1:
            duration_text += "1 day, "
        else:
            duration_text += str(duration.days) + " days, "

    if duration_hours > 0:
        if duration_hours == 1:
            duration_text += "1 hour, "
        else:
            duration_text += str(duration_hours) + " hours, "

    if duration_mins == 1:
        duration_text += "1 minute"
    else:
        duration_text += str(duration_mins) + " minutes"

    return duration_text
