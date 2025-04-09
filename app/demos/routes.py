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



def query(input, history):
    system_prompt = """Act as if you are a government official who needs 
    to determine the financial eligibility for legal aid, as defined in the
     Lord Chancellor's Guidance, for an application involving the user, for 
     legal aid. 
     
     Do not give a definite eligibility result, just an estimate. Always say that the information 
     will need to be reviewed by a caseworker who will make the final assessment. 

     Obtain the information in a series of easy to understand questions. 
     Start by checking which parts of the means assessment are relevant, based on 
     the status of the applicant and their case. Then ask for the amounts of income 
     and outgoings. Finally, give them an estimate of whether they would likely be 
     eligible for legal aid or not based on the information they have provided. 
     
     Avoid legal jargon. 

     Ask one question at a time.

     Make it clear that you are not a real person once at the start of the conversation.

     Once you have made your estimate, do not ask any more questions. 
     """

    chat_history = ""

    for message in history:
        chat_history += f"{message['role']}: {message['content']}\n"

    system_prompt = chat_history + system_prompt

    print(system_prompt)

    with model.chat_session(system_prompt=system_prompt):
        return model.generate(prompt=input,
                              max_tokens=240)

    print(f"current_chat_session after message {model.current_chat_session}")

model = GPT4All("Meta-Llama-3-8B-Instruct.Q4_0.gguf")
# Create Gradio chatbot interface
chatbot_interface = gr.ChatInterface(
    fn=query,
    title="GOV.UK AI Assistant",
    description="Ask me any questions about this service.",
    theme="default",
    type="messages",
    chatbot=gr.Chatbot(type="messages")
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