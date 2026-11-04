"""For families & partners pages. Every number, hour and URL comes from
homecircle-plans/families-services.md (checked 4 Nov 2026). Imported by build.py."""
CHECKED = "Last checked: 4 Nov 2026"

def tel(num, label=None):
    d = "".join(c for c in num if c.isdigit())
    return f'<a class="btn ghost" href="tel:{d}">{label or "Call " + num}</a>'

def link(url, label):
    return f'<a class="btn ghost" href="{url}" rel="noopener">{label}</a>'

def svc(name, who, phone=None, hours=None, url=None, url_label="Open site", extra=""):
    h = f'<p class="small"><strong>Hours:</strong> {hours}</p>' if hours else ""
    btns = (tel(phone) if phone else "") + (link(url, url_label) if url else "")
    return f'<div class="card"><h3>{name}</h3><p>{who}</p>{h}{extra}<div class="btn-row">{btns}</div><p class="small">{CHECKED}</p></div>'

TOP = """<div class="fam-strip" role="region" aria-label="Call for help now"><strong>Call for help now:</strong>
<a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="tel:131114">Lifeline 13 11 14</a>
<button class="btn ghost fam-exit" type="button" id="quick-exit" aria-label="Quick exit, leaves this site">Quick exit, leaves this site<span class="small fam-esc"> (Esc)</span></button>
<span class="small fam-exit-note">Quick exit won't clear your browser history. A private window is safer.</span></div>
<p class="fam-scared"><strong>If you're scared of them, call <a href="tel:000">000</a> or 1800RESPECT <a href="tel:1800737732">1800 737 732</a>.</strong></p>"""

SHARE = """<div class="card sage mt"><h2 class="mt0">Send this page to someone</h2><p>Share it, or copy the link. Nothing is tracked.</p>
<button class="btn" type="button" id="fam-share">Send this page to someone</button><p class="small" id="fam-share-status" role="status"></p></div>"""

AOD = "1800 250 015"
WITHDRAWAL_LINE = f'Withdrawal from alcohol or some medicines can be dangerous. Don\'t manage it at home alone. See a GP, or call the National Alcohol and Other Drug Hotline on <a href="tel:1800250015">{AOD}</a> (some state lines have set hours). Call <a href="tel:000">000</a> for a seizure, confusion or collapse.'

def withdrawal():
    return f"""<section class="card mt" id="withdrawal"><h2 class="mt0">Withdrawal warning signs and when to call 000</h2>
<p><strong>{WITHDRAWAL_LINE}</strong></p>
<p><strong>Call 000 straight away if they:</strong></p><ul><li>have a seizure (fit)</li><li>are confused or don't know where they are</li><li>collapse or can't be woken</li></ul>
<div class="btn-row"><a class="btn danger" href="tel:000">Call 000</a>{tel(AOD, "Call the AOD Hotline " + AOD)}</div>
<details class="more"><summary>More info</summary>
<p>When someone cuts down or stops alcohol or some drugs, their body can react badly. Don't try to manage it at home on your own.</p>
<p>The hotline is open 24/7 and puts you through to your state or territory's service. SA calls are answered 8.30am–10pm.</p>
<p>If opioids are involved, naloxone can reverse an overdose for a short time. It's free, with no prescription, at participating pharmacies and other approved sites.</p>
<div class="btn-row">{link("https://www.health.gov.au/our-work/take-home-naloxone-program/about-the-take-home-naloxone-program", "About take-home naloxone")}{link("https://www.health.gov.au/our-work/take-home-naloxone-program/where-to-access-naloxone", "Where to get naloxone")}</div>
</details><p class="small">{CHECKED}. HomeCircle is support, not medical care.</p></section>"""

def groups():
    return f"""<details class="card more mt" id="groups"><summary><h2 class="mt0">Family meetings, support groups and counselling</h2></summary>
<p>You don't have to work this out alone. Family support groups are free meetings where people with a loved one who drinks, uses drugs or gambles share what helps. Counselling services can help the whole family talk.</p>
<p><strong>HomeCircle isn't part of these groups.</strong></p>
<div class="grid g2">
{svc("Family Drug Support Australia", "A support line and meetings for families and friends of people who use alcohol or other drugs, and for bereaved families.", "1300 368 186", "24 hours, 7 days", "https://www.fds.org.au/")}
{svc("Al-Anon Family Groups Australia", "Meetings for families and friends of people with a drinking problem.", "1300 252 666", None, "https://www.al-anon.org.au/")}
{svc("Gam-Anon (listed on Gamblers Anonymous Australia's site)", "For families and friends of people with a gambling problem.", None, None, "https://gaaustralia.org.au/gam-anon/", extra='<p><a href="mailto:gam-anon@live.com.au">gam-anon@live.com.au</a></p>')}
{svc("Relationships Australia", "Counselling, mediation and family support for individuals, couples and families.", "1300 364 277", None, "https://relationships.org.au/")}
</div>
<!-- PLACEHOLDER: future gambling (GA) family content goes here. Hidden from visitors until written and checked. -->
</details>"""

