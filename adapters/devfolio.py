import requests
import hashlib
from backend.schemas import Hackathon
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://devfolio.co/hackathons"

def parse_custom_date(date_string):
    try:
        day, month, year = date_string.split("/")
        full_year = f"20{year}" if len(year) == 2 else year
        parsed_date = datetime.strptime(f"{full_year}-{month}-{day}", "%Y-%m-%d")
        return parsed_date
    except Exception:
        return None

def scrape_devfolio_hackathons():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    hackathon_cards = soup.select(".CompactHackathonCard__StyledCard-sc-174a161-0")
    
    hackathons = []
    for card in hackathon_cards:
        title = card.find("h3").get_text(strip=True) if card.find("h3") else None
        
        participants = None
        participants_tag = card.select_one(".sc-hZgfyJ.iYRNEE")
        if participants_tag:
            digits = [int(s) for s in participants_tag.get_text(strip=True).split() if s.isdigit()]
            participants = digits[0] if digits else None
        
        mode_tag = card.select(".sc-hZgfyJ.ifkmYk")
        mode = mode_tag[0].get_text(strip=True) if len(mode_tag) > 0 else None
        status = mode_tag[1].get_text(strip=True) if len(mode_tag) > 1 else None
        start_date_text = mode_tag[2].get_text(strip=True) if len(mode_tag) > 2 else None
        
        link_tag = card.find("a")
        link = link_tag["href"] if link_tag else None

        # Date parsing
        date = None
        if status != "Ended":
            if start_date_text == "Live":
                date = datetime.today()
            else:
                try:
                    parts = start_date_text.split(" ")
                    if len(parts) == 1:
                        date = datetime.strptime(parts[0], "%b %d") 
                    else:
                        date = parse_custom_date(parts[1]) if "/" in parts[1] else datetime.strptime(parts[1], "%b %d")
                except Exception:
                    date = None
        
        if date:
            hackathon = Hackathon(
                id=hashlib.sha256(title.encode()).hexdigest(),
                title=title,
                start_date=date.date(),
                end_date=date.date(),
                location="Everywhere",
                url=link,
                mode="Online",
                status=status,
                source="Devfolio"
            )
            hackathons.append(hackathon)
            print(f"{hackathon}/n")
    return hackathons


if __name__ == "__main__":
    scarpe_devfolio_hackathons()

