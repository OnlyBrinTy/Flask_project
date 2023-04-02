var speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
var listening_animation;
var is_recognizing;
var recognition;
var paragraph;
var button;


function send_text_to_server(audio_output, paragraph_text) {
    $.ajax({ 
        type: 'POST',
        url: '/DATA_text_from_speech',
        data: JSON.stringify({"audio": audio_output, "text": paragraph_text}),
        contentType: 'application/json;charset=UTF-8',
        success : function(similarity)
        {
            alert(similarity);
        }
    });
}


function start_listening(paragraph_id) {
    listening_animation = document.getElementById(`loadFacebookG_${paragraph_id}`);
    listening_animation.style.display = 'flex';

    button = document.getElementById(`button_${paragraph_id}`);
    button.className = 'stop_button';
    button.innerHTML = 'Stop';
    button.setAttribute('onclick', `stop_listening(${paragraph_id})`);

    paragraph = document.getElementById(`paragraph_${paragraph_id}`).firstElementChild;
    paragraph_text = paragraph.innerHTML
    paragraph.innerHTML = 'Speak...'

    get_text_from_speech(paragraph_text);
}


function stop_listening(paragraph_id) {
    listening_animation.style.display = 'none';

    button.className = "start_button";
    button.innerHTML = 'Start';
    button.setAttribute('onclick', `start_listening(${paragraph_id})`);

    stop_recognition();
}


async function get_text_from_speech(paragraph_text) {
    recognition = new speechRecognition()
    recognition.continuous = true
    recognition.interimResults = false
    recognition.maxAlternatives = 3
    recognition.lang = 'ru-RU'

    is_recognizing = true
    let final_transcript = ''

    recognition.start();

    recognition.onresult = (event) => {
        var last = event.results.length - 1;

        if(event.results[last].isFinal && event.results[last][0].confidence >= 0.7) {
            final_transcript += event.results[last][0].transcript + ' ';
        }
    }
 
    recognition.onend = () => {
        if (is_recognizing) {
            recognition.start()
        }
        else {
            final_transcript = final_transcript.slice(0, -1)
            if (final_transcript.length < 10) {
                alert('Слишком короткое сообщение')
                return;
            }

            send_text_to_server(final_transcript, paragraph_text)
        }
    }
}


function stop_recognition() {
    recognition.stop()
    is_recognizing = false
}
