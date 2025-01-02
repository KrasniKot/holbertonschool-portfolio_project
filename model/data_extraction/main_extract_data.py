from data_extractor import DataExtractor

de = DataExtractor(jsonfile='./Laws-20000101_20250101_raw.json')  # Generate the data extractor

# Get the laws from the json file, covering texts from 01-01-2000 up to 01-01-2025
de.fetch_json()         # Fetch the json containing all the laws' metadata
de.get_all_json_laws()  # Save the laws into a mongodb db

# Get contitution and Codes
de.get_constitution()  # Get uruguayan Constitution

# Get uruguayan Penal Code
de.get_pcode()

# Get uruguayan Civil Code
de.get_ccode()

# Get uruguayan Commercial Code
de.get_comcode()

# Get uruguayan Tax Code
de.get_tcode()

# Get uruguayan Criminal Procedure Code
de.get_cpcode()

# Get uruguayan General Process Code
de.get_gpcode()


# 'LIBRO': r"LIBRO(?:\s+[IVXLCDM]+|\s+PRELIMINAR)?(?:\s*-\s*[^\n<]*)?",
# 'CAPITULO': r"CAPITULO(?:\s+[IVXLCDM]+)?(?:\s*-\s*[^\n<]*)?",
# 'TIUTLO': r"(TITULO(?:\s+[IVXLCDM]+)?(?:\s+-)?\s*[^<\n]*)",
# 'SECCION': r"SECCION(?:\s+[IVXLCDM]+|\s+PRELIMINAR)?(?:\s*-\s*[^\n<]*)?"