def selfcare():
    return f"""<details class="card sage more mt" id="you"><summary><h2 class="mt0">Looking after yourself</h2></summary>
<ul><li>You didn't cause it, and you can't fix it alone.</li><li>Sleep, eat and get outside when you can.</li><li>Keep up with friends and things you enjoy.</li><li>Set limits that keep you safe, and stick to them.</li><li>Talk to someone: a GP, a counsellor, or a family support group.</li></ul>
<p class="small">{CHECKED}</p></details>"""

def legal():
    return f"""<details class="card more mt" id="legal"><summary><h2 class="mt0">Legal questions</h2></summary>
<p>Questions about protection orders, custody or making someone get treatment need proper legal advice. We can't give legal steps. Please don't secretly track someone's phone, location or messages. It can break the law, it can be a form of abuse, and it usually damages trust. Talk to a counsellor or Family Drug Support about other ways to help.</p>
<p><strong>Queensland:</strong> Legal Aid Queensland's Legal Information Line gives free legal information (Mon–Fri 8:30am–4:30pm AEST, except public holidays).</p>
<div class="btn-row">{tel("1300 65 11 88", "Legal Aid Qld 1300 65 11 88")}{link("https://www.legalaid.qld.gov.au/", "Legal Aid Qld site")}</div>
<p><strong>Other states and territories:</strong> National Legal Aid links to all 8 state and territory Legal Aid commissions, with a Find legal help page.</p>
<div class="btn-row">{link("https://www.nationallegalaid.org/", "National Legal Aid")}</div>
<p>For family and domestic violence, 1800RESPECT can help any time on <a href="tel:1800737732">1800 737 732</a>.</p>
<p>Young people can call Kids Helpline any time on <a href="tel:1800551800">1800 55 1800</a>.</p>
<p class="small">{CHECKED}</p></details>"""

DV_STATES = [
    ("Queensland", "DVConnect Womensline", "Anyone in Queensland experiencing domestic or family violence.", "1800 811 811", "24 hours, 7 days", "https://www.dvconnect.org/womensline/"),
    ("Queensland", "DVConnect Mensline", "Men in Queensland experiencing DFV, or wanting to change their own abusive behaviour.", "1800 600 636", "9am to midnight, 7 days (not 24/7)", "https://www.dvconnect.org/mensline/"),
    ("Victoria", "Safe Steps Family Violence Response Centre", "Anyone in Victoria experiencing family or domestic violence.", "1800 015 188", "24/7", "https://www.safesteps.org.au/"),
    ("New South Wales", "NSW Domestic Violence Line", "Women experiencing domestic violence in NSW (calls answered by female caseworkers).", "1800 65 64 63", "24/7", "https://dcj.nsw.gov.au/children-and-families/family-domestic-and-sexual-violence/domestic--family-and-sexual-violence-support-contacts/nsw-domestic-violence-line.html"),
    ("South Australia", "Domestic Violence Crisis Line", "Women and children in SA experiencing domestic or family violence. Run by Women's Safety Services SA.", "1800 800 098", "24/7", "https://womenssafetyservices.com.au/"),
    ("Western Australia", "Women's Domestic Violence Helpline", "Western Australians, including women with or without children, experiencing FDV (includes refuge referrals).", "1800 007 339", "24 hours, 7 days", "https://www.wa.gov.au/organisation/department-of-communities/family-and-domestic-violence-helplines-and-support-services"),
    ("Western Australia", "Men's Domestic Violence Helpline", "Men in WA concerned about their own violent or abusive behaviour, and male victims of FDV.", "1800 000 599", "24 hours, 7 days", "https://www.wa.gov.au/service/community-services/community-support/mens-domestic-violence-helpline"),
    ("Tasmania", "Family Violence Response and Referral Line (Safe at Home)", "Anyone in Tasmania affected by family violence.", "1800 633 937", "24 hours, 7 days", "https://www.safeathome.tas.gov.au/"),
    ("ACT", "Domestic Violence Crisis Service", "People in the ACT affected by domestic and family violence.", "02 62 800 900", "24/7 crisis line", "https://dvcs.org.au/"),
    ("Northern Territory", "Dawn House Inc. (Darwin)", "Shelter, counselling and outreach for women and children in Greater Darwin experiencing DFV.", "08 8945 1388", None, "https://nt.gov.au/law/crime/domestic-and-family-violence"),
]

