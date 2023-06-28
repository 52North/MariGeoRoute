from datetime import datetime, timezone


def parse_datetime(datetime_str):
    try:
        return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
