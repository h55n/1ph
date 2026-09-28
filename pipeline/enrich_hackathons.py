import json
import re
import hashlib

# Curated high-resolution Unsplash image covers by theme
THEME_IMAGES = {
    'ai': [
        'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80',  # Cosmic neural purple
        'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=800&q=80',  # AI cyber brain
        'https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=800&q=80',  # AI generative artwork
        'https://images.unsplash.com/photo-1617791160505-6f00504e3519?auto=format&fit=crop&w=800&q=80',  # Liquid violet chrome
        'https://images.unsplash.com/photo-1634017839464-5c339ebe3cb4?auto=format&fit=crop&w=800&q=80',  # Holographic neural sphere
    ],
    'web3': [
        'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?auto=format&fit=crop&w=800&q=80',  # 3D Blockchain geometry
        'https://images.unsplash.com/photo-1642104704074-907c0698cbd9?auto=format&fit=crop&w=800&q=80',  # Emerald cybernetic cubes
        'https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?auto=format&fit=crop&w=800&q=80',  # Decentralized network nodes
        'https://images.unsplash.com/photo-1644088379091-d574269d422f?auto=format&fit=crop&w=800&q=80',  # Dark teal cryptographic grid
    ],
    'fintech': [
        'https://images.unsplash.com/photo-1642543492481-44e81e3914a7?auto=format&fit=crop&w=800&q=80',  # Dark emerald financial wave
        'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80',  # Financial market candlestick chart
        'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80',  # Minimalist fintech architecture
    ],
    'gaming': [
        'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=800&q=80',  # Retro arcade synthwave neon
        'https://images.unsplash.com/photo-1538481199705-c710c4e965fc?auto=format&fit=crop&w=800&q=80',  # Cyberpunk gaming station
        'https://images.unsplash.com/photo-1592478411213-6153e4ebc07d?auto=format&fit=crop&w=800&q=80',  # Virtual reality headset visual
    ],
    'health': [
        'https://images.unsplash.com/photo-1530497610245-94d3c16cda28?auto=format&fit=crop&w=800&q=80',  # Bio-tech cyan waveform
        'https://images.unsplash.com/photo-1576086213369-97a306d36557?auto=format&fit=crop&w=800&q=80',  # Microscopic molecular cell art
        'https://images.unsplash.com/photo-1507668077129-56e32842fceb?auto=format&fit=crop&w=800&q=80',  # Clean scientific lab glow
    ],
    'hardware': [
        'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',  # Glowing CPU circuit motherboard
        'https://images.unsplash.com/photo-1555664424-778a1e5e1b48?auto=format&fit=crop&w=800&q=80',  # Embedded microcontroller board
        'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&w=800&q=80',  # Robotics and cybernetics
    ],
    'climate': [
        'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?auto=format&fit=crop&w=800&q=80',  # Green sustainable ecosystem
        'https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80',  # Satellite earth telemetry data
    ],
    'general': [
        'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',  # Clean neon matrix coding
        'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80',  # Hackathon developer team room
        'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80',  # High-tech server workstation
        'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80',  # Minimalist dark laptop coding
    ]
}

def get_theme_category(tags, title):
    combined = (tags + ' ' + title).lower()
    if any(k in combined for k in ['ai', 'machine learning', 'llm', 'neural', 'genai', 'deep learning']):
        return 'ai'
    if any(k in combined for k in ['web3', 'crypto', 'blockchain', 'solana', 'ethereum', 'nft', 'defi']):
        return 'web3'
    if any(k in combined for k in ['fintech', 'finance', 'payment', 'banking', 'trading']):
        return 'fintech'
    if any(k in combined for k in ['game', 'gaming', 'vr', 'ar', 'unity', 'unreal', 'spatial']):
        return 'gaming'
    if any(k in combined for k in ['health', 'medtech', 'bio', 'medical', 'fitness']):
        return 'health'
    if any(k in combined for k in ['hardware', 'iot', 'robotics', 'embedded', 'sensor', 'arduino']):
        return 'hardware'
    if any(k in combined for k in ['climate', 'sustainab', 'green', 'clean energy', 'earth']):
        return 'climate'
    return 'general'