def dv_body():
    states = "".join(f'<details class="card state"><summary><h3>{st}: {n}</h3></summary>{svc(n, w, p, h, u)}</details>' for st, n, w, p, h, u in DV_STATES)
    return f"""<h1>Worried about violence at home?</h1>
<p class="lede">If someone you love is drinking or using, and you feel unsafe, you deserve help. You can call any of these services.</p>
<div class="grid g2">
{svc("1800RESPECT", "Anyone affected by domestic, family or sexual violence, and people supporting them. National.", "1800 737 732", "24/7", "https://www.1800respect.org.au/")}
{svc("Kids Helpline", "Children and young people aged 5–25.", "1800 55 1800", "24/7", "https://kidshelpline.com.au/")}
{svc("Men's Referral Service (No to Violence)", "For men worried about their own behaviour, and their family, friends and professionals.", "1300 766 491", "24 hours 7 days a week", "https://ntv.org.au/get-help/")}
</div>
<h2 class="mt">Find your state's line</h2><p>Tap your state or territory to see its line. The national lines above work everywhere.</p>
{states}
<div class="card mt"><h3>Northern Territory (whole territory)</h3><p>The NT Government doesn't list a single 24/7 NT line. It lists 1800RESPECT, NT Police and 000, plus regional services. Under NT law, everyone must report domestic and family violence to police.</p>
<div class="btn-row">{tel("1800 737 732", "1800RESPECT 1800 737 732")}{tel("131 444", "NT Police 131 444")}{link("https://nt.gov.au/law/crime/domestic-and-family-violence", "NT Government DFV page")}</div><p class="small">{CHECKED}</p></div>
{legal()}"""

WHO = {
 "partner": ("My partner", "My partner is addicted, what can I do?", "Help when your partner drinks, uses drugs or gambles: what to say, warning signs and where to get support.",
   "Your partner's drinking or drug use can change the whole home. It's not your fault, and you can't make them stop. But you can look after yourself and help them find support.",
   ["“I love you and I'm worried about you.”", "“I've noticed you're drinking more. Can we talk?”", "“I'll come with you to the GP if you want.”"],
   ["Blaming or name-calling", "Talking while they're drunk or high", "Covering for them or making excuses", "Threats you won't carry out"]),
 "child": ("My child", "My child is using drugs or drinking, how can I help?", "Help for parents worried about a son or daughter's drinking or drug use.",
   "Finding out your child is drinking or using drugs is scary. Many parents feel this. Staying calm and keeping the door open matters most.",
   ["“I'm here for you, no matter what.”", "“Can you help me understand what's going on?”", "“Let's find someone to talk to together.”"],
   ["Yelling or shaming", "Searching their phone or messages", "Talking when they're drunk or high", "Giving up on them"]),
 "family": ("A parent or family member", "My parent or family member is addicted, what can I do?", "Help when a mum, dad, brother, sister or other relative has a drinking or drug problem.",
   "When a parent or relative drinks or uses drugs, it can affect everyone. You're allowed to have feelings about it, and you're allowed to get help for you.",
   ["“I care about you and I'm worried.”", "“I miss how things used to be.”", "“Would you talk to a GP?”"],
   ["Blaming yourself", "Arguing when they're drunk or high", "Keeping it a secret if you feel unsafe", "Trying to fix it on your own"]),
 "friend": ("A friend", "My friend has a drug or alcohol problem, how can I help?", "How to support a friend who drinks or uses drugs too much.",
   "Being a good friend doesn't mean fixing their problem. Listening, staying in touch and pointing them to support can help a lot.",
   ["“I've noticed you don't seem okay. Want to talk?”", "“I'm not judging you.”", "“I can help you find someone to call.”"],
   ["Lecturing or judging", "Joining in to keep the peace", "Promising to keep a secret if they're in danger", "Gossiping about them"]),
}

START = {
 "partner": "Living with a partner who drinks or uses can wear you down. You can't make them stop, but you can keep yourself safe and get support for you both.",
 "child": "If your child is drinking or using drugs, stay calm and keep talking. Parents and families can call for advice any time, day or night.",
 "family": "When a parent or relative drinks or uses, it affects the whole family. It's not your fault, and you're allowed to get help for you.",
 "friend": "You don't have to fix your friend's problem. Listening, staying in touch and pointing them to support really helps.",
}
GROUP = {"partner": ("Al-Anon Family Groups Australia", "Meetings for families and friends of people with a drinking problem.", "1300 252 666", "https://www.al-anon.org.au/"),
         "family": ("Al-Anon Family Groups Australia", "Meetings for families and friends of people with a drinking problem.", "1300 252 666", "https://www.al-anon.org.au/"),
         "child": ("Al-Anon Family Groups Australia", "For people affected by someone else's drinking.", "1300 252 666", "https://al-anon.org.au/"),
         "friend": ("Al-Anon Family Groups Australia", "For people affected by someone else's drinking.", "1300 252 666", "https://al-anon.org.au/")}

