#!/usr/bin/env python3
"""Build app/index.html: embeds every skills/*/SKILL.md into the Reel Studio page.

Run after adding or editing a skill:  python3 app/build.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
TEMPLATE = Path(__file__).resolve().parent / "template.html"
OUT = Path(__file__).resolve().parent / "index.html"

# Skills that need Claude Code tools (filesystem, scraping CLI) or that the app replaces.
SKIP = {"ai-brain", "agent-reach", "content-factory"}

# Group headings from README.md ("**Study — learn what is working (5)**").
GROUP_NAMES = {"Study": "Estudiar", "Create": "Crear", "Distribute & convert": "Distribuir y convertir",
               "Grow & analyze": "Crecer y analizar"}


def readme_groups():
    groups, current = {}, None
    for line in (ROOT / "README.md").read_text().splitlines():
        m = re.match(r"\*\*(.+?) — .+\(\d+\)\*\*$", line)
        if m:
            current = GROUP_NAMES.get(m.group(1))
            continue
        m = re.match(r"- \[.+?\]\(skills/([\w-]+)/SKILL\.md\) — (.+)$", line)
        if m and current:
            groups[m.group(1)] = (current, m.group(2))
    return groups


def parse(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    front, body = (m.group(1), m.group(2)) if m else ("", text)
    desc = re.search(r"description:\s*>?\s*\n?((?:\s{2,}.+\n?)+|.+)", front)
    desc = " ".join(desc.group(1).split()) if desc else ""
    title = re.search(r"^# (.+)$", body, re.M)
    return (title.group(1).split(" — ")[0].strip() if title else path.parent.name), desc, body.strip()


def main():
    groups = readme_groups()
    skills = []
    for path in sorted(SKILLS.glob("*/SKILL.md")):
        slug = path.parent.name
        if slug in SKIP:
            continue
        title, desc, body = parse(path)
        group, tagline = groups.get(slug, ("Más herramientas", desc.split(". ")[0].rstrip(".") + "."))
        tagline = tagline[:1].upper() + tagline[1:]
        skills.append({"id": slug, "title": title, "group": group, "tagline": tagline, "body": body})
    data = json.dumps(skills, ensure_ascii=False).replace("</", "<\\/")
    OUT.write_text(TEMPLATE.read_text().replace("/*__SKILLS__*/[]", data))
    print(f"Wrote {OUT.relative_to(ROOT)} with {len(skills)} skills")


if __name__ == "__main__":
    main()