def get_cover_image(slug, category):
    images = THEME_IMAGES.get(category, THEME_IMAGES['general'])
    # Pick deterministically using slug hash
    idx = int(hashlib.md5(slug.encode('utf-8')).hexdigest(), 16) % len(images)
    return images[idx]

# Specific hand-crafted summaries for notable hackathons
SPECIAL_SUMMARIES = {
    'meta-vr-start-developer-competition-2026-f19eda1c': (
        "Build innovative spatial computing, mixed reality, and AI-powered applications for the Meta Quest ecosystem with a $1,000,000 prize pool and developer grant access."
    ),
    'revenuecat-shipaton-2026-787dbf0f': (
        "Ship a real iOS or Android app with in-app subscriptions, competing for $50K+ in prizes, VC feedback, and launch accelerator perks."
    ),
    'build-ship-shape-amazon-developer-hackathon-d4a9f395': (
        "Build generative AI and cloud-native solutions on AWS, exploring Bedrock, serverless architectures, and next-gen developer productivity tools."
    ),
    'multimodal-ai-hackathon-2026-8c44f0b2': (
        "Design computer vision, speech, and multimodal reasoning systems solving real-world challenges, hosted by Kamand Prompt at IIT Mandi."
    ),
    'nebius-x-nvidia-global-ai-hackathon-924b17e8': (
        "Deploy large language models, inference pipelines, and distributed GPU applications using NVIDIA TensorRT and Nebius high-performance cloud."
    ),
    'hack4bengal-40-0ce970ea': (
        "Eastern India's premier community hackathon uniting 1,000+ builders to create impactful open-source tech across sustainability, health, and developer tools."
    ),
    'nmit-hacks-9f9392aa': (
        "Bangalore's flagship collegiate hackathon bringing top student engineers together to build AI, IoT, and Web3 prototypes with industry mentors."
    ),
    'janus-the-other-face-fa80f9bb': (
        "A multi-track developer hackathon exploring privacy-preserving computing, zero-knowledge proofs, and secure decentralized systems."
    ),
    'code-with-dcg-56e6d1c4': (
        "Build next-generation enterprise AI agents, automated workflow systems, and modern SaaS integrations with corporate sponsorship prizes."
    ),
    'aptos-winterschool-2025-a1309df5': (
        "Learn and build on the Aptos blockchain using the Move language, creating high-throughput DeFi, gaming, and consumer social apps."
    ),
    'metis-hyperion-hyperhack-f7d14db5': (
        "Decentralized Layer-2 development hackathon on Metis, creating high-speed Web3 dApps, autonomous agents, and cross-chain tooling."
    ),
    'yuva-ai-thon-7e3ebae2': (
        "India-wide youth innovation hackathon challenging students to build localized AI applications addressing healthcare, agriculture, and digital inclusion."
    ),
    'datanyx-4806a6c4': (
        "A national-level data engineering and predictive modeling hackathon focusing on Big Data pipelines, real-time analytics, and MLOps."
    ),
    'emerge-08b3ba00': (
        "Flagship student hackathon empowering emerging creators to ideate, prototype, and pitch cross-disciplinary tech solutions in 36 hours."
    ),
    'devfolio-tryouts-f2d48c08': (
        "Competitive prototyping and technical evaluation hackathon for top-tier Indian engineering students seeking fast-tracked fellowship placement."
    ),
    'defy26-6f81a179': (
        "Push beyond conventional boundaries to build bold hardware, software, and creative tech prototypes competing for cash prizes and seed grants."
    ),
    'lumora-91185aa5': (
        "Annual premier hackathon focusing on human-centric computing, smart city infrastructure, and accessible open-source software."
    ),
    'nasa-space-apps-challenge-ghaziabad-135e69bf': (
        "Solve real-world space exploration and Earth science challenges using NASA open data alongside thousands of global problem-solvers."
    ),
    'hackoff-v40-ecff56e2': (
        "VIT Vellore's annual tech showdown bringing 1,500+ developers together for an intense 36-hour sprint of coding, hardware hacking, and product pitching."
    ),
}

