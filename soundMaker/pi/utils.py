import datetime
    
def toTimestamp(dt):
    return int(dt.strftime("%s"))

def fromTimestamp(ts):
    return datetime.datetime.fromtimestamp(int(ts))

def humanReadableTime2(dt=None, sec=None):
    """ DEPRECATED """
    if sec:
        seconds = sec
    else:
        seconds = dt.seconds
    roundedSeconds300 = round(float(seconds)/300.0)*300 # round number of seconds to closest 5 minute increment
    roundedSeconds10 = round(float(seconds)/10.0)*10 # round number of seconds to closest 10 second increment
    days, hours, minutes = int(roundedSeconds300//86400), int(roundedSeconds300//3600), int((roundedSeconds300%3600)/60)

    # print roundedSeconds300
    # print days, hours, minutes

    if days < 0:
        print "ERORR: negative time"
        return ""

    if days + hours + minutes == 0:
        # print seconds%60
        return "%i seconds" % (roundedSeconds10%60)
    if days + hours == 0:
        return "%i minutes" % minutes
    if days == 0:
        if hours == 1: return "an hour"
        else: return "%s hours" % hours
    else:
        if days == 1: return "a day"
        elif days > 3: return "a long time"
        else: return "%s days" % days

    return ""

def humanReadableTime(dt=None, sec=None):
    if sec:
        dt = datetime.timedelta(seconds=sec)

    # print dt

    if dt.seconds < 0:
        print "ERROR: negative time"
        return None

    days, hours, minutes, seconds = int(dt.seconds//86400), int(dt.seconds//3600), int((dt.seconds%3600)/60), dt.seconds%60
    # print days, hours,minutes, seconds

    if days + hours + minutes == 0:
        return "%i seconds" % seconds
    if days + hours == 0:
        if minutes == 1: return "a minute"
        elif minutes == 2: return "a couple of minutes"
        else: return "%i minutes" % minutes
    if days == 0:
        if hours == 1: return "an hour"
        if hours == 2: return "a couple of hours"
        else: return "%s hours" % hours
    else:
        if days == 1: return "a day"
        elif days > 3: return "a long time"
        else: return "%s days" % days

    return ""

# now = datetime.datetime.now()
# dt = datetime.timedelta(seconds=180)
# then = now-dt
# print then,now
# print humanReadableTime2(dt=now-then)
# # print humanReadableTime(
