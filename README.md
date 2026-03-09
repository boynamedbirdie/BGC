For the regular season, you can get all W-L and schedule info from ESPN. Will need to pull the projected win totals from a google sheet most likely.

This is what the Claude recommends for the post season site

How the site works:

Single index.html file hosted on GitHub Pages
Pulls live W-L records from ESPN's public API (no API key needed)
Conference tournament detection uses hardcoded per-team start dates
Google Sheet is no longer used for wins/losses — only the 64 team assignments + ESPN IDs matter
Schedule pulls from ESPN scoreboard with groups=50 to get all D1 games

Key things to update next year:

The 64 team assignments in the ST array (gambler, team name, ESPN ID, conference, tourney start date)
ESPN IDs if any teams change (look up at espn.com/mens-college-basketball/team/_/id/XXXX)
Conference tournament start dates from the annual schedule
The ncaaStart date (usually mid-March)

How to find ESPN team IDs:

Go to espn.com/mens-college-basketball/team/_/id/XXXX/team-name — the number in the URL is the ID

How to deploy:

Upload index.html to the repo
GitHub Pages serves it automatically from the main branch
