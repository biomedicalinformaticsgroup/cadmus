import re

MATERIALS_METHODS_TITLES = [
    r"materials\s*(and|&)?\s*methods",           # matches "Materials and Methods"
    r"methods\s*(and|&)?\s*materials",           # matches "Methods and Materials"
    r"materials",                                # matches just "Materials"
    r"methodology",                              # matches "Methodology"
    r"experimental\s+(procedure[s]?|section[s]?)",  # matches "Experimental Procedures" or "Experimental Sections"
    r"method[s]?",                               # matches "Method" or "Methods"
]

STOP_SECTION_TITLES = [
    "results",
    "discussion",
    "conclusion",
    "acknowledgments",
    "acknowledgement",
    "references",
    "bibliography",
    "supplementary materials",
    "supporting information",
]

def is_start_of_materials_methods(text):
    text = text.strip().lower()
    for pattern in MATERIALS_METHODS_TITLES:
        if re.search(pattern, text):
            return True
    return False

def is_end_of_materials_methods(text):
    lower_text = text.strip().lower()
    return any(keyword in lower_text for keyword in STOP_SECTION_TITLES)
