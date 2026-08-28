#!/usr/bin/env python3
"""Generate the Mongbotics multi-page site. Plain HTML out, no build step needed after this."""
import os, re

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the site folder, one level up


def css_version():
    """Short hash of styles.css.

    Linked as styles.css?v=<hash>, the browser cannot serve a stale stylesheet:
    edit the CSS and the URL changes with it. Without this, Chrome guesses an
    expiry and keeps the old file, which has repeatedly made correct CSS edits
    look like they did nothing.
    """
    import hashlib
    path = os.path.join(OUT, "styles.css")
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


CSS = "styles.css?v=" + css_version()

# The Product dropdown. "Overview" is the old Technology page, which is how
# MongChain and Soul.md stay reachable from the nav at all.
PRODUCTS = [("technology.html", "Overview"), ("mongbot.html", "MongBot"),
            ("mongcore.html", "MongCore"), ("mongmarket.html", "MongMarket")]

PRODUCT_PAGES = {"technology.html", "mongbot.html", "mongcore.html", "mongmarket.html"}


def head(title, desc, page):
    items = "\n".join(
        '          <a href="%s"%s>%s</a>' % (h, ' class="active"' if h == page else '', t)
        for h, t in PRODUCTS)
    on_product = page in PRODUCT_PAGES
    links = '''        <a href="index.html"%s>Home</a>
        <div class="menu">
          <button type="button" class="menuBtn%s" aria-expanded="false" aria-controls="productMenu">
            Product <span class="caret" aria-hidden="true">&#9662;</span>
          </button>
          <div class="menuList" id="productMenu">
            <div class="menuInner">
%s
            </div>
          </div>
        </div>
        <a href="about.html"%s>About Us</a>''' % (
        ' class="active"' if page == "index.html" else "",
        " active" if on_product else "",
        items,
        ' class="active"' if page == "about.html" else "")
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:image" content="og.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{CSS}">
</head>
<body>
<main>

  <nav class="nav">
    <a class="brand" href="index.html"><span class="mark">M</span>Mongbotics</a>
    <div class="links">
{links}
    </div>
    <a class="navCta" href="about.html#contact">Build with us <span aria-hidden="true">&#8599;</span></a>
  </nav>
'''


def page_hero(img, alt, eyebrow, h1, video=None, crop=None):
    """crop="low" keeps the bottom of the frame, for a subject standing low in it."""
    # a background video needs muted + playsinline or iOS will not autoplay it,
    # and a poster so there is something to look at while it loads or if it fails
    media = (f'''<video class="heroVideo" autoplay muted loop playsinline
             poster="{img}" aria-label="{alt}">
        <source src="{video}" type="video/mp4">
        <img src="{img}" alt="{alt}">
      </video>''' if video else f'<img src="{img}" alt="{alt}">')
    return f'''
  <section class="pageHero{" videoHero" if video else ""}{" cropLow" if crop == "low" else ""}">
    {media}
    <div class="heroShade"></div>
    <div class="pageHeroCopy">
      <p class="eyebrow"><span></span> {eyebrow}</p>
      <h1>{h1}</h1>
    </div>
  </section>
'''


def page_intro(tag, text):
    return f'''
  <section class="pageIntro">
    <p class="sectionTag">{tag}</p>
    <p>{text}</p>
  </section>
'''


def manifesto(tag, h2, text):
    return f'''
  <section class="manifesto">
    <p class="sectionTag">{tag}</p>
    <h2>{h2}</h2>
    <p class="manifestoBody">{text}</p>
  </section>
'''


def page_next(a_href, a_label, a_title, b_href, b_label, b_title):
    return f'''
  <nav class="pageNext">
    <a href="{a_href}"><span>{a_label}</span><strong>{a_title}</strong></a>
    <a href="{b_href}"><span>{b_label}</span><strong>{b_title}</strong></a>
  </nav>
'''


NAV_SCRIPT = '''<script>
// The dropdown opens on hover and on keyboard focus through CSS alone. This
// adds click, which is what a trackpad tap and a touch device actually send,
// plus Escape and click-outside to close it again.
(function () {
  var menu = document.querySelector(".menu");
  if (!menu) return;
  var btn = menu.querySelector(".menuBtn");

  function close() {
    menu.classList.remove("open");
    btn.setAttribute("aria-expanded", "false");
  }

  btn.addEventListener("click", function (e) {
    e.stopPropagation();
    var open = menu.classList.toggle("open");
    btn.setAttribute("aria-expanded", open ? "true" : "false");
  });

  document.addEventListener("click", function (e) {
    if (!menu.contains(e.target)) close();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      close();
      btn.focus();
    }
  });
})();
</script>
'''


def footer(scripts=NAV_SCRIPT):
    return '''
