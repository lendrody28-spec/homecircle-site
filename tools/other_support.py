"""Other support pages. Hale review 20 Nov 2026: exact framing strings stay character-for-character."""

# Hale review, copied exactly.
OS_INTRO = "HomeCircle doesn't run, host or list these groups. We link to official finders and services so you can find support near you. HomeCircle is independent and isn't affiliated with or endorsed by any service we link to."
OS_UNDER18 = "If you're under 18, Kids Helpline is there any time on 1800 55 1800."
OS_QEXIT_NOTE = "Quick exit (Esc) takes you away from this page fast. It doesn't clear your browser history. A private window is safer."
OS_DANGER = "If you're in danger now, call 000."
OS_PLAN = "1800RESPECT can help you plan for your safety."
OS_CHILDREN = "Children can be affected by violence at home, even when it isn't aimed at them, including by seeing or hearing it. Support is available for children and for parents. 1800RESPECT explains more. Young people can call Kids Helpline any time on 1800 55 1800."
OS_TECH = "If someone may be checking your phone or computer, use a device they can't access. eSafety has more about tech-based abuse."
OS_WOMEN_GAP = "There isn't one national directory of women's groups. These finders can help."
OS_FAM_JS = '<script src="assets/families.js" defer></script>'

def other_support_top(danger=False):
    danger_p = f'<p class="fam-scared"><strong>{OS_DANGER}</strong></p>\n' if danger else ""
    respect = '<a class="btn" href="tel:1800737732">Call 1800RESPECT 1800 737 732</a>' if danger else ""
    return (
        '<div class="fam-strip" role="region" aria-label="Call for help now"><strong>Call for help now:</strong>\n'
        f'<a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="tel:131114">Lifeline 13 11 14</a>{respect}\n'
        '<button class="btn ghost fam-exit" type="button" id="quick-exit" aria-label="Quick exit, leaves this site">Quick exit, leaves this site<span class="small fam-esc"> (Esc)</span></button>\n'
        f'<span class="small fam-exit-note">{OS_QEXIT_NOTE}</span></div>\n'
        f"{danger_p}"
    )

