import re


# Small offline knowledge base of common medicines.
# Maps a normalized name / generic keyword -> (generic_name, category, form)
MEDICINE_KB = {
    "paracetamol": ("Paracetamol", "Analgesic & Antipyretic", "Tablet"),
    "panadol": ("Paracetamol", "Analgesic & Antipyretic", "Tablet"),
    "amoxicillin": ("Amoxicillin", "Antibiotic", "Capsule"),
    "amoxil": ("Amoxicillin", "Antibiotic", "Capsule"),
    "amoxiclav": ("Amoxicillin + Clavulanic Acid", "Antibiotic", "Tablet"),
    "ceftriaxone": ("Ceftriaxone", "Antibiotic", "Injection"),
    "azithromycin": ("Azithromycin", "Antibiotic", "Tablet"),
    "ciprofloxacin": ("Ciprofloxacin", "Antibiotic", "Tablet"),
    "metronidazole": ("Metronidazole", "Antibiotic / Antiprotozoal", "Tablet"),
    "flagyl": ("Metronidazole", "Antibiotic / Antiprotozoal", "Tablet"),
    "ibuprofen": ("Ibuprofen", "NSAID", "Tablet"),
    "diclofenac": ("Diclofenac", "NSAID", "Tablet"),
    "diclofenac sodium": ("Diclofenac Sodium", "NSAID", "Tablet"),
    "mefenamic acid": ("Mefenamic Acid", "NSAID", "Tablet"),
    "aspirin": ("Acetylsalicylic Acid", "NSAID / Antiplatelet", "Tablet"),
    "vitamin c": ("Ascorbic Acid", "Vitamin", "Tablet"),
    "ascorbic": ("Ascorbic Acid", "Vitamin", "Tablet"),
    "vitamin b": ("Vitamin B Complex", "Vitamin", "Tablet"),
    "vitamin b complex": ("Vitamin B Complex", "Vitamin", "Tablet"),
    "folic acid": ("Folic Acid", "Vitamin", "Tablet"),
    "ferrous": ("Ferrous Sulfate", "Mineral Supplement", "Tablet"),
    "iron": ("Ferrous Sulfate", "Mineral Supplement", "Tablet"),
    "multivitamin": ("Multivitamin", "Vitamin", "Tablet"),
    "amitriptyline": ("Amitriptyline", "Antidepressant", "Tablet"),
    "diazepam": ("Diazepam", "Sedative / Anxiolytic", "Tablet"),
    "prednisolone": ("Prednisolone", "Corticosteroid", "Tablet"),
    "dexamethasone": ("Dexamethasone", "Corticosteroid", "Tablet"),
    "hydrocortisone": ("Hydrocortisone", "Corticosteroid", "Cream"),
    "salbutamol": ("Salbutamol", "Bronchodilator", "Syrup"),
    "ventolin": ("Salbutamol", "Bronchodilator", "Inhaler"),
    "amodiaquine": ("Amodiaquine", "Antimalarial", "Tablet"),
    "artemether": ("Artemether + Lumefantrine", "Antimalarial", "Tablet"),
    "coartem": ("Artemether + Lumefantrine", "Antimalarial", "Tablet"),
    "quinine": ("Quinine", "Antimalarial", "Tablet"),
    "chloroquine": ("Chloroquine", "Antimalarial", "Tablet"),
    "omeprazole": ("Omeprazole", "Antacid / PPI", "Capsule"),
    "ranitidine": ("Ranitidine", "Antacid / H2 Blocker", "Tablet"),
    "metformin": ("Metformin", "Antidiabetic", "Tablet"),
    "glibenclamide": ("Glibenclamide", "Antidiabetic", "Tablet"),
    "glimepiride": ("Glimepiride", "Antidiabetic", "Tablet"),
    "losartan": ("Losartan", "Antihypertensive", "Tablet"),
    "amlodipine": ("Amlodipine", "Antihypertensive", "Tablet"),
    "nifedipine": ("Nifedipine", "Antihypertensive", "Tablet"),
    "enalapril": ("Enalapril", "Antihypertensive", "Tablet"),
    "captopril": ("Captopril", "Antihypertensive", "Tablet"),
    "atenolol": ("Atenolol", "Beta Blocker", "Tablet"),
    "propranolol": ("Propranolol", "Beta Blocker", "Tablet"),
    "simvastatin": ("Simvastatin", "Statin", "Tablet"),
    "atorvastatin": ("Atorvastatin", "Statin", "Tablet"),
    "clotrimazole": ("Clotrimazole", "Antifungal", "Cream"),
    "miconazole": ("Miconazole", "Antifungal", "Cream"),
    "fluconazole": ("Fluconazole", "Antifungal", "Capsule"),
    "albendazole": ("Albendazole", "Anthelmintic", "Tablet"),
    "mebendazole": ("Mebendazole", "Anthelmintic", "Tablet"),
    "loratadine": ("Loratadine", "Antihistamine", "Tablet"),
    "cetirizine": ("Cetirizine", "Antihistamine", "Tablet"),
    "chlorpheniramine": ("Chlorpheniramine", "Antihistamine", "Tablet"),
    "domperidone": ("Domperidone", "Antiemetic", "Tablet"),
    "ondansetron": ("Ondansetron", "Antiemetic", "Tablet"),
    "doxylamine": ("Doxylamine", "Antihistamine", "Tablet"),
    "vitamin d": ("Cholecalciferol", "Vitamin", "Capsule"),
    "calciferol": ("Cholecalciferol", "Vitamin", "Capsule"),
    "calcium": ("Calcium Carbonate", "Mineral Supplement", "Tablet"),
    "zinc": ("Zinc Sulfate", "Mineral Supplement", "Tablet"),
    "rehydrat": ("Oral Rehydration Salts", "Electrolyte", "Powder"),
    "ors": ("Oral Rehydration Salts", "Electrolyte", "Powder"),
    "gentamicin": ("Gentamicin", "Antibiotic", "Injection"),
    "penicillin": ("Penicillin", "Antibiotic", "Injection"),
    "tetracycline": ("Tetracycline", "Antibiotic", "Ointment"),
    "chloramphenicol": ("Chloramphenicol", "Antibiotic", "Drops"),
    "betamethasone": ("Betamethasone", "Corticosteroid", "Cream"),
    "mupirocin": ("Mupirocin", "Antibiotic", "Ointment"),
    "silver": ("Silver Sulfadiazine", "Antibiotic", "Cream"),
    "paraffin": ("Liquid Paraffin", "Laxative", "Syrup"),
    "lactulose": ("Lactulose", "Laxative", "Syrup"),
    "gaviscon": ("Gaviscon", "Antacid", "Syrup"),
    "antacid": ("Aluminium + Magnesium Hydroxide", "Antacid", "Syrup"),
    "cough": ("Guaifenesin", "Cough Suppressant", "Syrup"),
    "piriton": ("Chlorpheniramine", "Antihistamine", "Syrup"),
    "benylin": ("Benylin", "Cough Suppressant", "Syrup"),
    "nasal": ("Xylometazoline", "Decongestant", "Drops"),
    "eye": ("Eye Drops", "Ophthalmic", "Drops"),
    "ear": ("Ear Drops", "Otological", "Drops"),
    "insulin": ("Insulin", "Antidiabetic", "Injection"),
    "tramadol": ("Tramadol", "Opioid Analgesic", "Capsule"),
    "morphine": ("Morphine", "Opioid Analgesic", "Injection"),
    "furosemide": ("Furosemide", "Diuretic", "Tablet"),
    "spironolactone": ("Spironolactone", "Diuretic", "Tablet"),
    "warfarin": ("Warfarin", "Anticoagulant", "Tablet"),
    "clopidogrel": ("Clopidogrel", "Antiplatelet", "Tablet"),
    "acyclovir": ("Aciclovir", "Antiviral", "Tablet"),
    "zidovudine": ("Zidovudine", "Antiretroviral", "Tablet"),
    "nevirapine": ("Nevirapine", "Antiretroviral", "Tablet"),
    "efavirenz": ("Efavirenz", "Antiretroviral", "Tablet"),
    "carbamazepine": ("Carbamazepine", "Anticonvulsant", "Tablet"),
    "phenytoin": ("Phenytoin", "Anticonvulsant", "Tablet"),
    "valproate": ("Sodium Valproate", "Anticonvulsant", "Tablet"),
    "thyroxine": ("Levothyroxine", "Thyroid Hormone", "Tablet"),
    "pioglitazone": ("Pioglitazone", "Antidiabetic", "Tablet"),
    "allopurinol": ("Allopurinol", "Antigout", "Tablet"),
    "hydroxychloroquine": ("Hydroxychloroquine", "Antimalarial", "Tablet"),
    "ketoconazole": ("Ketoconazole", "Antifungal", "Cream"),
    "griseofulvin": ("Griseofulvin", "Antifungal", "Tablet"),
    "doxycycline": ("Doxycycline", "Antibiotic", "Capsule"),
    "erythromycin": ("Erythromycin", "Antibiotic", "Tablet"),
    "cloxacillin": ("Cloxacillin", "Antibiotic", "Capsule"),
    "ampicillin": ("Ampicillin", "Antibiotic", "Capsule"),
    "cefixime": ("Cefixime", "Antibiotic", "Tablet"),
    "cefuroxime": ("Cefuroxime", "Antibiotic", "Tablet"),
    "bactrim": ("Sulfamethoxazole + Trimethoprim", "Antibiotic", "Tablet"),
    "cotrimoxazole": ("Sulfamethoxazole + Trimethoprim", "Antibiotic", "Tablet"),
    "septrin": ("Sulfamethoxazole + Trimethoprim", "Antibiotic", "Tablet"),
    "malarone": ("Atovaquone + Proguanil", "Antimalarial", "Tablet"),
    "vitamin b12": ("Cyanocobalamin", "Vitamin", "Injection"),
    "vitamin a": ("Retinol", "Vitamin", "Capsule"),
    "vitamin e": ("Tocopherol", "Vitamin", "Capsule"),
    "vitamin k": ("Phytomenadione", "Vitamin", "Injection"),
    "omeg": ("Omega-3", "Supplement", "Capsule"),
    "fish": ("Omega-3", "Supplement", "Capsule"),
}

