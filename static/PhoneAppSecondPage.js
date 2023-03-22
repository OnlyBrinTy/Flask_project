var listening_animation;
var button;
var text_field;
var rec;
var stream;
var synth;
var recognition;
var speechRecognition;
var recognizing
var paragraph;
var audio_output

start()


function start() {
    href = window.location.href;
    bt_num = Number(href.slice(href.lastIndexOf('=') + 1));
    $.ajax({ 
        type: 'POST',
        url: `/DATA_request?param=${bt_num}`,
        contentType: 'application/json;charset=UTF-8',
        success : function(outp_data)
        {
            fill_paragraphs(outp_data);
            afterLoad();
        }
    });
}


function audio_ajax(audio_output, paragraph, paragraph_obj) {
    $.ajax({ 
        type: 'POST',
        url: '/DATA_audio_text',
        data: JSON.stringify({"audio": audio_output, "text": paragraph}),
        contentType: 'application/json;charset=UTF-8',
        success : function(similarity)
        {
            paragraph_obj.firstChild.innerHTML = similarity['_'];
        }
    });
}


function fill_paragraphs(outp_data) {
    text_field = document.getElementById('text_field');
    outp_arr = outp_data['_'];
    for(let i = 0; i < outp_arr.length; i++) {
        let div = document.createElement('div');
        let button = document.createElement('div');
        let paragraph = i + 1
        if (i != 0) {
            div.className = "paragraph";
        }
        div.id = `paragraph_${paragraph}`;
        div.innerHTML = `<a>${outp_arr[i]}</a>`;
        button.className = "button";
        button.id = `button_${paragraph}`;
        button.innerHTML = "Start";
        button.setAttribute('onclick', `start_alg(${paragraph})`)
        text_field.append(div);
        let parahraph = document.getElementById(div.id);
        parahraph.append(button);
        parahraph.insertAdjacentHTML("beforeend",`
        <div class="loadFacebookG" id="loadFacebookG_${paragraph}">
            <div id="blockG_1" class="facebook_blockG"></div>
            <div id="blockG_2" class="facebook_blockG"></div>
            <div id="blockG_3" class="facebook_blockG"></div>
        </div>`);
    }
}


function afterLoad() {
    document.getElementById('loading').style.display = 'none';
    text_field.style.display = 'block';
}


document.addEventListener("onselectionchange") = () => {
    alert(window.getSelection());
}


function start_alg(paragraph_id) {
    listening_animation = document.getElementById(`loadFacebookG_${paragraph_id}`);
    button = document.getElementById(`button_${paragraph_id}`);
    button.className = 'stop_button';
    button.innerHTML = 'Stop';
    button.setAttribute('onclick', `end_alg(${paragraph_id})`);
    listening_animation.style.display = 'flex';
    paragraph = document.getElementById(`paragraph_${paragraph_id}`);
    audio_output = get_text(paragraph, paragraph.firstChild.innerHTML);
    paragraph.firstChild.innerHTML = 'Speak...'
}


async function get_text(paragraph_obj, paragraph) {
    let final_transcript = ''
    speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    recognition = new speechRecognition()
    recognition.continuous = true
    recognition.interimResults = false
    recognition.maxAlternatives = 3
    recognition.lang = 'ru-RU'
    synth = window.speechSynthesis;
    recognition.start();
    recognizing = true

      recognition.onresult = (event) => {
        var last = event.results.length - 1;
        if(event.results[last].isFinal && event.results[last][0].confidence >= 0.7) {
            final_transcript += event.results[last][0].transcript + ' ';
        }
      }
 
    recognition.onend = () => {
        if (recognizing){
            recognition.start()
        }
        else{
            final_transcript = final_transcript.slice(0, -1)
            if (final_transcript.length < 10) {
                alert('Слишком короткое сообщение')
                return;
            }
            audio_ajax(final_transcript, paragraph, paragraph_obj)
        }
    }
}

function stop() {
    recognition.stop()
    recognizing = false
}


function end_alg(paragraph_id) {
    button.className = "button";
    button.innerHTML = 'Start';
    button.setAttribute('onclick', `start_alg(${paragraph_id})`);
    listening_animation.style.display = 'none';
    stop();
}
