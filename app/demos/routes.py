import os

import yaml
from flask import flash, redirect, render_template, url_for, jsonify
from werkzeug.exceptions import NotFound
import gradio as gr
from transformers import pipeline
import threading


from fastapi.middleware.cors import CORSMiddleware

from app.demos import bp
from app.demos.forms import (
    AutocompleteForm,
    BankDetailsForm,
    ConditionalRevealForm,
    CreateAccountForm,
    KitchenSinkForm,
)

chatbot_model = pipeline("text-generation", model="gpt2")

def chat_with_ai(message, history):
    """Function to handle chatbot interactions with new message format"""
    # Format history using OpenAI-style messages
    history_text = ""
    for item in history:
        role = item["role"].capitalize()
        content = item["content"]
        history_text += f"{role}: {content}\n"
    
    prompt = f"{history_text}User: {message}\nAI:"

    # Generate response using GPT-2
    response = chatbot_model(prompt, max_new_tokens=100, num_return_sequences=1)[0]['generated_text']

    # Extract the AI response part
    ai_response = response.split("AI:")[-1].strip()

    return ai_response


# Create Gradio chatbot interface
chatbot_interface = gr.ChatInterface(
    fn=chat_with_ai,
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