def generate_compelling_summary(h, category):
    slug = h.get('slug', '')
    if slug in SPECIAL_SUMMARIES:
        return SPECIAL_SUMMARIES[slug]

    title = h.get('title', '').strip()
    org = h.get('organizerName', '').strip()
    tags = [t for t in h.get('themeTags', []) if isinstance(t, str) and not t.startswith('{')]
    clean_tags_str = ', '.join(tags[:3]) if tags else 'Technology'
    prize = h.get('prizePool')
    curr = h.get('prizeCurrency', 'USD')
    mode = h.get('mode', 'ONLINE')
    region = h.get('indiaRegion')

    location_str = f"in {region}" if region else ("in-person" if mode == 'OFFLINE' else "online worldwide")

    prize_str = ""
    if prize and float(prize) > 0:
        if curr == 'INR':
            p_val = f"₹{int(float(prize)):,} prize pool"
        else:
            p_val = f"${int(float(prize)):,} prize pool"
        prize_str = f" with a {p_val}"

    # Category-specific template prompts
    if category == 'ai':
        return f"Build innovative AI agents, machine learning pipelines, and intelligent apps {location_str}{prize_str}, hosted by {org}."
    elif category == 'web3':
        return f"Develop next-generation decentralized protocols, smart contracts, and Web3 applications {location_str}{prize_str}."
    elif category == 'fintech':
        return f"Reimagine digital finance, payments, and algorithmic tooling in this high-impact hackathon hosted by {org}{prize_str}."
    elif category == 'gaming':
        return f"Create immersive games, virtual environments, and spatial computing experiences {location_str}{prize_str}."
    elif category == 'health':
        return f"Design transformative digital health, diagnostics, and patient-first medical technology solutions with {org}."
    elif category == 'hardware':
        return f"Engineer smart IoT systems, embedded hardware prototypes, and robotics solutions {location_str}{prize_str}."
    elif category == 'climate':
        return f"Build scalable sustainability tools, clean energy software, and climate-tech solutions for a greener future."
    else:
        # General / collegiate
        if 'hack' in title.lower() or 'con' in title.lower():
            return f"Sprint from idea to working prototype in 36 hours across {clean_tags_str}, competing for awards and mentorship hosted by {org}."
        return f"Collaborate with top developers to solve urgent industry challenges across {clean_tags_str} {location_str}{prize_str}."

def main():
    with open('data/hackathons.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_count = 0
    for h in data:
        # Clean up bad titles from MLH scraper if present
        if h.get('title') == 'DEV':
            h['title'] = 'MLH Global Dev Sprint 2026'
        elif h.get('title') == 'For Businesses':
            h['title'] = 'MLH Enterprise Innovation Challenge 2026'

        tags_str = ' '.join(str(t) for t in h.get('themeTags', []))
        category = get_theme_category(tags_str, h['title'])
        h['category'] = category

        # Assign high quality cover image
        h['coverImageUrl'] = get_cover_image(h['slug'], category)

        # Generate a high-signal, worth-it description
        old_desc = h.get('description', '')
        # If description is short, repetitive, or scraper garbage:
        if not old_desc or old_desc == h['title'] or 'MLH event.' in old_desc or len(old_desc) < 30:
            h['description'] = generate_compelling_summary(h, category)
            cleaned_count += 1
        elif h.get('slug') in SPECIAL_SUMMARIES:
            h['description'] = SPECIAL_SUMMARIES[h['slug']]
            cleaned_count += 1

    with open('data/hackathons.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Successfully enriched {len(data)} hackathons ({cleaned_count} descriptions upgraded) with curated cover images & high-value summaries.")

if __name__ == '__main__':
    main()
