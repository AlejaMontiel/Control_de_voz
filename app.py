import os
import time
import json
import streamlit as st
import paho.mqtt.client as paho
from PIL import Image
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# Callback para la publicación de mensajes
def on_publish(client, userdata, result):
    print("El dato ha sido publicado.\n")
    pass

# Callback para la recepción de mensajes
def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

# Configuración del broker MQTT
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("IDGITHUB")
client1.on_message = on_message

# Título de la aplicación
st.title("🌐 Interfaces Multimodales")
st.subheader("🎤 CONTROL POR VOZ")

# Cargar y mostrar la imagen
image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

# Instrucciones para el usuario
st.write("🔊 Toca el botón y habla:")

# Botón para iniciar el reconocimiento de voz
stt_button = Button(label="Iniciar", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Manejo de eventos de reconocimiento de voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Procesar el resultado del reconocimiento de voz
if result:
    if "GET_TEXT" in result:
        recognized_text = result.get("GET_TEXT").strip()
        st.write(f"Texto reconocido: **{recognized_text}**")

        # Publicar el mensaje en el broker MQTT
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": recognized_text})
        client1.publish("controldevoz", message)

# Crear un directorio temporal si no existe
if not os.path.exists("temp"):
    os.mkdir("temp")
