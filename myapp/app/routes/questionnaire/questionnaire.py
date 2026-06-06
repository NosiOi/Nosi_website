from flask import Blueprint

questionnaire_bp = Blueprint(
    "questionnaire",
    __name__,
    url_prefix="/questionnaire"
)

@questionnaire_bp.get("/")
def questionnaire_home():
    return "Questionnaire module is working"
