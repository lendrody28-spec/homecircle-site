"""For families & partners pages. Every number, hour and URL comes from
homecircle-plans/families-services.md (checked 4 Nov 2026). Imported by build.py."""
CHECKED = "Last checked: 4 Nov 2026"
NEW = "Last checked: 5 Nov 2026"

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
KIDS_SCARED = """<p class="fam-scared"><strong>If you're scared or in danger, call <a href="tel:000">000</a>. You can call Kids Helpline any time on <a href="tel:1800551800">1800 55 1800</a>.</strong></p>"""

SHARE = """<div class="card sage mt"><h2 class="mt0">Share this page</h2><p>Send it to someone you care about, or copy the link. Nothing is tracked.</p>
<button class="btn" type="button" id="fam-share">Share this page</button><p class="small" id="fam-share-status" role="status"></p></div>"""

AOD = "1800 250 015"
WITHDRAWAL_LINE = f'Withdrawal from alcohol or some medicines can be dangerous. Don\'t manage it at home alone. See a GP, or call the National Alcohol and Other Drug Hotline on <a href="tel:1800250015">{AOD}</a> (some state lines have set hours). Call <a href="tel:000">000</a> for a seizure, confusion or collapse.'

def withdrawal():
    return f"""<section class="card mt" id="withdrawal"><h2 class="mt0">Withdrawal warning signs and when to call 000</h2>
<p><strong>{WITHDRAWAL_LINE}</strong></p>
<p><strong>Call 000 straight away if they:</strong></p><ul><li>have a seizure (fit)</li><li>are confused or don't know where they are</li><li>collapse or can't be woken</li></ul>
<div class="btn-row"><a class="btn danger" href="tel:000">Call 000</a>{tel(AOD, "Call the AOD Hotline " + AOD)}<a class="btn ghost" href="overdose.html">What to do in an overdose</a></div>
<details class="more"><summary>More info</summary>
<p>When someone cuts down or stops alcohol or some drugs, their body can react badly. Don't try to manage it at home on your own.</p>
<p>The hotline is open 24/7 and puts you through to your state or territory's service. SA calls are answered 8.30am–10pm.</p>
<p>If opioids are involved, naloxone can reverse an overdose for a short time. It's free, with no prescription, at participating pharmacies and other approved sites.</p>
<div class="btn-row">{link("https://www.health.gov.au/our-work/take-home-naloxone-program/about-the-take-home-naloxone-program", "About take-home naloxone")}{link("https://www.health.gov.au/our-work/take-home-naloxone-program/where-to-access-naloxone", "Where to get naloxone")}</div>
</details><p class="small">{CHECKED}. HomeCircle is support, not medical care.</p></section>"""

def svc5(name, who, phone=None, hours=None, url=None, url_label="Open site"):
    return svc(name, who, phone, hours, url, url_label).replace(CHECKED, NEW)

def src(items):
    return '<p class="small"><strong>Sources:</strong> ' + "; ".join(f'<a href="{u}" rel="noopener">{n}</a>' for n, u in items) + f'. {NEW}.</p>'

def overdose():
    return f"""<section class="card mt" id="overdose"><h2 class="mt0">Think it's an overdose? Call 000</h2>
<p><strong>Call <a href="tel:000">000</a> straight away if they can't be woken, are breathing very slowly or not at all, or their lips or fingertips look blue. Stay with them and follow what the 000 operator tells you.</strong></p>
<div class="btn-row"><a class="btn danger" href="tel:000">Call 000</a></div>
<details class="more"><summary>More info</summary>
<p>If opioids might be involved, naloxone can reverse an overdose for a short time. The Australian Government's Take Home Naloxone program makes it free, with no prescription, from participating pharmacies and services. Ask a pharmacist how and when to use it. Always call 000 too, even if you have naloxone.</p>
<p>HomeCircle can't give medical instructions. Follow the 000 operator, a pharmacist or a doctor.</p>
<div class="btn-row"><a class="btn" href="overdose.html">What to do in an overdose</a>{link("https://www.health.gov.au/our-work/take-home-naloxone-program", "Take Home Naloxone program")}</div>
{src([("Australian Government Department of Health, Disability and Ageing: Take Home Naloxone program", "https://www.health.gov.au/our-work/take-home-naloxone-program")])}
</details></section>"""

