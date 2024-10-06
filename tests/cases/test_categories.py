from app.models.types.categories import Categories


def test_all_civil_categories_exist():
    expected_categories = [
        "Claims Against Public Authorities",
        "Clinical negligence",
        "Community care",
        "Crime",
        "Debt",
        "Discrimination",
        "Education",
        "Family",
        "Family mediation",
        "Housing",
        "Immigration or asylum",
        "Mental health",
        "Prison law",
        "Public law",
        "Welfare benefits",
        "Modern slavery",
        "Housing Loss Prevention Advice Service",
    ]
    for category_name in expected_categories:
        assert category_name in [category.value for category in Categories]
