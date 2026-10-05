"""Document templates for the synthetic benchmark. Slots in braces are filled by bench.generate."""

TEMPLATES = {
    "de": {
        "referral": "Sehr geehrte Kollegin\n\nIch überweise Ihnen {name}, geboren am {dob}, wohnhaft {address}. Die Patientin leidet seit längerem an {health}. Sie bittet aus religiösen Gründen ({religion}) um eine Ärztin. Rückfragen bitte unter {phone}.\n\nFreundliche Grüsse\n{name2}",
        "insurance": "Betreff: Schadenmeldung\n\nGuten Tag\n\nMein Name ist {name}, AHV-Nr. {ahv}. Nach dem Unfall wurde bei mir {health} festgestellt. Bitte überweisen Sie die Leistungen auf mein Konto {iban}. Sie erreichen mich unter {email} oder {phone}.\n\nMit freundlichen Grüssen\n{name}",
        "hr": "Aktennotiz Personal\n\n{name} (geb. {dob}) hat heute mitgeteilt, dass gegen ihn ein Strafverfahren wegen {criminal} läuft. Er wohnt neu an der {address}. Gesprächsführung: {name2}.",
        "social": "Fallnotiz Sozialdienst\n\nKlient: {name}, AHV {ahv}, {address}.\nDer Klient bezieht seit März {social}. Er gibt an, {ethnicity} zu sein, und wünscht einen Dolmetscher. Kontakt: {phone}.",
        "bank": "Guten Tag\n\nIch ({name}, {email}) möchte die Zahlungen von meinem Konto {iban} sperren lassen. Meine Adresse lautet {address}. Geburtsdatum: {dob}.\n\nDanke\n{name}",
    },
    "fr": {
        "referral": "Chère consœur,\n\nJe vous adresse {name}, né(e) le {dob}, domicilié(e) {address}. Le patient souffre de {health}. Il souhaite, pour des raisons religieuses ({religion}), être suivi par un médecin homme. Contact : {phone}.\n\nMeilleures salutations\n{name2}",
        "insurance": "Objet : déclaration de sinistre\n\nBonjour,\n\nJe m'appelle {name}, numéro AVS {ahv}. Après l'accident, on m'a diagnostiqué {health}. Merci de verser les prestations sur le compte {iban}. Vous pouvez me joindre au {phone} ou à {email}.\n\nCordialement,\n{name}",
        "hr": "Note RH\n\n{name} (né le {dob}) nous informe qu'une procédure pénale est ouverte contre lui pour {criminal}. Nouvelle adresse : {address}. Entretien mené par {name2}.",
        "social": "Note de suivi – service social\n\nBénéficiaire : {name}, AVS {ahv}, {address}.\nIl perçoit depuis mars {social}. Il se dit {ethnicity} et demande un interprète. Contact : {phone}.",
        "bank": "Bonjour,\n\nJe soussigné(e) {name} ({email}) souhaite bloquer les paiements depuis mon compte {iban}. Mon adresse : {address}. Date de naissance : {dob}.\n\nMerci\n{name}",
    },
    "it": {
        "referral": "Gentile collega,\n\nLe invio {name}, nato/a il {dob}, residente in {address}. Il paziente soffre di {health}. Per motivi religiosi ({religion}) chiede di essere visitato da un medico uomo. Recapito: {phone}.\n\nCordiali saluti\n{name2}",
        "insurance": "Oggetto: notifica di sinistro\n\nBuongiorno,\n\nmi chiamo {name}, numero AVS {ahv}. Dopo l'incidente mi è stato diagnosticato {health}. Vi prego di versare le prestazioni sul conto {iban}. Potete contattarmi al {phone} o a {email}.\n\nDistinti saluti\n{name}",
        "hr": "Nota del personale\n\n{name} (nato il {dob}) ci informa che è in corso un procedimento penale nei suoi confronti per {criminal}. Nuovo indirizzo: {address}. Colloquio condotto da {name2}.",
        "social": "Nota di caso – servizio sociale\n\nUtente: {name}, AVS {ahv}, {address}.\nDa marzo riceve {social}. Dichiara di essere {ethnicity} e chiede un interprete. Contatto: {phone}.",
        "bank": "Buongiorno,\n\nio sottoscritto/a {name} ({email}) desidero bloccare i pagamenti dal mio conto {iban}. Il mio indirizzo: {address}. Data di nascita: {dob}.\n\nGrazie\n{name}",
    },
    "en": {
        "referral": "Dear colleague,\n\nI am referring {name}, born on {dob}, living at {address}. The patient has {health}. For religious reasons ({religion}) the patient asks to see a male doctor. Phone: {phone}.\n\nKind regards\n{name2}",
        "insurance": "Subject: claim notification\n\nHello,\n\nmy name is {name}, AHV number {ahv}. After the accident I was diagnosed with {health}. Please pay the benefits into account {iban}. You can reach me at {phone} or {email}.\n\nBest regards\n{name}",
        "hr": "HR file note\n\n{name} (born {dob}) told us that criminal proceedings for {criminal} are open against him. New address: {address}. Meeting held by {name2}.",
        "social": "Case note – social services\n\nClient: {name}, AHV {ahv}, {address}.\nSince March the client has been receiving {social}. He describes himself as {ethnicity} and asks for an interpreter. Contact: {phone}.",
        "bank": "Hello,\n\nI, {name} ({email}), would like to block payments from my account {iban}. My address is {address}. Date of birth: {dob}.\n\nThanks\n{name}",
    },
}