def build(page):
    body = f"""{other_support_top()}
<h1>Other support</h1>
<p class="lede">Find grief support, community groups and domestic violence help through official finders and services.</p>
<p>{OS_INTRO}</p>
<p>{OS_UNDER18}</p>
<div class="btn-row"><a class="btn" href="tel:1800551800">Call Kids Helpline 1800 55 1800</a></div>
<nav class="card sage" aria-label="On this page">
<p class="mt0"><strong>On this page</strong></p>
<ul>
<li><a href="#grief">Grief counselling and grief support groups</a></li>
<li><a href="#mens-groups">Men's groups</a></li>
<li><a href="#womens-groups">Women's groups</a></li>
<li><a href="#lgbtq">LGBTQ+ groups</a></li>
<li><a href="#multicultural">Multicultural and migrant support</a></li>
<li><a href="#domestic-violence">Domestic violence</a></li>
</ul>
</nav>

<h2 id="grief">Grief counselling and grief support groups</h2>
<p><a href="https://griefline.org.au/get-help/" rel="noopener">Griefline</a> is now part of SANE Australia. Call <a href="tel:1300845745">1300 845 745</a> Monday to Friday, 10am-8pm (AEST/AEDT), about grief support and resources through SANE. Griefline's <a href="https://griefline.org.au/get-help/bereavement-support-groups/" rel="noopener">online bereavement groups</a> are for people aged 18+ living in Australia. They are not a local-area finder. Griefline says these groups are free.</p>
<div class="btn-row"><a class="btn" href="tel:1300845745">Call Griefline 1300 845 745</a><a class="btn ghost" href="https://griefline.org.au/get-help/" rel="noopener">Griefline</a></div>
<p>A Friend's Place, operated by the National Centre for Childhood Grief, provides counselling and group support for children, teens and their families. Parents can find out more on their site. Their site says specialist counselling for children and teens is free. Call <a href="tel:1300654556">1300 654 556</a>.</p>
<div class="btn-row"><a class="btn" href="tel:1300654556">Call 1300 654 556</a><a class="btn ghost" href="https://childhoodgrief.org.au/" rel="noopener">National Centre for Childhood Grief (A Friend's Place)</a></div>
<p><a href="https://www.grief.org.au/" rel="noopener">Grief Australia</a> (the Australian Centre for Grief and Bereavement) has <a href="https://www.grief.org.au/ga/ACGB/Bereavement_Support/Bereavement_Support.aspx" rel="noopener">bereavement counselling and support groups</a>. On that page the number is <a href="tel:0392652100" aria-label="Call Grief Australia, (03) 9265 2100">(03) 9265 2100</a>. Specialist bereavement support is funded by the Victorian Government and is free of charge to Victorians. It is not a national postcode finder.</p>
<p>You can also search for local support groups with <a href="https://www.healthdirect.gov.au/australian-health-services/all-services/support-groups/1239081000168107" rel="noopener">healthdirect's support groups finder</a> or the <a href="https://www.healthdirect.gov.au/australian-health-services" rel="noopener">Australian health services search</a>.</p>

<h2 id="mens-groups">Men's groups</h2>
<p>The <a href="https://mensshed.org/" rel="noopener">Australian Men's Shed Association</a> has a <a href="https://mensshed.org/find-a-shed/" rel="noopener">find a shed</a> tool to look up a shed near you. The <a href="https://www.health.gov.au/our-work/mens-sheds/about-mens-sheds" rel="noopener">Department of Health, Disability and Ageing page on men's sheds</a> lists the Association on <a href="tel:1300550009">1300 550 009</a>.</p>
<div class="btn-row"><a class="btn" href="tel:1300550009">Call Australian Men's Shed Association 1300 550 009</a><a class="btn ghost" href="https://mensshed.org/find-a-shed/" rel="noopener">Find a shed</a></div>
<p><a href="https://mensline.org.au/" rel="noopener">MensLine Australia</a> is a telephone and online counselling service for men, not a local men's group finder. MensLine says it offers free professional 24/7 telephone counselling. Call <a href="tel:1300789978">1300 78 99 78</a>.</p>
<div class="btn-row"><a class="btn" href="tel:1300789978">Call MensLine Australia 1300 78 99 78</a><a class="btn ghost" href="https://mensline.org.au/" rel="noopener">MensLine Australia</a></div>
<p><a href="https://www.relationships.org.au/support/" rel="noopener">Relationships Australia</a> has support services in each state and territory. To be connected to the nearest Relationships Australia, call <a href="tel:1300364277">1300 364 277</a>. Their services are for all members of the community.</p>
<p>healthdirect's support groups finder, linked above, can also be used to look for local groups.</p>

<h2 id="womens-groups">Women's groups</h2>
<p>{OS_WOMEN_GAP}</p>
<ul>
<li><a href="https://www.healthdirect.gov.au/australian-health-services/all-services/support-groups/1239081000168107" rel="noopener">healthdirect support groups finder</a></li>
<li><a href="https://www.healthdirect.gov.au/australian-health-services/all-services/women-s-health-clinic/1248691000168108" rel="noopener">healthdirect women's health clinic finder</a></li>
<li><a href="https://www.relationships.org.au/support/" rel="noopener">Relationships Australia</a>, including <a href="tel:1300364277">1300 364 277</a></li>
</ul>
<p>If you're worried about your safety, see <a href="other-support-domestic-violence.html">domestic violence support</a> and 1800RESPECT on <a href="tel:1800737732">1800 737 732</a>.</p>

<h2 id="lgbtq">LGBTQ+ groups</h2>
<p><a href="https://www.qlife.org.au/" rel="noopener">QLife</a> provides anonymous and free LGBTIQ+ peer support and referral. QLife phone and webchat are open from 3pm – 9pm every day. Call <a href="tel:1800184527">1800 184 527</a>. QLife is not a postcode map. <a href="https://www.qlife.org.au/resources/directory" rel="noopener">QDirectory</a> lists national and state organisations.</p>
<div class="btn-row"><a class="btn" href="tel:1800184527">Call QLife 1800 184 527</a><a class="btn ghost" href="https://qlife.org.au/get-help" rel="noopener">QLife get help</a><a class="btn ghost" href="https://www.qlife.org.au/resources/directory" rel="noopener">QDirectory</a></div>
<p><a href="https://www.lgbtiqhealth.org.au/" rel="noopener">LGBTIQ+ Health Australia</a> has an <a href="https://navigator.lgbtiqhealth.org.au/lgbti-supports" rel="noopener">LGBTI Supports Navigator</a> to find services.</p>
<p>The <a href="https://fullstop.org.au/get-help/our-services/rainbowviolenceandabusesupport" rel="noopener">Rainbow Sexual, Domestic and Family Violence Helpline</a>, from Full Stop Australia, is for anyone in Australia from LGBTQ+ communities who has experienced sexual, domestic or family violence, and for supporters. Call <a href="tel:1800497212">1800 497 212</a>.</p>
<div class="btn-row"><a class="btn" href="tel:1800497212">Call 1800 497 212</a></div>

<h2 id="multicultural">Multicultural and migrant support</h2>
<p><a href="https://www.tisnational.gov.au/" rel="noopener">TIS National</a> (Translating and Interpreting Service) is provided by the Department of Home Affairs. For immediate phone interpreting, call <a href="tel:131450">131 450</a>. TIS National says this is available 24 hours a day, every day of the year. See also the <a href="https://immi.homeaffairs.gov.au/settling-in-australia/settle-in-australia/language-services/tis-national" rel="noopener">Home Affairs page on TIS National</a> and <a href="https://www.tisnational.gov.au/en/Contact-us" rel="noopener">TIS National contact details</a>.</p>
<div class="btn-row"><a class="btn" href="tel:131450">Call TIS National 131 450</a></div>
<p>The Department of Home Affairs lists <a href="https://immi.homeaffairs.gov.au/settling-in-australia/sets-program/list-of-providers/sets-locations" rel="noopener">Settlement Engagement and Transition Support (SETS) providers</a>. There is also a <a href="https://immi.homeaffairs.gov.au/settlement-services-subsite/Pages/sets-program-overview.aspx" rel="noopener">SETS program overview</a>. HomeCircle doesn't list provider addresses.</p>

<h2 id="domestic-violence">Domestic violence</h2>
<p>{OS_DANGER}</p>
<p><a href="https://1800respect.org.au/" rel="noopener">1800RESPECT</a> is the national domestic, family and sexual violence counselling, information and support service. It is available for free, 24 hours a day, 7 days a week. Call <a href="tel:1800737732">1800 737 732</a>.</p>
<p>The Rainbow Sexual, Domestic and Family Violence Helpline is on <a href="tel:1800497212">1800 497 212</a>.</p>
<p>For types of abuse, effects on children, official help and safe-browsing notes, see <a href="other-support-domestic-violence.html">domestic violence support</a>.</p>
<div class="btn-row"><a class="btn" href="tel:000">Call 000</a><a class="btn" href="tel:1800737732">Call 1800RESPECT 1800 737 732</a><a class="btn" href="other-support-domestic-violence.html">Domestic violence support</a></div>
{OS_FAM_JS}"""
    page(
        "other-support.html",
        "other-support.html",
        "Other support – HomeCircle",
        "Find grief support, community groups and domestic violence help in Australia through official finders. HomeCircle doesn't run these groups.",
        body,
    )

    dv = f"""{other_support_top(danger=True)}
<h1>Domestic violence support</h1>
<p class="lede">{OS_DANGER}</p>
<p>{OS_INTRO}</p>
<p>{OS_UNDER18}</p>
<div class="btn-row"><a class="btn danger" href="tel:000">Call 000</a><a class="btn" href="tel:1800737732">Call 1800RESPECT 1800 737 732</a><a class="btn" href="tel:1800551800">Call Kids Helpline 1800 55 1800</a></div>
<p><a href="other-support.html">← Other support</a></p>

<h2 id="help">Get help</h2>
<p><a href="https://1800respect.org.au/" rel="noopener">1800RESPECT</a> is the national domestic, family and sexual violence counselling, information and support service. It is available for free, 24 hours a day, 7 days a week. Call <a href="tel:1800737732">1800 737 732</a>, or text 0458 737 732. 1800RESPECT also lists NRS: 1800 555 677 and Interpreter: 13 14 50.</p>
<p>{OS_PLAN}</p>
<div class="btn-row"><a class="btn" href="tel:1800737732">Call 1800RESPECT 1800 737 732</a><a class="btn ghost" href="https://1800respect.org.au/services" rel="noopener">1800RESPECT Service Directory</a><a class="btn ghost" href="https://1800respect.org.au/" rel="noopener">1800RESPECT website</a></div>
<p>Use the Service Directory on 1800RESPECT's site to find services. HomeCircle doesn't list addresses or safe-house locations, and doesn't map locations.</p>
<p>The <a href="https://fullstop.org.au/get-help/our-services/rainbowviolenceandabusesupport" rel="noopener">Rainbow Sexual, Domestic and Family Violence Helpline</a> is for anyone in Australia from LGBTQ+ communities who has experienced sexual, domestic or family violence, and for supporters. Call <a href="tel:1800497212">1800 497 212</a>.</p>
<div class="btn-row"><a class="btn" href="tel:1800497212">Call 1800 497 212</a></div>
<p><a href="https://www.servicesaustralia.gov.au/family-and-domestic-violence" rel="noopener">Services Australia</a> has information, referrals and support for people affected by family and domestic violence, including help with payments.</p>
<p><a href="https://www.ourwatch.org.au/help-and-support" rel="noopener">Our Watch's help and support page</a> points people to services. Our Watch is a prevention organisation, not a crisis line of its own.</p>
<p>State and territory lines are listed on our <a href="families/safety.html">families page about violence at home</a>.</p>

<h2 id="types">Types of abuse</h2>
<p>1800RESPECT describes domestic and family violence as a repeated pattern of behaviour that happens when one person in a relationship hurts another or makes them feel unsafe. Abuse doesn't have to involve physical violence. Read more on <a href="https://1800respect.org.au/violence-and-abuse/domestic-and-family-violence" rel="noopener">1800RESPECT's domestic and family violence page</a>.</p>
<p>1800RESPECT describes <a href="https://1800respect.org.au/violence-and-abuse/psychological-abuse" rel="noopener">psychological abuse</a> as when someone uses words or behaviours to make you question your feelings, memories, or perception of reality to control or isolate you.</p>
<p>1800RESPECT describes <a href="https://1800respect.org.au/violence-and-abuse/physical-abuse" rel="noopener">physical abuse</a> as when someone deliberately hurts or threatens to hurt any part of your body, or takes away your control over your body.</p>
<p>1800RESPECT describes <a href="https://1800respect.org.au/violence-and-abuse/financial-abuse" rel="noopener">financial abuse</a>, also known as economic abuse, as a form of domestic and family violence that often involves someone using money in ways that can hurt and control you.</p>
<p>1800RESPECT describes <a href="https://1800respect.org.au/coercive-control" rel="noopener">coercive control</a> as an underpinning dynamic of family and domestic violence, where a person uses patterns of abusive behaviours over time that create fear and deny liberty and autonomy. The <a href="https://www.ag.gov.au/families-and-marriage/publications/understanding-coercive-control-fact-sheets" rel="noopener">Attorney-General's Department has fact sheets on understanding coercive control</a>.</p>

<h2 id="children">Effects on children</h2>
<p>{OS_CHILDREN}</p>
<div class="btn-row"><a class="btn ghost" href="https://1800respect.org.au/violence-and-abuse/children-and-young-people/children-and-violence/impacts" rel="noopener">1800RESPECT: children and violence</a><a class="btn" href="tel:1800551800">Call Kids Helpline 1800 55 1800</a></div>

<h2 id="tech">Tech safety</h2>
<p>{OS_TECH}</p>
<div class="btn-row"><a class="btn ghost" href="https://www.esafety.gov.au/key-topics/domestic-family-violence" rel="noopener">eSafety: domestic violence</a><a class="btn ghost" href="https://www.esafety.gov.au/key-topics/tech-based-abuse/i-may-be-experiencing-it" rel="noopener">eSafety: I may be experiencing tech-based abuse</a></div>
<p>1800RESPECT also asks: <a href="https://1800respect.org.au/" rel="noopener">Are you worried someone will find out you visited this website?</a></p>
{OS_FAM_JS}"""
    page(
        "other-support-domestic-violence.html",
        "other-support.html",
        "Domestic violence support – HomeCircle",
        "1800RESPECT and official information on domestic and family violence, including support for children. If you're in danger now, call 000.",
        dv,
    )
