from enum import Enum


class Categories(str, Enum):
    aap = "Claims Against Public Authorities"
    med = "Clinical negligence"
    com = "Community care"
    crm = "Crime"
    deb = "Debt"
    disc = "Discrimination"
    edu = "Education"
    mat = "Family"
    fmed = "Family mediation"
    hou = "Housing"
    immas = "Immigration or asylum"
    mhe = "Mental health"
    pl = "Prison law"
    pub = "Public law"
    wb = "Welfare benefits"
    mosl = "Modern slavery"
    hlpas = "Housing Loss Prevention Advice Service"