</main>
<footer>
  <a class="brand" href="index.html"><span class="mark">M</span>Mongbotics</a>
  <p>Robots with identity. Ownership with proof.<br>A network built for everyone.</p>
  <div>
    <a href="technology.html">Technology</a>
    <a href="mongbot.html">MongBot</a>
    <a href="mongcore.html">MongCore</a>
    <a href="mongmarket.html">MongMarket</a>
    <a href="about.html">About Us</a>
  </div>
  <span>&#169; 2026 Mongbotics</span>
</footer>
''' + scripts + '''</body>
</html>
'''

pages = {}

# ----------------------------------------------------------------- home ---
pages["index.html"] = (
    head("Mongbotics | Autonomous delivery, owned by anyone",
         "Thailand's first decentralized robotics company. The control, identity, and ownership layer for autonomous robots.",
         "index.html")
    + '''
  <section id="top" class="hero">
    <img class="heroImage" src="images/construction.jpg" alt="A MongBot autonomous robot operating at night">
    <div class="heroShade"></div>
    <div class="heroCopy">
      <p class="eyebrow"><span></span> Thailand&#8217;s first decentralized robotics company</p>
      <h1>Robots with<br><em>soul.</em></h1>
      <div class="actions">
        <a class="primary" href="#ecosystem">Discover the ecosystem <span aria-hidden="true">&#8599;</span></a>
        <a class="textLink" href="mongbot.html">Meet MongBot <span>&#8595;</span></a>
      </div>
    </div>
    <div class="heroMeta">
      <span>01</span>
      <p>Autonomous hardware<br>Decentralized identity<br>Open robot economy</p>
    </div>
  </section>
'''
    + '''
  <section class="vision">
    <div class="visionCopy">
      <p class="sectionTag">The thesis</p>
      <h2>Autonomous robots should be as <span>personal and accessible</span> as smartphones.</h2>
      <p class="visionBody">We are building the infrastructure for a world where robots live alongside people, earn a character of their own, and carry it with them from one owner to the next.</p>
    </div>
    <img src="images/vision.jpg" alt="A MongBot robot working inside a modern office building">
  </section>
'''
    + '''
  <section id="ecosystem" class="ecosystem">
    <div class="sectionHead">
      <p class="sectionTag">The Mongbotics ecosystem</p>
      <h2>One stack.<br>Four connected layers.</h2>
    </div>
    <div class="productGrid">
      <article class="product featured">
        <span class="number">01</span>
        <div>
          <h3>MongBot</h3>
          <p>Our last-mile autonomous delivery robot, engineered for indoor and outdoor operations.</p>
        </div>
        <a href="mongbot.html" aria-label="Explore MongBot">&#8599;</a>
      </article>
      <article class="product">
        <span class="number">02</span>
        <div>
          <h3>MongCore</h3>
          <p>One intuitive application to onboard, monitor, command, and manage supported robots.</p>
        </div>
        <a href="mongcore.html" aria-label="Explore MongCore">&#8599;</a>
      </article>
      <article class="product">
        <span class="number">03</span>
        <div>
          <h3>MongChain</h3>
          <p>Permanent on-chain identity, history, and verifiable ownership for every robot.</p>
        </div>
        <a href="technology.html" aria-label="Explore MongChain">&#8599;</a>
      </article>
      <article class="product">
        <span class="number">04</span>
        <div>
          <h3>MongMarket</h3>
          <p>A peer-to-peer network where anyone can request a robot and owners can put theirs to work.</p>
        </div>
        <a href="mongmarket.html" aria-label="Explore MongMarket">&#8599;</a>
      </article>
    </div>
  </section>

  <section class="network">
    <div class="networkCopy">
      <p class="sectionTag">A network for the physical world</p>
      <h2>One robot.<br>Endless possibilities.</h2>
      <p class="networkTags">Hotels &#183; Hospitals &#183; Campuses &#183; Communities &#183; Factories &#183; Offices &#183; Retail &#183; Public roads</p>
    </div>
    <img src="images/network.jpg" alt="An isometric city showing MongBot delivering to hotels, hospitals, campuses, residential communities, offices, convenience stores and public roads">
  </section>

  <section class="cta">
    <p class="sectionTag">The autonomous future is arriving</p>
    <h2>Let&#8217;s build it<br>together.</h2>
    <a href="about.html#contact">Partner with Mongbotics <span aria-hidden="true">&#8599;</span></a>
  </section>
