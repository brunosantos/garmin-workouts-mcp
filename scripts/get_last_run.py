import json
import sys
from datetime import datetime

try:
    from garmin_workouts_mcp import init_api
except Exception as e:
    print("Error: cannot import project package. Make sure you're running from the repository root.", file=sys.stderr)
    raise


def fmt_activity(a: dict) -> dict:
    return {
        "id": a.get("activityId") or a.get("activity_id"),
        "name": a.get("activityName") or a.get("name"),
        "type": (a.get("activityType") or {}).get("typeKey") if isinstance(a.get("activityType"), dict) else a.get("activityType"),
        "start_time": a.get("startTimeLocal") or a.get("start_time_local") or a.get("startTimeGMT"),
        "distance_m": a.get("distance"),
        "duration_s": a.get("duration"),
    }


def main():
    # init_api uses tokens if present; pass None for email/password to prefer tokens
    garmin = init_api(None, None)
    if not garmin:
        print("Failed to initialize Garmin client. Run 'garmin-mcp-auth' to create tokens first.")
        sys.exit(2)

    try:
        # Get newest activities (0 = newest). Request 50 to ensure we find recent runs.
        activities = garmin.get_activities(0, 50)
    except Exception as e:
        print(f"Error fetching activities: {e}")
        sys.exit(3)

    if not activities:
        print("No activities returned from Garmin Connect.")
        sys.exit(0)

    # activities are ordered newest first. Find first running activity.
    last_run = None
    for a in activities:
        # activityType may be a dict with typeKey or a string
        at = a.get("activityType")
        type_key = None
        if isinstance(at, dict):
            type_key = at.get("typeKey")
        elif isinstance(at, str):
            type_key = at

        if type_key and type_key.lower() in ("running", "run"):
            last_run = a
            break

    if not last_run:
        # fallback: take the very first activity
        last_run = activities[0]
        print("No running activity found in the most recent activities; showing newest activity instead.")

    print(json.dumps(fmt_activity(last_run), indent=2, default=str))


if __name__ == "__main__":
    main()
