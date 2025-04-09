from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovCheckboxInput,
    GovDateInput,
    GovPasswordInput,
    GovSubmitInput,
    GovTextInput,
)
from wtforms.fields import (
    BooleanField,
    DateField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
    Regexp,
)

from app.demos.custom_validators import RequiredIf



class CreateAccountForm(FlaskForm):
    first_name = StringField(
        "First name",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter your first name")],
    )
    last_name = StringField(
        "Last name",
        widget=GovTextInput(),
        validators=[InputRequired(message="Enter your last name")],
    )
    date_of_birth = DateField(
        "Date of birth",
        widget=GovDateInput(),
        format="%d %m %Y",
        validators=[InputRequired(message="Enter your date of birth")],
        description="For example, 31 3 1980",
    )
    national_insurance_number = StringField(
        "National Insurance number",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter a National Insurance number"),
            Length(
                max=13,
                message="National Insurance number must be 13 characters or fewer",
            ),
            Regexp(
                regex=r"^[a-zA-Z]{2}\d{6}[aAbBcCdD]$",
                message="Enter a National Insurance number in the correct format",
            ),
        ],
        description="It’s on your National Insurance card, benefit letter, payslip or P60. For example, ‘QQ 12 34 56 C’.",
    )
    email_address = StringField(
        "Email address",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter an email address"),
            Length(
                max=256,
                message="Email address must be 256 characters or fewer",
            ),
            Email(
                message="Enter an email address in the correct format, like name@example.com"
            ),
        ],
        description="You'll need this email address to sign in to your account",
    )
    telephone_number = StringField(
        "UK telephone number",
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter a UK telephone number"),
            Regexp(
                regex=r"[\d \+]",
                message="Enter a telephone number, like 01632 960 001, 07700 900 982 or +44 0808 157 0192",
            ),
        ],
    )
    password = PasswordField(
        "Create a password",
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message="Enter a password"),
            Length(
                min=8,
                message="Password must be at least 8 characters",
            ),
        ],
        description="Must be at least 8 characters",
    )
    confirm_password = PasswordField(
        "Confirm password",
        widget=GovPasswordInput(),
        validators=[
            InputRequired(message="Confirm your password"),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    terms_and_conditions = BooleanField(
        "I agree to the terms and conditions",
        widget=GovCheckboxInput(),
        validators=[
            InputRequired(
                message="Select to confirm you agree with the terms and conditions"
            )
        ],
    )
    submit = SubmitField("Create account", widget=GovSubmitInput())