'''
    + footer())

# ----------------------------------------------------------- technology ---
pages["technology.html"] = (
    head("Technology | Mongbotics",
         "MongChain gives every robot a permanent on-chain identity: its Soul.md, ownership history, and verifiable record.",
         "technology.html")
    + page_hero("images/technology-hero.jpg",
                "A MongBot robot at night, its LiDAR scan, depth camera and on-chain network links visualised around it",
                "MongChain / Soul.md",
                "Built as a machine.<br>Loved as a <em>friend.</em>")
    + page_intro("Robot Identity",
                 "Every robot carries a Soul.md, a permanent on-chain record of its identity, personality, and history. As it works, that history grows with it, and it stays who it is, no matter who owns it next.")
    + '''
  <section class="soulFile">
    <div>
      <p class="sectionTag">MongChain / Soul.md</p>
      <h2>Every robot gets a permanent life story.</h2>
      <p class="lead">A robot&#8217;s Soul is its persistent digital identity: an auditable record that grows with every owner, task, service, and experience.</p>
    </div>
    <div class="soulCard">
      <div class="bar"><b>Soul.md</b><span>On-chain &#183; permanent</span></div>
      <div class="soulRow"><i>01</i><span><em>identity</em>: who it is</span></div>
      <div class="soulRow"><i>02</i><span><em>ownership history</em>: every owner it has had</span></div>
      <div class="soulRow"><i>03</i><span><em>job history</em>: the work it has done</span></div>
      <div class="soulRow"><i>04</i><span><em>service history</em>: how it has been maintained</span></div>
      <div class="soulRow"><i>05</i><span><em>performance data</em>: how well it works</span></div>
      <div class="soulRow"><i>06</i><span><em>ratings</em>: how it is rated</span></div>
      <div class="soulRow"><i>07</i><span><em>personality attributes</em>: the character it keeps</span></div>
      <p class="soulNote">Stored on the blockchain, not a company server. It cannot be edited, deleted, or faked.</p>
    </div>
  </section>

  <section class="ownRule">
    <p class="sectionTag">Verifiable ownership and control</p>
    <h2>The token is the key to the robot.</h2>
    <div class="ownStep">
      <b>01</b><h3>Tokenized</h3>
      <p>Every robot is tokenized as a Real World Asset (RWA), creating a permanent digital identity linked to the physical robot.</p>
    </div>
    <div class="ownStep">
      <b>02</b><h3>Controlled</h3>
      <p>The RWA token represents ownership and determines who can access the robot&#8217;s control, data, and management systems.</p>
    </div>
    <div class="ownStep">
      <b>03</b><h3>Transferred</h3>
      <p>If an owner sells or transfers a robot, the RWA token must also be transferred to the new owner&#8217;s control application in order for them to operate the robot.</p>
    </div>
  </section>