# Form keywords detected inside the medicine name
FORM_KEYWORDS = [
    ("ointment", "Ointment"), ("cream", "Cream"), ("gel", "Gel"),
    ("syrup", "Syrup"), ("suspension", "Syrup"), ("susp", "Syrup"),
    ("injection", "Injection"), ("inject", "Injection"), ("inj", "Injection"),
    ("drops", "Drops"), ("drop", "Drops"), ("eye drops", "Drops"),
    ("tablet", "Tablet"), ("tabs", "Tablet"), ("tab", "Tablet"),
    ("capsule", "Capsule"), ("caps", "Capsule"), ("cap", "Capsule"),
    ("powder", "Powder"), ("sachet", "Powder"),
    ("lotion", "Lotion"), ("spray", "Spray"), ("inhaler", "Inhaler"),
    ("patch", "Patch"), ("suppository", "Suppository"),
]

# Default unit per form
UNIT_BY_FORM = {
    "Tablet": "Strip", "Capsule": "Strip", "Syrup": "Bottle",
    "Injection": "Vial", "Cream": "Tube", "Ointment": "Tube",
    "Drops": "Bottle", "Powder": "Sachet", "Gel": "Tube",
    "Lotion": "Bottle", "Spray": "Bottle", "Inhaler": "Piece",
    "Patch": "Piece", "Suppository": "Piece",
}