def dv_aod(full=False):
    body = f"""<p><strong>Drinking or drugs never excuse violence.</strong> Violence is always the choice of the person using it, and it's never your fault. Your safety, and any children's safety, comes first.</p>
<p>If you're in danger now, call <a href="tel:000">000</a>. For advice any time, call 1800RESPECT on <a href="tel:1800737732">1800 737 732</a>.</p>
<p>Getting sober doesn't always stop the abuse. Please don't wait for them to stop drinking or using before you get help for yourself.</p>"""
    more = f"""<details class="more"><summary>More info</summary>
<p>Abuse can be physical, but it can also be threats, control over money, checking your phone, or cutting you off from friends and family.</p>
<p>Avoid raising their drinking or drug use when they're drunk, high or angry. If talking about it could make things more dangerous, talk to 1800RESPECT first.</p>
<p>Family support services, like Family Drug Support, can help with the drinking or drugs. For violence, a domestic and family violence service is the right place to start.</p>
{src([("1800RESPECT", "https://www.1800respect.org.au/"), ("eSafety Commissioner: Domestic violence", "https://www.esafety.gov.au/key-topics/domestic-family-violence")])}</details>"""
    if full:
        return f'<section class="card mt" id="dv-aod"><h2 class="mt0">When drinking or drugs and violence happen together</h2>{body}<div class="btn-row">{tel("1800 737 732", "Call 1800RESPECT 1800 737 732")}</div>{more}</section>'
    return f'<details class="card more mt" id="dv-aod"><summary><h2 class="mt0">When drinking or drugs and violence happen together</h2></summary>{body}<a class="btn" href="safety.html#dv-aod">Read more and find help</a></details>'

def safety_plan():
    return f"""<section class="card mt" id="plan"><h2 class="mt0">Safety planning and tech safety</h2>
<p>A safety plan is a plan for staying as safe as possible, whether you stay, are thinking of leaving, or have left. A 1800RESPECT counsellor or your state's line can make one with you.</p>
<p><strong>If you think your phone or accounts are being checked or tracked, use a phone or computer they can't get to, like a friend's phone or a library computer.</strong></p>
<div class="btn-row">{tel("1800 737 732", "Call 1800RESPECT 1800 737 732")}{link("https://www.1800respect.org.au/help-and-support/safety-planning", "1800RESPECT: safety planning")}</div>
<details class="more"><summary>More info</summary>
<p><strong>Things people often think about in a safety plan</strong> (a support worker can help you with what fits you):</p>
<ul><li>Who you can call, and a safe place you could go</li><li>Where you'd keep important things such as ID, medicines, keys and some money</li><li>A code word with someone you trust that means “I need help”</li><li>How to keep children safe, and what they should do in an emergency</li></ul>
<p>Risk can go up when someone confronts the person using violence, tries to leave, or after the relationship ends. That's why it helps to plan with a specialist before taking big steps.</p>
<p><strong>Tech safety.</strong> Phones, apps, smart devices, cars and shared accounts can be used to track or control someone. The eSafety Commissioner has advice on tech abuse, collecting evidence safely, and online safety planning. If it's safe, make a plan before changing passwords or removing apps, because sudden changes can alert the other person.</p>
<p>If you work and you're experiencing family and domestic violence, you can get 10 days of paid leave a year. This applies to all employees, including casuals.</p>
<div class="btn-row">{link("https://www.esafety.gov.au/key-topics/domestic-family-violence", "eSafety: domestic violence and tech abuse")}</div>
{src([("1800RESPECT: Safety planning", "https://www.1800respect.org.au/help-and-support/safety-planning"), ("eSafety Commissioner: Domestic violence", "https://www.esafety.gov.au/key-topics/domestic-family-violence"), ("Safe Steps", "https://www.safesteps.org.au/"), ("Fair Work Ombudsman: Family and domestic violence leave", "https://www.fairwork.gov.au/leave/family-and-domestic-violence-leave"), ("Fair Work Act 2009 (Cth) s 106B", "https://www.legislation.gov.au/C2009A00028/latest/text")])}
</details></section>"""