'''
    + manifesto("What is Soul.md",
                "A permanent digital <span>identity.</span>",
                "Soul.md is a robot&#8217;s permanent digital identity, stored on the blockchain: its ownership history, work, performance, and personality, for life. It is tied to an on-chain token, a Real World Asset (RWA), that proves ownership. Whoever holds the token controls the robot, and when it is sold or transferred, the token, and its Soul, goes with it.")
    + page_next("mongbot.html", "Next", "MongBot", "mongcore.html", "Also see", "MongCore")
    + footer())

# -------------------------------------------------------------- mongbot ---
pages["mongbot.html"] = (
    head("MongBot | Mongbotics",
         "MongBot is our last-mile autonomous delivery robot, engineered for indoor and outdoor operations.",
         "mongbot.html")
    + page_hero("images/mongbot-hero.jpg",
                "A MongBot robot on a wet city street at night, city lights reflected on the road",
                "Meet MongBot",
                "Built to move through<br>the <em>real world.</em>")
    + page_intro("MongBot / 01",
                 "Designed for residential communities, commercial districts, office buildings, campuses, and controlled public roads.")
    + '''
  <section class="specBuild">
    <div class="specRail">
      <p class="sectionTag">Detailed specifications</p>
      <h2>Engineered for the long shift.</h2>
      <p>Every number here comes from the production platform we build on with our hardware partners.</p>
      <div class="specRow"><span>Recommended payload</span><strong>50 kg</strong></div>
      <div class="specRow"><span>Maximum static load</span><strong>200 kg</strong></div>
      <div class="specRow"><span>Maximum speed</span><strong>2.5 m/s</strong></div>
      <div class="specRow"><span>Maximum climb</span><strong>30&#176;</strong></div>
      <div class="specRow"><span>Operating time</span><strong>12&#8211;15 h</strong></div>
      <div class="specRow"><span>Full charge</span><strong>3 h</strong></div>
      <div class="specRow"><span>Obstacle clearance</span><strong>&lt; 3 cm</strong></div>
      <div class="specRow"><span>Battery type</span><strong>LiFePO&#8324;</strong></div>
      <p class="specDim">L 75 cm &#215; W 56 cm &#183; customizable height</p>
    </div>
    <div class="specShots">
      <figure>
        <img src="images/features/house.jpg" alt="MongBot delivering to a residential doorway">
        <figcaption>Residential communities</figcaption>
      </figure>
      <figure>
        <img src="images/features/metro.jpg" alt="MongBot operating beside a metro line">
        <figcaption>Controlled public roads</figcaption>
      </figure>
    </div>
  </section>

  <section class="sense">
    <div>
      <p class="sectionTag">How it sees</p>
      <h2>Four sensor systems, always on.</h2>
    </div>
    <div class="senseList">
      <div><i>01</i><span>3D LiDAR</span></div>
      <div><i>02</i><span>Infrared wide-angle camera</span></div>
      <div><i>03</i><span>3D depth camera</span></div>
      <div><i>04</i><span>4&#215; ultrasonic sensors</span></div>
    </div>
    <img class="senseDiagram" src="images/features/specs.jpg" alt="MongBot sensor layout: 3D LiDAR, infrared wide-angle camera, 3D depth camera and bumper bar">
  </section>

  <section class="network">
    <div class="networkCopy">
      <p class="sectionTag">Where it operates</p>
      <h2>Indoors, outdoors,<br>and everywhere between.</h2>
      <p class="networkTags">Residential communities &#183; Commercial districts &#183; Office buildings &#183; Campuses &#183; Controlled public roads</p>
    </div>
    <img src="images/network.jpg" alt="An isometric city map showing MongBot delivering to hotels, hospitals, industrial parks, campuses, residential communities, offices, convenience stores and public roads">
  </section>
'''
    + page_next("mongcore.html", "Next", "MongCore", "technology.html", "Also see", "Technology")
    + footer())

# ------------------------------------------------------------- mongcore ---
pages["mongcore.html"] = (
    head("MongCore | Mongbotics",
         "MongCore is one application to onboard, monitor, command, and manage every supported robot.",
         "mongcore.html")
    + page_hero("images/control-system.jpg",
                "The MongCore control application beside a MongBot robot",
                "MongCore",
                "Your entire robot fleet,<br>in <em>one place.</em>")
    + page_intro("Universal robot control",
                 "See live status, assign tasks, issue commands, track activity, and access every robot&#8217;s identity and history through a unified interface.")
    + '''
  <section class="control">
    <div class="controlCopy">
      <p class="sectionTag">MongCore</p>
      <h2>One application.<br>Every robot.</h2>
      <p>Individuals and companies can onboard supported robots and manage them day to day from a single control interface, whatever the make.</p>
      <ul>
        <li><span>01</span>Real-time robot operations</li>
        <li><span>02</span>Universal fleet control</li>
        <li><span>03</span>Connected robot profiles</li>
      </ul>
    </div>
    <img src="images/control-system.jpg" alt="The MongCore control application beside a MongBot robot">
  </section>