# Common brand-name prefixes we should NOT treat as generic
BRAND_MARKERS = ["pfizer", "gsk", "glaxo", "cipla", "norton", "zydus", "tanzamed", "shelys", "unihealth"]

STRENGTH_RE = re.compile(r'(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|mcg|iu|units|unit|tablet|tablets)?', re.IGNORECASE)


class MedicineAIService:
    """AI-style assistant that suggests medicine details from a name.

    Uses a local knowledge base + heuristic parsing so it works offline.
    Can be swapped for a real ML model later without changing the API.
    """

    @staticmethod
    def suggest(name: str, strength: str = None, category: str = None, generic_name: str = None):
        raw = (name or "").strip()
        normalized = raw.lower().strip()

        result = {
            "name": raw,
            "generic_name": None,
            "category": None,
            "form": None,
            "unit": None,
            "strength": None,
            "brand": None,
            "confidence": "low",
            "source": "heuristics",
            "explanation": [],
        }

        if not normalized:
            return result

        # 1) Form detection from name keywords
        detected_form = None
        for kw, form in FORM_KEYWORDS:
            # word-boundary-ish match
            if re.search(r'(^|[\s\-/])' + re.escape(kw) + r'($|[\s\-/]|s$)', normalized):
                detected_form = form
                break
        if detected_form:
            result["form"] = detected_form
            result["unit"] = UNIT_BY_FORM.get(detected_form, "Piece")
            result["explanation"].append(f"Form '{detected_form}' detected in name")

        # 2) Strength extraction from the name itself
        if not strength:
            m = STRENGTH_RE.search(normalized)
            if m:
                num = m.group(1)
                unit_word = (m.group(2) or "").lower()
                strength = f"{num} {unit_word}".strip() if unit_word else f"{num}"
                result["strength"] = strength
                result["explanation"].append(f"Strength '{strength}' parsed from name")

        # 3) Knowledge base lookup (exact or partial)
        kb_hit = MEDICINE_KB.get(normalized)
        if not kb_hit:
            # try the first word(s)
            for word in normalized.split():
                if word in MEDICINE_KB:
                    kb_hit = MEDICINE_KB[word]
                    break
            if not kb_hit:
                for key, val in MEDICINE_KB.items():
                    if key in normalized and len(key) >= 5:
                        kb_hit = val
                        break

        if kb_hit:
            generic, cat, form = kb_hit
            result["generic_name"] = generic_name or generic
            result["category"] = category or cat
            if not result["form"]:
                result["form"] = form
                result["unit"] = UNIT_BY_FORM.get(form, "Piece")
            result["confidence"] = "high"
            result["source"] = "knowledge_base"
            result["explanation"].append(f"Matched known medicine '{generic}'")

        # 4) Category inference from generic if still unknown
        if not result["category"]:
            result["category"] = MedicineAIService._infer_category(result["generic_name"] or normalized)

        # 5) Brand suggestion: first capitalized word, unless it looks like a generic
        if not result["brand"] and result["confidence"] != "high":
            first_word = raw.split()[0] if raw.split() else ""
            if first_word and first_word.lower() not in MEDICINE_KB:
                result["brand"] = first_word

        return result

    @staticmethod
    def _infer_category(text: str):
        t = text.lower()
        rules = [
            (["antibiotic", "amox", "cef", "cipro", "metro", "doxy", "clox", "azithro", "genta", "cloram", "tetra", "cotrim", "bactrim", "flagyl", "penicillin", "amoxic"], "Antibiotic"),
            (["antimal", "malari", "artem", "quini", "amodia", "chloroquine", "lumef", "coartem"], "Antimalarial"),
            (["antifungal", "fung", "clotrim", "micon", "keto", "flucon", "griseo", "terbina"], "Antifungal"),
            (["pain", "analges", "paracetamol", "panadol", "tramadol", "morphine", "nsaid", "ibuprofen", "diclofenac", "aspirin", "naproxen", "mefenamic"], "Analgesic & Antipyretic"),
            (["vitamin", "ascorbic", "retinol", "tocopherol", "calciferol", "cyanocobal", "folic", "ferrous", "calcium", "zinc", "multivit"], "Vitamins & Supplements"),
            (["antiinflamm", "anti-inflamm", "steroid", "cortico", "predniso", "dexamethasone", "betamethasone", "hydrocortisone"], "Corticosteroid"),
            (["antidiabet", "metformin", "glibenclamide", "glimepiride", "insulin", "pioglitazone"], "Antidiabetic"),
            (["antihypertens", "losartan", "amlodipine", "nifedipine", "enalapril", "captopril", "atenolol", "propranolol", "beta blocker"], "Antihypertensive"),
            (["antacid", "ppi", "omeprazole", "ranitidine", "gaviscon", "acid"], "Gastrointestinal"),
            (["antihistamin", "loratadine", "cetirizine", "chlorphen", "allerg"], "Antihistamine"),
            (["cough", "expectorant", "guaifenesin", "dextrometh", "benylin", "cold"], "Cough & Cold"),
            (["antiviral", "aciclovir", "acyclovir", "antiretrov", "zidovudine", "nevirapine"], "Antiviral"),
            (["diuretic", "furosemide", "spironolactone"], "Diuretic"),
            (["anticoag", "warfarin", "clopidogrel"], "Cardiovascular"),
            (["statin", "simvastatin", "atorvastatin"], "Cardiovascular"),
            (["anticonvulsant", "epilep", "carbamazepine", "phenytoin", "valproate"], "Anticonvulsant"),
            (["anthelmintic", "albendazole", "mebendazole", "worm"], "Anthelmintic"),
            (["antiemetic", "domperidone", "ondansetron", "nausea"], "Antiemetic"),
            (["sedative", "anxiolytic", "diazepam", "dormicum", "antidepress", "amitriptyline"], "Psychiatric"),
            (["thyroid", "thyroxine", "levothyroxine"], "Thyroid"),
            (["electrolyte", "rehydrat", "ors", "saline"], "Electrolyte"),
        ]
        for keywords, cat in rules:
            if any(k in t for k in keywords):
                return cat
        return "General"