import requests
import hashlib
from datetime import datetime
from backend.schemas import Hackathon
from pydantic import ValidationError

def parse_hackathon_dates(date_str: str):
    """
    Parses date strings from Devpost API like:
    - 'May 26 - Jul 10, 2025' (different months)
    - 'Jul 10 - 20, 2025' (same month)
    - 'Jul 10, 2025' (single day)
    """
    if not date_str or not isinstance(date_str, str):
        return None, None

    try:
        if ' - ' in date_str:
            start_str, end_str = date_str.split(' - ')
            
            year = end_str.split(',')[-1].strip()
            
            month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            has_month = any(month in end_str for month in month_names)

            if has_month:
                full_start_str = f"{start_str}, {year}"
                full_end_str = end_str
            else:
                month = start_str.split(' ')[0]
                full_start_str = f"{start_str}, {year}"
                full_end_str = f"{month} {end_str}"

            start_date = datetime.strptime(full_start_str, "%b %d, %Y").date()
            end_date = datetime.strptime(full_end_str, "%b %d, %Y").date()
            return start_date, end_date
        else:
            date = datetime.strptime(date_str, "%b %d, %Y").date()
            return date, date
    except (ValueError, IndexError):
        return None, None

def fetch_devpost_hackathons() -> list[Hackathon]:
    """
    Fetches and validates hackathon data from the first 20 pages of the official Devpost API.
    """
    hackathons = []
    for page in range(1, 21):
        url = f"https://devpost.com/api/hackathons?page={page}"
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            hackathon_data = resp.json().get("hackathons", [])
        except requests.RequestException as e:
            print(f"Error fetching URL (page {page}): {e}")
            continue
        except ValueError:
            print(f"Error decoding JSON from response on page {page}.")
            continue

        for item in hackathon_data:

            if item.get("open_state") == "ended":
                break
            start_date, end_date = parse_hackathon_dates(
                item.get("submission_period_dates")
            )

            mode = "Online"
            location: str
            if item.get("displayed_location"):
                location = item["displayed_location"].get("location", "Online")
            if location != "Online":
                mode = "Offline"
            else:
                location = "Everywhere"

            try:
                hackathon = Hackathon(
                    id=hashlib.sha256(str(item.get("id")).encode()).hexdigest(),
                    title=item.get("title"),
                    start_date=start_date,
                    end_date=end_date,
                    location=location,
                    url=item.get("url"),
                    mode=mode,
                    status=item.get("open_state"),
                    source="devpost",
                    tags=[theme["name"] for theme in item.get("themes", [])]
                )
                hackathons.append(hackathon)
            except ValidationError as e:
                print(f"Skipping hackathon due to validation error: {item.get('title')}")
                print(e)
    return hackathons

if __name__ == "__main__":
    fetch_devpost_hackathons()
