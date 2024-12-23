import uuid
from sqlmodel import Session, select
from fastapi.testclient import TestClient
from app.models.case_adaptations import CaseAdaptations, Adaptations, Languages
from app.models.cases import Case, CaseTypes
from tests.cases.utils import get_case_test_data, assert_dicts_equal
from tests.conftest import with_versions


def create_case_adaptation(case_id=None):
    return CaseAdaptations(
        case_id=case_id or uuid.uuid4(),
        languages=[Languages("CY"), Languages("EN")],
        needed_adaptations=[Adaptations("BSL - Webcam"), Adaptations("Text Relay")],
    )


def test_create_case_adaptation(session: Session):
    case_adaptation = create_case_adaptation()
    session.add(case_adaptation)
    session.commit()
    assert session.exec(select(CaseAdaptations)).all() == [case_adaptation]


def test_cascade_delete(session: Session):
    """If a case is deleted the cae_adaptations attached to said case should also be deleted."""
    case = Case(case_type=CaseTypes.CLA)
    case_adaptation = create_case_adaptation(case_id=case.id)
    session.add(case)
    session.add(case_adaptation)
    session.commit()
    assert session.exec(select(CaseAdaptations)).all() == [case_adaptation]

    session.delete(case)
    session.commit()
    assert session.exec(select(CaseAdaptations)).all() == []


@with_versions(["v1"])
def test_request_create_case_with_adaptations(client_authed: TestClient, version):
    """Test creating a case with adaptations through the api."""
    case_data = get_case_test_data()
    response = client_authed.post(f"{version}/cases/", json=case_data)
    assert response.status_code == 201
    assert_dicts_equal(
        response.json()["case_adaptations"], case_data["case_adaptations"]
    )


@with_versions(["v1"])
def test_request_update_case_with_adaptations(
    client_authed: TestClient, session: Session, version
):
    """Test updating a case with adaptations through the api."""
    case = Case(case_type=CaseTypes.CLA)
    session.add(case)
    session.commit()

    adaptations_data = {"case_adaptations": get_case_test_data()["case_adaptations"]}
    response = client_authed.put(f"{version}/cases/{case.id}", json=adaptations_data)
    assert response.status_code == 200
    assert_dicts_equal(
        response.json()["case_adaptations"], adaptations_data["case_adaptations"]
    )


@with_versions(["v1"])
def test_request_create_case_without_adaptations(client_authed: TestClient, version):
    """Test creating a case without adaptations through the api."""
    case_data = get_case_test_data()
    del case_data["case_adaptations"]

    response = client_authed.post(f"{version}/cases/", json=case_data)
    assert response.status_code == 201
    assert response.json()["case_adaptations"] is None


@with_versions(["v1"])
def test_request_update_case_without_adaptations(
    client_authed: TestClient, session: Session, version
):
    """Test updating a case without adaptations through the api."""
    case = Case(case_type=CaseTypes.CLA)
    session.add(case)
    session.commit()
    case_data = get_case_test_data()
    del case_data["case_adaptations"]

    response = client_authed.put(f"{version}/cases/{case.id}", json=case_data)
    assert response.status_code == 200
    assert response.json()["case_adaptations"] is None
