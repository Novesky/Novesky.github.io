import requests
import re
import yaml
from icalendar import Calendar

with open("config.yaml") as f:
    cfg = yaml.safe_load(f)

include = [re.compile(x, re.I) for x in cfg["include"]]
exclude = [re.compile(x, re.I) for x in cfg["exclude"]]

out = Calendar()
out.add("X-WR-CALNAME", "A+S Holidays")
out.add("X-WR-TIMEZONE", "America/Chicago")
seen = set()

for url in cfg["sources"]:
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    cal = Calendar.from_ical(r.content)

    for c in cal.walk():
        if c.name != "VEVENT":
            continue

        summary = str(c.get("SUMMARY", ""))
        
        keep = any(p.search(summary) for p in include)
        reject = any(p.search(summary) for p in exclude)
        if not keep or reject:
            continue

        # dedupe on name + start date
        key = (summary, str(c.get("DTSTART")))
        if key in seen:
            continue
        seen.add(key)

        out.add_component(c)

with open("custom_holidays.ics", "wb") as f:
    f.write(out.to_ical())

print("done")