def look_after():
    return f"""<details class="card sage more mt" id="you"><summary><h2 class="mt0">Look after yourself</h2></summary>
<ul><li>You didn't cause it, you can't control it, and you can't fix it alone.</li><li>Sleep, eat and get outside when you can.</li><li>Keep up with friends and things you enjoy.</li><li>Talk to someone: a GP, a counsellor, or a family support group.</li></ul>
<h3>Signs you're burning out</h3><p>Always tired, on edge, can't stop worrying, cutting yourself off from people, or feeling hopeless. These are signs to get support for you, not signs you've failed.</p>
<h3>Setting boundaries</h3><p>A boundary is what <em>you</em> will do, not a rule for them. For example: “I won't lend money”, “I won't call your work for you”, or “I'll leave the room if you're drunk.” Say it calmly once, then follow through. Only set limits that are safe for you. If you're scared of how they'll react, talk to 1800RESPECT first.</p>
<p>Some family programs teach ways to stay connected while encouraging the person to get help, and to look after yourself at the same time. Family Drug Support and SMART Recovery Family &amp; Friends both run free support for families.</p>
<div class="grid g2">
{svc5("Family Drug Support Australia", "Support line, groups and courses for families and friends of people who use alcohol or other drugs.", "1300 368 186", "24 hours, 7 days", "https://www.fds.org.au/")}
{svc5("SMART Recovery Family &amp; Friends", "Free groups for people affected by someone else's alcohol, drug or gambling use. HomeCircle isn't part of SMART Recovery.", None, None, "https://smartrecoveryaustralia.com.au/family-friends/")}
</div>
{src([("Family Drug Support Australia", "https://www.fds.org.au/"), ("SMART Recovery Australia: Family &amp; Friends", "https://smartrecoveryaustralia.com.au/family-friends/")])}</details>"""

def kids_body():
    return f"""<p><a href="index.html">← For families &amp; partners</a></p>
<h1>For kids and teens: when a parent drinks or uses drugs</h1>
<section class="card sage" id="start"><h2 class="mt0">It's not your fault</h2>
<p>If your mum, dad or someone who looks after you drinks too much or uses drugs, you didn't cause it, and it's not your job to fix it. Lots of kids and teens go through this. You're not alone.</p></section>
<section class="card mt" id="now"><h2 class="mt0">If you're scared or someone is hurt</h2>
<p><strong>Call <a href="tel:000">000</a> if someone is hurt, won't wake up, or you're in danger.</strong> Go somewhere safe first if you can, like a neighbour's house.</p>
<div class="btn-row"><a class="btn danger" href="tel:000">Call 000</a></div></section>
<h2 class="mt">People you can talk to</h2>
<div class="grid g2">
{svc5("Kids Helpline", "Free counselling for anyone aged 5 to 25, any time, about anything. You can call or chat online.", "1800 55 1800", "24/7", "https://kidshelpline.com.au/")}
{svc5("eheadspace", "Online and phone support for young people aged 12 to 25.", "1800 650 890", "3pm to 10pm, every day", "https://www.headspace.org.au/")}
</div>
<details class="card more mt" id="feelings"><summary><h2 class="mt0">Feelings you might have</h2></summary>
<p>You might feel angry, sad, scared, embarrassed or worried. You might love them and be upset with them at the same time. All of these feelings are OK.</p>
<p>Some things that can help:</p>
<ul><li>Tell a trusted adult, like a relative, teacher or school counsellor.</li><li>Keep doing things you enjoy, like sport, music or seeing friends.</li><li>Write or draw how you feel.</li><li>Have a safe person and a safe place you can go to.</li></ul>
<p>When you talk to a counsellor or teacher, they'll try to help you stay safe. If they're worried you might be in danger, they may need to tell someone who can help. You can ask them about this first.</p></details>
<details class="card more mt" id="more-help"><summary><h2 class="mt0">More help for young people</h2></summary>
<p><strong>Alateen</strong> is a group for young people affected by someone else's drinking. It's part of Al-Anon Family Groups. HomeCircle isn't part of Al-Anon or Alateen.</p>
<div class="btn-row">{link("https://al-anon.org.au/", "Al-Anon and Alateen Australia")}</div>
<p><strong>COPMI</strong> (Children of Parents with a Mental Illness) is about a parent's <strong>mental illness</strong>, not drinking or drug use. It has information for kids and teens whose parent has a mental illness. For help with a parent's drinking or drugs, try Alateen or Kids Helpline.</p>
<div class="btn-row">{link("https://www.copmi.net.au/", "COPMI")}</div>
<p>If there's fighting or violence at home, it's not your fault. Kids Helpline can help you make a plan to stay safe.</p>
<div class="btn-row"><a class="btn" href="safety.html">Help with violence at home</a></div></details>
{src([("Kids Helpline", "https://kidshelpline.com.au/"), ("headspace", "https://www.headspace.org.au/"), ("Al-Anon Family Groups Australia", "https://al-anon.org.au/"), ("COPMI", "https://www.copmi.net.au/")])}"""

