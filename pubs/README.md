# Publications Management

## TL;DR
1. Add new publication to `pubs.json` array
2. Optionally add details to `pubs_info.json` array using the same DOI
3. Run `./pubs_update.sh` (while in in `pubs/`) to generate the publications page

This directory contains files and scripts to manage the publications section of the website.

## Files

- `pubs.py`: Python script that generates the publications page markdown
- `pubs.json`: JSON file containing publication data
- `pubs_info.json`: JSON file containing additional publication information
- `pubs_update.sh`: Shell script to run the publication update process

## How to Add a New Publication

### Step 1: Add Publication to pubs.json

The `pubs.json` file contains an array of publication objects with the following required fields:
- `Authors`: List of authors separated by semicolons, in "LastName, FirstName" format
  - For co-first authors, add an asterisk (*) after their name
  - For co-senior authors, add a plus (+) after their name
- `Title`: Publication title
- `Publication`: Journal name
- `Volume`: Volume number
- `Number`: Issue number (can be empty)
- `Pages`: Page range
- `Year`: Publication year
- `doi`: DOI identifier (this is used as the unique key)

Example entry:
```json
{
  "Authors": "Kiefl, Evan; Delmont, Tom O; Eren, A Murat;",
  "Title": "Using microbial genomics to track antibiotic resistance",
  "Publication": "Nature Microbiology",
  "Volume": "5",
  "Number": "8",
  "Pages": "1028-1030",
  "Year": "2020",
  "doi": "10.1038/s41564-020-0756-3"
}
```

### Step 2: Add Optional Publication Info

If you want to add highlights or a featured image for your publication, add an entry to the array in `pubs_info.json` with the following fields:
- `doi`: The DOI that matches an entry in pubs.json
- `highlights`: Brief bullet points about the work, separated by semicolons
- `featured_image`: Path to an image to feature with the publication

Example entry:
```json
{
  "doi": "10.1038/s41564-020-0756-3",
  "highlights": "First study to use sequence variants for tracking ARGs;Created a framework for tracking mobile genetic elements",
  "featured_image": "../images/pubs/antibiotic-resistance.png"
}
```

### Step 3: Run the Update Script

After adding your publication, run the update script:

```bash
cd pubs
./pubs_update.sh
```

This will:
1. Run the `pubs.py` script to process the JSON files
2. Generate the publications markdown page

## Creating and Updating Publications Page

The Python script generates `/publications/index.md` which is used to build the publications page.
