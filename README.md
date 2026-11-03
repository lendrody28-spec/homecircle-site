# HomeCircle website (homecircle.au)

Free website for the HomeCircle recovery support app (au.endrody.homecircle), served by GitHub Pages at https://homecircle.au. Static HTML, CSS and JavaScript only: no accounts, no cookies, no analytics, no trackers, no third-party scripts or fonts.

## Pages
- index.html – Home, with Upcoming events (from events.json)
- library.html and library/*.html – the app's Library (guides, breathing, meditation, body, fellowships, recovery books)
- twelve-steps.html – the 12 Steps with plain-language notes and the official aa.org link
- meditations.html – animated breathing guide and meditations
- meetings.html – meeting finder that reads the app's public feed in the browser
- help.html – helplines; support.html – contact and FAQs

Every page has a fixed "Get help now" button (000, Lifeline 13 11 14, Gambling Helpline, National Alcohol and Other Drug Hotline).

## Updating
- Content comes from the iOS app source: `python3 tools/extract_app_content.py /path/to/homecircle-ios > tools/app-content.json`
- Events: edit `events.json` (title, start, end, place, state, fellowship, organiser, source). Only add events from official AA or NA pages. Past events hide themselves.
- Rebuild pages: `python3 tools/build.py`, then check links: `python3 tools/check_links.py`

The Privacy Policy currently links to https://lendrody28-spec.github.io/homecircle/privacy.html (the version matching app 1.2.16). The 1.3.0 Privacy Policy and Terms of Use will be added here once 1.3.0 is submitted to Apple.

The app's meeting feed is served separately from lendrody28-spec/homecircle (gh-pages) at https://lendrody28-spec.github.io/homecircle/feed/au/index.json. Do not move it. This site only reads it.

© 2026 LJ Endrody (ABN 53 687 374 897)
