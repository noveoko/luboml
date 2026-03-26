# takes a HTML file of a family tree page from Jewishgen and converts it to a gephi ready graph
import csv
import re
from bs4 import BeautifulSoup
from difflib import get_close_matches
from collections import defaultdict

INPUT_FILE = "galinsky_family_tree.html.txt"

# ----------------------------
# Helpers
# ----------------------------

def normalize_name(name):
    name = re.sub(r"\s+", " ", name.strip())
    parts = name.split()

    if len(parts) == 1:
        return parts[0], ""

    given = " ".join(parts[:-1])
    surname = parts[-1]

    return given, surname


def extract_years(dates):
    years = re.findall(r"\d{4}", dates)
    birth = years[0] if len(years) > 0 else ""
    death = years[1] if len(years) > 1 else ""
    return birth, death


def canonical_key(given, surname, birth):
    return f"{surname.lower()}|{given.lower()}|{birth}"


# ----------------------------
# Parse People
# ----------------------------

def extract_people(soup):
    people = {}
    name_index = {}

    for box in soup.find_all("div", class_="tv_box"):
        for person_div in box.find_all("div", class_=re.compile("tvM|tvF")):

            name_tag = person_div.find("span", class_="NAME")
            dates_tag = person_div.find("span", class_="dates")

            if not name_tag:
                continue

            full_name = name_tag.get_text(" ", strip=True)
            given, surname = normalize_name(full_name)

            dates = dates_tag.get_text(" ", strip=True) if dates_tag else ""
            birth, death = extract_years(dates)

            key = canonical_key(given, surname, birth)

            if key not in people:
                pid = f"P{len(people)+1}"
                people[key] = {
                    "id": pid,
                    "label": full_name,
                    "given_name": given,
                    "surname": surname,
                    "birth": birth,
                    "death": death
                }

            name_index[full_name.lower()] = key

    return people, name_index


# ----------------------------
# Fuzzy matching
# ----------------------------

def resolve_name(name, name_index):
    name = name.lower()

    if name in name_index:
        return name_index[name]

    matches = get_close_matches(name, name_index.keys(), n=1, cutoff=0.7)

    if matches:
        return name_index[matches[0]]

    # fallback: surname match
    parts = name.split()
    if len(parts) > 1:
        surname = parts[-1]
        for k in name_index:
            if k.endswith(surname):
                return name_index[k]

    return None


# ----------------------------
# Extract Edges
# ----------------------------

def extract_edges(soup, people, name_index):
    edges = defaultdict(lambda: {"weight": 0, "type": ""})

    for box in soup.find_all("div", class_="tv_box"):
        person_divs = box.find_all("div", class_=re.compile("tvM|tvF"))

        names = []
        for div in person_divs:
            name_tag = div.find("span", class_="NAME")
            if name_tag:
                names.append(name_tag.get_text(" ", strip=True))

        # --- spouse edges ---
        if len(names) == 2:
            k1 = resolve_name(names[0], name_index)
            k2 = resolve_name(names[1], name_index)

            if k1 and k2 and k1 != k2:
                id1 = people[k1]["id"]
                id2 = people[k2]["id"]

                key = (id1, id2, "spouse")
                edges[key]["weight"] += 1
                edges[key]["type"] = "spouse"

        # --- parent edges ---
        for div in person_divs:
            title = div.get("title", "")

            match = re.search(r"(Son|Daughter) of (.+?) \+ (.+)", title)
            if not match:
                continue

            parent1_name = match.group(2).strip()
            parent2_name = match.group(3).strip()

            child_name_tag = div.find("span", class_="NAME")
            if not child_name_tag:
                continue

            child_name = child_name_tag.get_text(" ", strip=True)

            child_key = resolve_name(child_name, name_index)
            p1_key = resolve_name(parent1_name, name_index)
            p2_key = resolve_name(parent2_name, name_index)

            if child_key:
                child_id = people[child_key]["id"]

                for pk in [p1_key, p2_key]:
                    if pk:
                        parent_id = people[pk]["id"]
                        key = (parent_id, child_id, "parent")
                        edges[key]["weight"] += 1
                        edges[key]["type"] = "parent"

    return edges


# ----------------------------
# Write CSV
# ----------------------------

def write_nodes(people):
    with open("nodes.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "label", "given_name", "surname", "birth", "death"]
        )
        writer.writeheader()
        for p in people.values():
            writer.writerow(p)


def write_edges(edges):
    with open("edges.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["source", "target", "type", "weight"]
        )
        writer.writeheader()

        for (src, tgt, typ), data in edges.items():
            writer.writerow({
                "source": src,
                "target": tgt,
                "type": typ,
                "weight": data["weight"]
            })


# ----------------------------
# MAIN
# ----------------------------

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    people, name_index = extract_people(soup)
    edges = extract_edges(soup, people, name_index)

    write_nodes(people)
    write_edges(edges)

    print(f"People: {len(people)}")
    print(f"Edges: {len(edges)}")


if __name__ == "__main__":
    main()