'''
    + manifesto("Connected identity",
                "Every profile is tied to its <span>on-chain Soul.</span>",
                "Each robot in MongCore has a profile connected to its on-chain Soul.md, bringing identity, ownership, history, performance, and personality directly into the control interface.")
    + page_next("mongmarket.html", "Next", "MongMarket", "mongbot.html", "Also see", "MongBot")
    + footer())

# ----------------------------------------------------------- mongmarket ---
pages["mongmarket.html"] = (
    head("MongMarket | Mongbotics",
         "MongMarket is a peer-to-peer network where anyone can request a robot and owners can put theirs to work.",
         "mongmarket.html")
    + page_hero("images/identity.jpg",
                "Two MongBot robots passing each other on a tree-lined street",
                "MongMarket",
                "Put robots<br>to <em>work.</em>")
    + page_intro("The robot economy",
                 "Request autonomous robots for delivery, transportation, inspection, security, and more. Owners list robots, accept jobs, and earn when work is completed.")
    + '''
  <section class="market">
    <div>
      <p class="sectionTag">MongMarket</p>
      <h2>Grab for<br>robots.</h2>
    </div>
    <div class="marketCopy">
      <p>The marketplace connects people who need robotic services with people who own robots, creating a peer-to-peer robot sharing economy. Jobs are assigned through the platform, completed by autonomous robots, and paid for in the app.</p>
      <div class="marketLine">
        <span>REQUEST</span><i></i><span>MATCH</span><i></i><span>COMPLETE</span><i></i><span>EARN</span>
      </div>
      <p class="plain">In simple terms: Grab for robots.</p>
    </div>
  </section>
'''
    + page_next("about.html", "Next", "About", "mongcore.html", "Also see", "MongCore")
    + footer())

# ---------------------------------------------------------------- about ---
pages["about.html"] = (
    head("About Us | Mongbotics",
         "Thailand's first decentralized robotics company, building the control layer for personally owned autonomous robots.",
         "about.html")
    + page_hero("images/about-hero.jpg",
                "A MongBot robot at rest on a quiet Bangkok street at night, warm light from a shopfront falling across it",
                "About Mongbotics",
                "Robots with<br>a <em>soul.</em>",
                crop="low")
    + page_intro("Who we are",
                 "We are Thailand&#8217;s first robotics company building our MongBot robots on a decentralized autonomous control system. Our mission is to build a global decentralized control layer that makes robots easy for anyone to own, use, and share.")
    + '''
  <section class="why">
    <p class="sectionTag">Why now</p>
    <h2>The autonomous revolution is here.</h2>
    <div class="whyGrid">
      <div>
        <h4>Ownership needs a digital layer</h4>
        <p>As robots gain autonomy, mobility, and value, they need persistent identity, verifiable ownership, and portable history. Blockchain provides the infrastructure for that.</p>
      </div>
      <div>
        <h4>Robots can become an economic network</h4>
        <p>Once robots can be securely owned, controlled, and transferred, they can also be shared, hired, and put to work through a global marketplace.</p>
      </div>
      <div>
        <h4>The infrastructure does not exist yet</h4>
        <p>Autonomous robots are moving toward a future where individuals and businesses can own and operate them as easily as other connected devices. Today there is no digital infrastructure to support that.</p>
      </div>
    </div>
  </section>
'''
    + manifesto("The thesis",
                "Autonomous robots should be as <span>personal and accessible</span> as smartphones.",
                "We believe the robots people choose to live and work alongside should have identity, personality, and character. Some of the most memorable robots in science fiction became cultural icons because they felt alive. We want to bring that same sense of individuality to real-world robots.")
    + '''
  <section class="reach" id="contact">
    <div>
      <p class="sectionTag">Talk to us</p>
      <h2>Partner with<br>Mongbotics.</h2>
    </div>
    <dl>
      <dt>Email</dt>
      <dd><a href="mailto:hello@mongbotics.com">hello@mongbotics.com</a></dd>
      <dt>Location</dt>
      <dd>Bangkok, Thailand</dd>
    </dl>
  </section>
'''
    + page_next("technology.html", "Next", "Technology", "index.html", "Back to", "Home")
    + footer())

# ------------------------------------------------------------------------
os.makedirs(OUT, exist_ok=True)
for name, html in pages.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {name:20s} {len(html):6d} bytes")

# guard: no em dashes anywhere in the generated output
bad = [(n, h.count("—")) for n, h in pages.items() if "—" in h]
print("\nem dash check:", "CLEAN" if not bad else f"FOUND {bad}")
