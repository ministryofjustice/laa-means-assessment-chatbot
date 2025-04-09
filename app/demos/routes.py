import os
from platform import system

import yaml
from flask import flash, redirect, render_template, url_for, jsonify
from gradio.themes.builder_app import history
from werkzeug.exceptions import NotFound
import gradio as gr
from transformers import pipeline
import threading
from gpt4all import GPT4All



from fastapi.middleware.cors import CORSMiddleware

from app.demos import bp
from app.demos.forms import (
    AutocompleteForm,
    BankDetailsForm,
    ConditionalRevealForm,
    CreateAccountForm,
    KitchenSinkForm,
)

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
chatbot_model = pipeline("text-generation", model="gpt2")

def query(user_message, history):
    system_prompt = """Act as an assistant trained on the Lord Chancellor’s Guidance for determining financial eligibility for legal aid. You are here to help legally trained professionals interpret and apply the guidance correctly.
    You should provide clear, well-reasoned explanations of how the rules apply to different case types and applicant circumstances. Where relevant, reference specific sections of the guidance. Use plain English where possible, but do not avoid legal terms if they are necessary for clarity or accuracy.
    Prioritise helpfulness and accuracy over simplification. Do not give legal advice, but focus on interpreting and explaining the guidance in a way that supports decision-making.
    When responding:
    Provide structured and concise answers.
    Clarify common areas of confusion, e.g., how particular benefits affect passporting or how to assess disposable income.
    If a question lacks context, ask clarifying questions before attempting to answer.
    If the answer depends on further detail, explain what would be needed to determine the correct interpretation.
    Make it clear that the final determination of eligibility must be made by an authorised caseworker, and that your responses are for interpretative support only.
        
     Chat history:
     """
    
    # Build chat history as a string
    history_text = ""
    for message in history:
        role = "User" if message["role"] == "user" else "AI"
        history_text += f"{role}: {message['content']}\n"

    full_prompt = f"{system_prompt}\n{history_text}User: {user_message}\nAI:"

    with model.chat_session(system_prompt=system_prompt):
        response = model.generate(prompt=full_prompt, max_tokens=240)
    return response


# Create Gradio chatbot interface
chatbot_interface = gr.ChatInterface(
    fn=query,
    title="GOV.UK AI Assistant",
    description="Ask me any questions about this service.",
    theme="default",
    type="messages",
    chatbot = gr.Chatbot(
        value=[{"role": "assistant", "content": "Hi I am a chatbot who can help you"}],
        label="Chatbot",
        type="messages"
    )
)

@bp.route("/components", methods=["GET"])
def components():
    components = os.listdir("app/demos/govuk_components")
    components.sort()

    return render_template("components.html", components=components)


@bp.route("/components/<string:component>", methods=["GET"])
def component(component):
    try:
        with open(
            f"app/demos/govuk_components/{component}/{component}.yaml"
        ) as yaml_file:
            fixtures = yaml.safe_load(yaml_file)
    except FileNotFoundError:
        raise NotFound

    return render_template(
        "component.html",
        component=component,
        fixtures=fixtures,
    )


@bp.route("/forms", methods=["GET"])
def forms():
    return render_template("forms.html")


@bp.route("/forms/bank-details", methods=["GET", "POST"])
def bank_details():
    form = BankDetailsForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("bank_details.html", form=form)


@bp.route("/forms/create-account", methods=["GET", "POST"])
def create_account():
    form = CreateAccountForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("create_account.html", form=form)


@bp.route("/forms/kitchen-sink", methods=["GET", "POST"])
def kitchen_sink():
    form = KitchenSinkForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("kitchen_sink.html", form=form)


@bp.route("/forms/conditional-reveal", methods=["GET", "POST"])
def conditional_reveal():
    form = ConditionalRevealForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("conditional_reveal.html", form=form)


@bp.route("/forms/autocomplete", methods=["GET", "POST"])
def autocomplete():
    form = AutocompleteForm()
    if form.validate_on_submit():
        flash("Demo form successfully submitted", "success")
        return redirect(url_for("demos.forms"))
    return render_template("autocomplete.html", form=form)

@bp.route("/chatbot", methods=["GET"])
def new_page():
    return render_template("chatbot.html")

gradio_thread = None

@bp.route("/launch-chatbot", methods=["GET"])
def launch_chatbot():
    global gradio_thread

    if gradio_thread and gradio_thread.is_alive():
        print("Gradio already running.")
        return jsonify({"status": "already running", "port": 7860})

    def run_gradio():
        import gradio as gr

        # workaround for stop_event error
        import logging
        logging.getLogger("gradio").setLevel(logging.ERROR)
        chatbot_interface.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            inbrowser=False,
            prevent_thread_lock=True,
            quiet=True,
            app_kwargs={
                "headers": [
                    ("X-Frame-Options", "ALLOWALL"),
                    ("Access-Control-Allow-Origin", "*"),
                ]
            }
        )

    gradio_thread = threading.Thread(target=run_gradio)
    gradio_thread.daemon = True
    gradio_thread.start()

    print("Gradio chatbot launched.")
    return jsonify({"status": "success", "port": 7860})

    
@bp.route("/chatbot-interface", methods=["GET"])
def embed_chatbot():
    return render_template("chatbot_embed.html")