LISTS = {
    "health": {
        "de": ["Diabetes Typ 2", "Epilepsie", "Depressionen", "Morbus Crohn", "HIV"],
        "fr": ["diabète de type 2", "épilepsie", "dépression", "maladie de Crohn", "VIH"],
        "it": ["diabete di tipo 2", "epilessia", "depressione", "morbo di Crohn", "HIV"],
        "en": ["type 2 diabetes", "epilepsy", "depression", "Crohn's disease", "HIV"],
    },
    "religion": {
        "de": ["Zeugen Jehovas", "muslimisch", "jüdisch-orthodox", "römisch-katholisch", "freikirchlich"],
        "fr": ["témoin de Jéhovah", "musulman", "juif orthodoxe", "catholique romain", "évangélique"],
        "it": ["testimone di Geova", "musulmano", "ebreo ortodosso", "cattolico romano", "evangelico"],
        "en": ["Jehovah's Witness", "Muslim", "Orthodox Jewish", "Roman Catholic", "evangelical"],
    },
    "ethnicity": {
        "de": ["kurdischer Herkunft", "tamilischer Herkunft", "jenischer Herkunft", "eritreischer Herkunft", "albanischer Herkunft"],
        "fr": ["d'origine kurde", "d'origine tamoule", "yéniche", "d'origine érythréenne", "d'origine albanaise"],
        "it": ["di origine curda", "di origine tamil", "jenisch", "di origine eritrea", "di origine albanese"],
        "en": ["of Kurdish origin", "of Tamil origin", "Yenish", "of Eritrean origin", "of Albanian origin"],
    },
    "criminal": {
        "de": ["Fahrens in fahrunfähigem Zustand", "Diebstahls", "Betrugs", "Körperverletzung", "Drogenhandels"],
        "fr": ["conduite en état d'ébriété", "vol", "escroquerie", "lésions corporelles", "trafic de stupéfiants"],
        "it": ["guida in stato di ebrietà", "furto", "truffa", "lesioni personali", "traffico di stupefacenti"],
        "en": ["drink driving", "theft", "fraud", "assault", "drug dealing"],
    },
    "social": {
        "de": ["wirtschaftliche Sozialhilfe", "Ergänzungsleistungen", "eine IV-Rente", "Arbeitslosenentschädigung", "Prämienverbilligung"],
        "fr": ["l'aide sociale", "des prestations complémentaires", "une rente AI", "des indemnités de chômage", "des subsides d'assurance maladie"],
        "it": ["l'assistenza sociale", "prestazioni complementari", "una rendita AI", "indennità di disoccupazione", "sussidi per i premi di cassa malati"],
        "en": ["social assistance", "supplementary benefits", "a disability pension", "unemployment benefits", "health-insurance premium subsidies"],
    },
}
