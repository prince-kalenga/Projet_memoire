import spacy
import random
import fitz  # PyMuPDF

nlp = spacy.load("fr_core_news_sm")

def extraire_texte_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    texte = ""
    for page in doc:
        texte += page.get_text()
    return texte

def generer_qcm_depuis_texte(texte, nb_questions=10):
    doc = nlp(texte)
    phrases = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 20]
    questions = []

    for phrase in random.sample(phrases, min(nb_questions * 2, len(phrases))):
        doc_phrase = nlp(phrase)
        entites = [ent for ent in doc_phrase.ents if ent.label_ in ("PER", "ORG", "LOC", "MISC", "DATE", "NUM")]
        
        if not entites:
            continue

        entite = random.choice(entites)
        bonne_reponse = entite.text
        question = phrase.replace(bonne_reponse, "_____")

        # Génération de distracteurs simples
        distracteurs = set()
        while len(distracteurs) < 3:
            mot = random.choice(phrases)
            faux = random.choice(mot.split())
            if faux != bonne_reponse and faux.isalpha() and len(faux) > 2:
                distracteurs.add(faux)

        options = list(distracteurs) + [bonne_reponse]
        random.shuffle(options)

        questions.append({
            "question": question,
            "options": options,
            "reponse": bonne_reponse
        })

        if len(questions) >= nb_questions:
            break

    return questions

























