from datetime import datetime, timezone


def convert_datetime(dt64):
    """Convert numpy.datetime64 to datetime.datetime

    :returns: datetime.datetime object or None
    """

    if dt64.dtype == '<M8[s]' or dt64.dtype == '<m8[s]':
        return datetime.fromtimestamp(dt64.astype(int), tz=timezone.utc)
    elif dt64.dtype == '<M8[ms]' or dt64.dtype == '<m8[ms]':
        return datetime.fromtimestamp(dt64.astype(int) * 1e-3, tz=timezone.utc)
    elif dt64.dtype == '<M8[us]' or dt64.dtype == '<m8[us]':
        return datetime.fromtimestamp(dt64.astype(int) * 1e-6, tz=timezone.utc)
    elif dt64.dtype == '<M8[ns]' or dt64.dtype == '<m8[ns]':
        return datetime.fromtimestamp(dt64.astype(int) * 1e-9, tz=timezone.utc)
    elif dt64.dtype == '<M8[ps]' or dt64.dtype == '<m8[ps]':
        return datetime.fromtimestamp(dt64.astype(int) * 1e-12, tz=timezone.utc)
    else:
        print("... do not know how to convert numpy.datetime64 with dtype '{}'"
              " to datetime.datetime object".format(dt64.dtype))
        return None


def parse_datetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