def groups():
    return f"""<details class="card more mt" id="groups"><summary><h2 class="mt0">Family meetings, support groups and counselling</h2></summary>
<p>You don't have to work this out alone. Family support groups are free meetings where people with a loved one who drinks, uses drugs or gambles share what helps. Counselling services can help the whole family talk.</p>
<p><strong>HomeCircle isn't part of these groups.</strong></p>
<div class="grid g2">
{svc("Family Drug Support Australia", "A support line and meetings for families and friends of people who use alcohol or other drugs, and for bereaved families.", "1300 368 186", "24 hours, 7 days", "https://www.fds.org.au/")}
{svc("Gam-Anon (listed on Gamblers Anonymous Australia's site)", "For families and friends of people with a gambling problem.", None, None, "https://gaaustralia.org.au/gam-anon/", extra='<p><a href="mailto:gam-anon@live.com.au">gam-anon@live.com.au</a></p>')}
{svc("Relationships Australia", "Counselling, mediation and family support for individuals, couples and families.", "1300 364 277", None, "https://relationships.org.au/")}
</div>
<!-- PLACEHOLDER: future gambling (GA) family content goes here. Hidden from visitors until written and checked. -->
</details>"""

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
<h2 class="mt">If you're experiencing violence</h2>
<div class="grid g2">
{svc("1800RESPECT", "Anyone affected by domestic, family or sexual violence, and people supporting them. National.", "1800 737 732", "24/7", "https://www.1800respect.org.au/")}
{svc("Kids Helpline", "Children and young people aged 5–25.", "1800 55 1800", "24/7", "https://kidshelpline.com.au/")}
{svc5("MensLine Australia", "Phone and online counselling for men, including men experiencing family or relationship problems.", "1300 78 99 78", None, "https://mensline.org.au/")}
{svc5("QLife", "Free, anonymous peer support for LGBTIQ+ people, including about relationships and family.", "1800 184 527", None, "https://qlife.org.au/")}
</div>
{safety_plan()}
{dv_aod(full=True)}
<div class="card mt" id="overdose-link"><h2 class="mt0">Worried someone has overdosed?</h2><p>Call <a href="tel:000">000</a> now. Then see what to do while you wait.</p><div class="btn-row"><a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="overdose.html">What to do in an overdose</a></div></div>
<h2 class="mt" id="change">Worried about your own behaviour?</h2>
<p>These services are for people who use violence or are worried they might, and for the people around them. If you're experiencing violence, use the services above instead.</p>
<div class="grid g2">
{svc("Men's Referral Service (No to Violence)", "For men worried about their own behaviour, and their family, friends and professionals.", "1300 766 491", "24 hours 7 days a week", "https://ntv.org.au/get-help/")}
</div>
<h2 class="mt">Find your state's line</h2><p>Tap your state or territory to see its line. The national lines above work everywhere.</p>
{states}
<div class="card mt"><h3>Northern Territory (whole territory)</h3><p>The NT Government doesn't list a single 24/7 NT line. It lists 1800RESPECT, NT Police and 000, plus regional services. In the NT, adults must tell police if they believe someone has been, or is likely to be, seriously hurt by domestic violence, or that someone's life or safety is under serious threat.</p>
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
GROUP = {"partner": ("Al-Anon Family Groups Australia", "Meetings for families and friends of people with a drinking problem.", "1300 252 666", "https://al-anon.org.au/"),
         "family": ("Al-Anon Family Groups Australia", "Meetings for families and friends of people with a drinking problem.", "1300 252 666", "https://al-anon.org.au/"),
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
{overdose()}
{groups()}
{look_after()}
{dv_aod()}
<details class="card more mt"><summary><h2 class="mt0">Worried about violence?</h2></summary><p>If you feel unsafe, there is help in every state and territory.</p><a class="btn" href="safety.html">Domestic and family violence help</a></details>
{legal()}"""

OD_SRC = [
    ("healthdirect: Drug overdose", "https://www.healthdirect.gov.au/healthy-living/alcohol-and-drugs/drug-overdose"),
    ("healthdirect: Accidental overdose of medicines", "https://www.healthdirect.gov.au/medicines/accidental-overdose-of-medicines"),
    ("healthdirect: Collapsing (DRSABCD)", "https://www.healthdirect.gov.au/collapsing"),
    ("healthdirect: GHB", "https://www.healthdirect.gov.au/healthy-living/alcohol-and-drugs/ghb"),
    ("healthdirect: How alcohol affects your health", "https://www.healthdirect.gov.au/healthy-living/alcohol-and-drugs/how-alcohol-affects-your-health"),
    ("St John Ambulance Australia: Recovery position fact sheet", "https://stjohn.org.au/assets/uploads/fact%20sheets/english/Fact%20sheets_recovery%20position.pdf"),
    ("St John Ambulance Australia: Accredited training courses", "https://stjohn.org.au/training/accredited-training-courses/"),
    ("ANZCOR Guideline 8: CPR", "https://www.anzcor.org/home/basic-life-support/guideline-8-cardiopulmonary-resuscitation-cpr/"),
    ("Australian Government: Take Home Naloxone program", "https://www.health.gov.au/our-work/take-home-naloxone-program"),
    ("Australian Government: Where to access naloxone", "https://www.health.gov.au/our-work/take-home-naloxone-program/where-to-access-naloxone"),
    ("Alcohol and Drug Foundation: Overdose and drug-related emergencies", "https://adf.org.au/insights/overdose/"),
    ("Alcohol and Drug Foundation: Alcohol", "https://adf.org.au/drug-facts/alcohol/"),
    ("Alcohol and Drug Foundation: GHB", "https://adf.org.au/drug-facts/ghb/"),
    ("Penington Institute: Overdose", "https://www.penington.org.au/overdose/"),
    ("Queensland Poisons Information Centre: Medicine or drug overdose", "https://www.poisonsinfo.health.qld.gov.au/medicine-or-drug-overdose"),
]

def overdose_body():
    return f"""<section class="card" id="call"><a class="btn danger fam-big" href="tel:000">Call 000 now</a>
<p><strong>Say it's an overdose. Ask for an ambulance. Stay with them and do what the 000 operator tells you.</strong></p>
<p>This is general first aid information, not medical training. Always follow the 000 operator.</p></section>
<p><a href="index.html">← For families &amp; partners</a></p>
<h1>What to do in an overdose</h1>
<section class="card mt" id="steps"><h2 class="mt0">What to do (DRSABCD)</h2>
<ol>
<li><strong>Danger.</strong> Make sure you, them and everyone nearby are safe.</li>
<li><strong>Response.</strong> Loudly say their name and squeeze their shoulder. If they don't respond, don't assume they're just asleep.</li>
<li><strong>Send for help.</strong> Call <a href="tel:000">000</a> and say it's an overdose. Don't leave them.</li>
<li><strong>Airway and Breathing.</strong> If they're breathing, roll them onto their side in the recovery position and stay with them.</li>
<li><strong>CPR.</strong> If they're not breathing normally, start CPR as the 000 operator tells you.</li>
<li><strong>Defibrillation.</strong> If someone can bring a defibrillator (AED), attach it and follow its voice prompts.</li>
<li><strong>Naloxone.</strong> If opioids might be involved and you have naloxone, use it as the packet or pharmacist instructs. It's free from participating pharmacies and services.</li>
<li><strong>Stay with them</strong> until the ambulance arrives.</li>
<li><strong>Tell the paramedics</strong> what they took, how much and when, if you know.</li>
</ol>
<details class="more"><summary>More info</summary>
<p><strong>Recovery position</strong> (St John Ambulance Australia): with them on their back, put their far arm out from their body and their near arm across their chest. Bend their near leg so the foot is on the floor. Roll them away from you onto their side, supporting their head and neck. Keep the bent knee on the ground so they don't roll onto their face, and put their hand under their chin to keep the airway open.</p>
<p>Open windows and loosen tight clothing so they get enough air.</p>
<p>Don't worry about getting in trouble for drug use. healthdirect says paramedics don't need to involve the police unless they feel in danger, and they're focused on saving lives.</p>
</details></section>
<section class="card mt" id="signs"><h2 class="mt0">Signs of an overdose</h2>
<p>They don't need to have every sign. If you're worried, call <a href="tel:000">000</a>.</p>
<details class="more"><summary>More info</summary>
<h3>Opioids (like heroin, oxycodone, codeine or fentanyl)</h3>
<ul><li>Can't be woken, or awake but can't respond</li><li>Slow, shallow or irregular breathing, or not breathing</li><li>Choking, gurgling or snoring sounds</li><li>Blue lips or fingertips</li><li>Pale, cool or clammy skin</li><li>Very small pupils</li></ul>
<h3>Alcohol poisoning</h3>
<ul><li>Slowed breathing</li><li>Confusion</li><li>Blurred vision</li><li>Nausea or vomiting</li><li>Passing out</li></ul>
<h3>Stimulants (like speed, ice, cocaine or MDMA)</h3>
<ul><li>Chest pain or a racing heartbeat</li><li>Difficulty breathing</li><li>Hot, flushed or sweaty skin</li><li>Severe agitation, paranoia, confusion or panic</li><li>Severe stomach pain</li><li>Seizures (fits)</li></ul>
<h3>GHB</h3>
<ul><li>Can't be woken</li><li>Confused, agitated or hallucinating</li><li>Sweating or vomiting</li><li>Slow or irregular breathing</li><li>Slow or irregular heartbeat</li><li>Seizures</li></ul>
</details></section>
<section class="card mt" id="dont"><h2 class="mt0">What not to do</h2>
<ul><li>Don't give them food or drink.</li><li>Don't make them vomit.</li><li>Don't leave them alone, or assume they're just sleeping it off.</li><li>Don't rely on a cold shower or coffee. They won't sober someone up.</li></ul></section>
<section class="card mt" id="after"><h2 class="mt0">Afterwards</h2>
<p><strong>They still need medical care, even if they wake up.</strong> Naloxone wears off, and they can overdose again. Always call 000, even if you've given naloxone.</p>
<details class="more"><summary>More info</summary>
<p>When they wake up, some people feel upset or irritable. Stay calm and keep them company until the ambulance arrives.</p>
<p>If you're worried someone has taken the wrong medicine or too much, but they're awake and well, call the Poisons Information Centre on <a href="tel:131126">13 11 26</a>, any time, anywhere in Australia. If they've collapsed or aren't breathing, call 000.</p>
<div class="btn-row">{tel("13 11 26", "Poisons 13 11 26")}</div></details></section>
<section class="card mt" id="naloxone"><h2 class="mt0">Free naloxone and first aid courses</h2>
<p>Naloxone is free, with no prescription, from participating pharmacies and services under the Australian Government's Take Home Naloxone program. Ask your pharmacist how to use it.</p>
<div class="btn-row">{link("https://www.health.gov.au/our-work/take-home-naloxone-program/where-to-access-naloxone", "Where to get free naloxone")}</div>
<details class="more"><summary>More info</summary>
<p>Naloxone only works on opioids. It won't reverse alcohol or other drug overdoses, but the Alcohol and Drug Foundation says it won't harm someone who hasn't taken an opioid.</p>
<p>A first aid course teaches you CPR and the recovery position hands-on. St John Ambulance runs nationally recognised courses in every state and territory.</p>
<div class="btn-row">{link("https://stjohn.org.au/training/accredited-training-courses/", "St John first aid courses")}{link("https://adf.org.au/insights/overdose/", "ADF: overdose")}</div></details></section>
{src(OD_SRC)}"""

def build(page, E):
    r_assets = '<script src="../assets/families.js" defer></script>'
    def P(path, title, desc, body):
        top, chk = TOP, CHECKED
        if path == "families/kids.html":
            top, chk = TOP.split('<p class="fam-scared">')[0] + KIDS_SCARED, NEW
        if path == "families/overdose.html":
            top, chk = TOP.split('<p class="fam-scared">')[0], NEW
        page(path, "families/index.html", title, desc, f'{top}\n{body}\n{SHARE}\n<p class="small mt">{chk}. HomeCircle is a free support app, not medical care, and isn\'t part of any service listed here.</p>{r_assets}')
    btns = "".join(f'<a class="btn fam-big" href="{k}.html">{v[0]}</a>' for k, v in WHO.items())
    P("families/index.html", "For families & partners: someone I love is addicted – HomeCircle",
      "Help for families, partners and friends of someone with an alcohol or drug problem in Australia.",
      f"""<h1>For families &amp; partners</h1><p class="lede">Someone you love is drinking or using drugs, and you want to help. Start here.</p>
<h2>Who are you worried about?</h2><div class="fam-choices">{btns}</div>
<div class="grid g2 mt"><a class="card tile" href="withdrawal.html"><div class="tbody"><h3>Supporting someone through withdrawal</h3><p>Warning signs and when to call 000.</p></div></a>
<a class="card tile" href="kids.html"><div class="tbody"><h3>For kids and teens</h3><p>When a parent drinks or uses drugs. It's not your fault.</p></div></a>
<a class="card tile" href="safety.html"><div class="tbody"><h3>Worried about violence at home?</h3><p>1800RESPECT and lines in every state.</p></div></a></div>""")
    for k, v in WHO.items():
        P(f"families/{k}.html", v[1] + " – HomeCircle", v[2], who_body(k))
    P("families/kids.html", "For kids and teens: when a parent drinks or uses drugs – HomeCircle",
      "For children and teens in Australia whose parent drinks or uses drugs: it's not your fault, and who to talk to.", kids_body())
    P("families/withdrawal.html", "Supporting someone through withdrawal – HomeCircle",
      "Withdrawal warning signs, when to call 000, and who to call for advice in Australia.",
      f'<p><a href="index.html">← For families &amp; partners</a></p><h1>Supporting someone through withdrawal</h1>{withdrawal()}')
    P("families/overdose.html", "What to do in an overdose – HomeCircle",
      "Signs of overdose and what to do: call 000, recovery position, CPR, naloxone. Australian first aid sources.", overdose_body())
    P("families/safety.html", "Domestic and family violence help for families – HomeCircle",
      "1800RESPECT, every state and territory domestic violence line, and the Men's Referral Service.",
      '<p><a href="index.html">← For families &amp; partners</a></p>' + dv_body())