def who_body(key):
    btn, h1, _, intro, say, dont = WHO[key]
    s = "".join(f"<li>{x}</li>" for x in say); d = "".join(f"<li>{x}</li>" for x in dont)
    g = GROUP[key]
    return f"""<p><a href="index.html">← Who are you worried about?</a></p>
<h1>{h1}</h1>
<section class="card sage" id="start"><h2 class="mt0">Start here</h2><p>{START[key]}</p></section>
<h2 class="mt">3 places to call or visit</h2>
<div class="grid g3">
{svc("Family Drug Support Australia", "Support for families and friends of people who use alcohol or other drugs.", "1300 368 186", "24 hours, 7 days", "https://www.fds.org.au/")}
{svc("National Alcohol and Other Drug Hotline", "Advice about someone's alcohol or drug use. SA calls are answered 8.30am–10pm.", "1800 250 015", "24/7 nationally; some state lines have set hours (SA 8.30am–10pm).", "https://www.health.gov.au/contacts/national-alcohol-and-other-drug-hotline")}
{svc(g[0], g[1] + " HomeCircle isn't part of this group.", g[2], None, g[3], "Find a meeting" if not g[2] else "Open site")}
</div>
<details class="card more mt" id="understand"><summary><h2 class="mt0">Understanding addiction (for them and for you)</h2></summary>
<p>{intro}</p>
<p>Addiction is a health problem, not a choice someone makes every day. People can and do recover, but it often takes time and more than one try.</p>
<p>For you: worry, anger, guilt and sadness are all normal. You matter too.</p></details>
<details class="card more mt" id="say"><summary><h2 class="mt0">What to say and what not to say</h2></summary>
<p>Pick a calm time when they're sober. Use “I” words and keep it short.</p>
<div class="grid g2"><div><h3>Try saying</h3><ul>{s}</ul></div><div><h3>Try not to</h3><ul>{d}</ul></div></div></details>
<details class="card more mt" id="withdrawal"><summary><h2 class="mt0">Withdrawal warning signs and when to call 000</h2></summary>
<p>Call <a href="tel:000">000</a> for a seizure, confusion or collapse.</p><p><a href="withdrawal.html">Supporting someone through withdrawal</a></p></details>
{groups()}
{selfcare()}
<details class="card more mt"><summary><h2 class="mt0">Worried about violence?</h2></summary><p>If you feel unsafe, there is help in every state and territory.</p><a class="btn" href="safety.html">Domestic and family violence help</a></details>
{legal()}"""

def build(page, E):
    r_assets = '<script src="../assets/families.js" defer></script>'
    def P(path, title, desc, body):
        page(path, "families/index.html", title, desc, f'{TOP}\n{body}\n{SHARE}\n<p class="small mt">{CHECKED}. HomeCircle is a free support app, not medical care, and isn\'t part of any service listed here.</p>{r_assets}')
    btns = "".join(f'<a class="btn fam-big" href="{k}.html">{v[0]}</a>' for k, v in WHO.items())
    P("families/index.html", "For families & partners: someone I love is addicted – HomeCircle",
      "Help for families, partners and friends of someone with an alcohol or drug problem in Australia.",
      f"""<h1>For families &amp; partners</h1><p class="lede">Someone you love is drinking or using drugs, and you want to help. Start here.</p>
<h2>Who are you worried about?</h2><div class="fam-choices">{btns}</div>
<div class="grid g2 mt"><a class="card tile" href="withdrawal.html"><div class="tbody"><h3>Supporting someone through withdrawal</h3><p>Warning signs and when to call 000.</p></div></a>
<a class="card tile" href="safety.html"><div class="tbody"><h3>Worried about violence at home?</h3><p>1800RESPECT and lines in every state.</p></div></a></div>""")
    for k, v in WHO.items():
        P(f"families/{k}.html", v[1] + " – HomeCircle", v[2], who_body(k))
    P("families/withdrawal.html", "Supporting someone through withdrawal – HomeCircle",
      "Withdrawal warning signs, when to call 000, and who to call for advice in Australia.",
      f'<p><a href="index.html">← For families &amp; partners</a></p><h1>Supporting someone through withdrawal</h1>{withdrawal()}')
    P("families/safety.html", "Domestic and family violence help for families – HomeCircle",
      "1800RESPECT, every state and territory domestic violence line, and the Men's Referral Service.",
      '<p><a href="index.html">← For families &amp; partners</a></p>' + dv_body())
