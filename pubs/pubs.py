# -*- coding: utf-8 -*-
# A script to convert publication data into markdown


# EDIT THESE #####################################################################
names_to_highlight = ["Kiefl E"]

journal_name_fixes = [
    ("The ISME journal", "ISME J"),
    (
        "Proceedings of the National Academy of Sciences of the United States of America",
        "Proc Natl Acad Sci U S A",
    ),
    ("Proceedings of the National Academy of Sciences", "Proc Natl Acad Sci U S A"),
    ("Frontiers in Microbiology", "Front Microbiol"),
]

keep_pubs_after_year = 2009
##################################################################################

import os
import sys
import json
from datetime import datetime


class ConfigError(Exception):
    """A simple exception class for configuration errors."""

    pass


class Publications:
    def __init__(
        self, pubs_file_path="pubs.json", pubs_info_file_path="pubs_info.json"
    ):
        """Takes a JSON file with publication data (`pubs_file_path`), and an optional\
           JSON file with additional publication info (`pubs_info_file_path`), and\
           generates Markdown formatted output.

           Expected fields in pubs.json:
           - Authors: List of authors separated by semicolons
           - Title: Publication title
           - Publication: Journal name
           - Volume: Volume number
           - Number: Issue number (can be empty)
           - Pages: Page range
           - Year: Publication year
           - doi: DOI identifier

           Expected fields in pubs_info.json:
           - doi: The DOI of the pub matching to an entry in pubs.json
           - highlights: Brief bullet points about the work. Separate points with ';' 
                        HTML tags are OK.
           - featured_image: A URL or path to an image.
        """

        self.info = {}
        self.pubs_dict = {}
        self.journals_list = []
        self.authors_list = []
        self.recent_authors_list = []
        self.author_links = {}

        self.pubs_file_path = pubs_file_path
        self.pubs_info_file_path = pubs_info_file_path

    def get_author_highlights(self, pub):
        authors_str = []
        contributions_html = ""

        if pub["doi"] in self.info and "contributions" in self.info[pub["doi"]]:
            contributions = self.info[pub["doi"]]["contributions"]
            if contributions:
                contributions_html = '<span class="pub-contributions-tooltip"><div class="pub-contributions-tooltip-title">Contribution Summary</div><ul>'
                for c in contributions:
                    if c.strip():
                        contributions_html += '<li>%s</li>' % c.strip()
                contributions_html += '</ul></span>'

        for author in pub["authors"]:
            if author in pub["co_first_authors"]:
                author_h = author + "<sup>☯</sup>"
            elif author in pub["co_senior_authors"]:
                author_h = author + "<sup>‡</sup>"
            else:
                author_h = author

            if author in names_to_highlight:
                if contributions_html:
                    authors_str.append(
                        '<span class="pub-member-author-with-contributions">%s%s</span>' % (author_h, contributions_html)
                    )
                else:
                    authors_str.append(
                        '<span class="pub-member-author">%s</span>' % (author_h)
                    )
            else:
                authors_str.append(author_h)

        return ", ".join(authors_str)

    def parse_pubs_json(self):
        """Parse the JSON files containing publication data and additional info."""
        # Check if files exist
        if not os.path.exists(self.pubs_file_path):
            raise ConfigError(f"The file '{self.pubs_file_path}' does not exist.")

        # Load pubs_info.json if it exists
        if os.path.exists(self.pubs_info_file_path):
            try:
                with open(self.pubs_info_file_path, "r") as f:
                    pubs_info_list = json.load(f)
                    # Convert to dictionary with doi as key
                    self.info = {item["doi"]: item for item in pubs_info_list}
            except json.JSONDecodeError:
                raise ConfigError(
                    f"Could not parse '{self.pubs_info_file_path}' as JSON."
                )

        # Load pubs.json
        try:
            with open(self.pubs_file_path, "r") as f:
                pubs_list = json.load(f)
        except json.JSONDecodeError:
            raise ConfigError(f"Could not parse '{self.pubs_file_path}' as JSON.")

        # Check required fields in each publication
        required_fields = ["Authors", "Title", "Publication", "Volume", "Year", "doi"]
        for pub in pubs_list:
            missing_fields = [f for f in required_fields if f not in pub]
            if missing_fields:
                raise ConfigError(
                    f"Publication with DOI '{pub.get('doi', 'unknown')}' is missing required fields: {', '.join(missing_fields)}"
                )

            # Process the publication data
            doi = pub["doi"]
            authors = []
            co_first_authors = []
            co_senior_authors = []

            for author in [_.strip() for _ in pub["Authors"].split(";")]:
                if not len(author):
                    continue

                author_parts = [p.strip() for p in author.split(",")]
                if len(author_parts) < 2:
                    continue  # Skip if the author format is invalid

                author_last_name = author_parts[0]
                author_first_name_raw = author_parts[1]

                author_first_name = "".join(
                    [n[0] for n in author_first_name_raw.split()]
                )
                author_final_name = "%s %s" % (author_last_name, author_first_name)

                if author_first_name_raw.endswith("*"):
                    co_first_authors.append(author_final_name)
                elif author_first_name_raw.endswith("+"):
                    co_senior_authors.append(author_final_name)

                authors.append(author_final_name)

            # Format the issue info - handle empty fields gracefully
            issue_parts = []
            volume = pub.get("Volume", "").strip()
            number = pub.get("Number", "").strip()
            pages = pub.get("Pages", "").strip()

            if volume:
                if number:
                    issue_parts.append(f"{volume}({number})")
                else:
                    issue_parts.append(volume)

            if pages:
                issue_parts.append(pages)

            issue = ":".join(issue_parts) if issue_parts else ""

            year = pub["Year"].strip()
            pub_entry = {
                "authors": authors,
                "title": pub["Title"],
                "journal": pub["Publication"],
                "issue": issue,
                "doi": doi,
                "url": pub.get("url", "").strip(),
                "year": year,
                "co_first_authors": co_first_authors,
                "co_senior_authors": co_senior_authors,
            }

            if year not in self.pubs_dict:
                self.pubs_dict[year] = [pub_entry]
            else:
                self.pubs_dict[year].append(pub_entry)

    def get_markdown_text_for_pub(self, pub):
        """Gets a dictionary `pub`, returns a markdown formatted text."""
        pub_md = []

        A = lambda s: pub_md.append(s)

        A('<div class="pub">')
        A(
            """<div class="__dimensions_badge_embed__" data-doi="%s" data-hide-zero-citations="true" data-legend="hover-bottom" data-style="small_circle"></div>"""
            % pub["doi"]
        )

        # Open pub-header container
        A('    <div class="pub-header">')

        # Prioritize custom URL, then DOI, otherwise no link
        if pub.get("url"):
            A(
                '        <span class="pub-title"><a href="%s" target="_new">%s</a></span>'
                % (pub["url"], pub["title"])
            )
        elif pub["doi"]:
            A(
                '        <span class="pub-title"><a href="%s" target="_new">%s</a></span>'
                % ("https://doi.org/%s" % (pub["doi"]), pub["title"])
            )
        else:
            A('        <span class="pub-title">%s</span>' % pub["title"])

        author_html = self.get_author_highlights(pub)
        A('        <span class="pub-authors">%s</span>' % author_html)

        if pub["doi"] in self.info and self.info[pub["doi"]].get("note_about_order"):
            A('        <div class="pub-author-order-note">Order does not reflect contribution</div>')

        if pub["co_first_authors"] and not pub["co_senior_authors"]:
            A(
                '        <span class="pub-co-first-authors"><sup>☯</sup>Co-first authors</span>'
            )
        elif pub["co_first_authors"] and pub["co_senior_authors"]:
            A(
                '        <span class="pub-co-first-authors"><sup>☯</sup>Co-first authors; <sup>‡</sup>Co-senior authors</span>'
            )
        elif pub["co_senior_authors"] and not pub["co_first_authors"]:
            A(
                '        <span class="pub-co-first-authors"><sup>‡</sup>Co-senior authors</span>'
            )

        # Close pub-header container
        A('    </div>')

        if pub["doi"] in self.info:
            info = self.info[pub["doi"]]
            A(
                '    <div class="%s">'
                % ("pub-info" if info["featured_image"] else "pub-info-no-image")
            )

            if info["featured_image"]:
                A('    <div class="pub-featured-image">')
                A(
                    '    <a href="%s"><img src="%s" style="max-width: 100px; max-height: 80px; width: auto; border: none; height: auto; margin: 0 auto; display: block; transform: translateY(15%%);"/></a>'
                    % (info["featured_image"], info["featured_image"])
                )
                A("    </div>")

            highlights = info.get("highlights", [])
            if highlights:
                A(
                    '    <div class="%s">'
                    % (
                        "pub-highlights"
                        if info["featured_image"]
                        else "pub-highlights-no-image"
                    )
                )
                A("    <ul>")
                for h in highlights:
                    if h.strip():
                        A("        <li>%s</li>" % h.strip())
                A("    </ul>")
                A("    </div>")

            # Handle journal formatting with optional issue info
            url = pub.get("url") or ("https://doi.org/%s" % pub["doi"])
            url_link = f' | 🔗 <a href="{url}" target="_blank">doi:{pub["doi"]}</a>'
            if pub["issue"]:
                A(
                    '    <span class="pub-journal">📚 <b>%s</b>, %s%s</span>'
                    % (pub["journal"], pub["issue"], url_link)
                )
            else:
                A(
                    '    <span class="pub-journal">📚 <b>%s</b>%s</span>'
                    % (pub["journal"], url_link)
                )
            A("    </div>")

        A("</div>\n")

        return "\n".join(pub_md)

    def store_markdown_output_for_pubs(self, output_file_path):
        """Generate the markdown output and write it to a file."""
        years = "".join(
            [
                '<a href="#%s"><span class="category-item">%s</span></a>' % (y, y)
                for y in sorted(list(self.pubs_dict.keys()), reverse=True)
            ]
        )

        output_file = open(output_file_path, "w")
        W = lambda s: output_file.write(s + "\n")

        W("---")
        W("layout: publications")
        W("modified: %s" % datetime.today().strftime("%Y-%m-%d"))
        W("comments: false")
        W("---\n")
        W("\n")
        W(
            "{:.notice}\nThese publications are a subset of my scientific work that I consider to have "
            "contributed significantly towards. For further auxiliary publications see my "
            "[Google Scholar](https://scholar.google.com/citations?user=WxWOLg0AAAAJ&hl=en).\n\n"
        )

        W(
            """<script type='text/javascript' src='https://d1bxh8uas1mnw7.cloudfront.net/assets/embed.js'></script>\n"""
        )
        W(
            """<script async src="https://badge.dimensions.ai/badge.js" charset="utf-8"></script>\n"""
        )

        for year in sorted(list(self.pubs_dict.keys()), reverse=True):
            W("<h1>%s</h1>\n" % year)

            for pub in self.pubs_dict[year]:
                W(self.get_markdown_text_for_pub(pub))

            W("")


if __name__ == "__main__":
    pubs = Publications("../_data/pubs.json", "../_data/pubs_info.json")
    try:
        pubs.parse_pubs_json()
        pubs.store_markdown_output_for_pubs("../publications/index.md")
    except ConfigError as e:
        print(e)
        sys.exit(-1)
