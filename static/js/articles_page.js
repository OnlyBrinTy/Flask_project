var speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
var listening_animation;
var is_recognizing;
var paragraph_text;
var paragraph_id;
var mic_button;
var textarea;
var curr_div;
var button;

function send_delete_signal() {
    $.ajax({
        type: 'POST',
        url: '/DATA_delete_paragraph',
        data: JSON.stringify({'id': paragraph_id}),
        contentType: 'application/json;charset=UTF-8',
        cache: false,
        success: function(response) {close_block(response['article_is_empty'])}
    });
}

function send_text_to_server() {
    $.ajax({
        type: 'POST',
        url: '/DATA_text_from_speech',
        data: JSON.stringify({"transcript": textarea.value, "text": paragraph_text}),
        contentType: 'application/json;charset=UTF-8',
        cache: false,
        success: function(response) {end_reciting(response)}
    });
}


function replace_first_child(new_elem) {
    curr_div.firstElementChild.remove();
    curr_div.prepend(new_elem);
}

function start_reciting(id) {
    if (is_recognizing) {
        stop_listening()
    }

    paragraph_id = id;

    button = document.getElementById(`button_${id}`);
    button.className = 'send_button';
    button.innerHTML = 'Отправить';
    button.setAttribute('onclick', `send_text_to_server()`);

    mic_button = document.getElementById(`mic_${id}`);
    mic_button.style.display = 'block';

    curr_div = document.getElementById(`paragraph_${id}`);
    paragraph_text = curr_div.firstElementChild.innerHTML

    textarea = document.createElement('textarea')
    textarea.id = `textarea_${id}`

    replace_first_child(textarea)
}

function end_reciting(difference_html) {
    if (is_recognizing) {
        stop_listening()
    }

    let diff_table = document.createElement('div');
    diff_table.innerHTML = difference_html;

    replace_first_child(diff_table);

    button.className = 'start_button';
    button.innerHTML = 'Закрыть';
    button.setAttribute('onclick', `send_delete_signal()`);

    mic_button.style.display = 'none';
}

function close_block(article_is_empty) {
    if (article_is_empty) {
        let ending_label = document.createElement('h1')
        ending_label.innerHTML = 'Отлично! Вы всё выполнили.';

        replace_first_child(ending_label)

        button.setAttribute('onclick', `return_to_home_page()`);
    }
    else {
        curr_div.remove()
        let next_block = document.getElementById(`paragraph_${paragraph_id + 1}`)

        if (next_block) {
            next_block.className = ''
        }
    }
}

function return_to_home_page() {
    url = '/';
    window.open(url, '_self');
}

function start_listening() {
    listening_animation = document.getElementById(`loadFacebookG_${paragraph_id}`);
    listening_animation.style.display = 'flex';

    mic_button.setAttribute('onclick', `stop_listening()`);
    mic_button.className = 'mic_listening';

    recognize_speech(paragraph_text, textarea);
}


function stop_listening() {
    listening_animation.style.display = 'none';

    mic_button.setAttribute('onclick', `start_listening(${paragraph_id})`);
    mic_button.className = 'mic_button';

    stop_recognition();
}


async function recognize_speech(paragraph_text, field_to_save) {
    recognition = new speechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 3;
    recognition.lang = 'ru-RU';

    is_recognizing = true
    recognition.start();

    let non_final_transcript_len = 0

    recognition.onresult = (event) => {
        var last = event.results.length - 1;

        if (event.results[last].isFinal && event.results[last][0].confidence >= 0.7) {
            field_to_save.value += event.results[last][0].transcript + ' ';
        }
    }

    recognition.onend = () => {
        if (is_recognizing) {
            recognition.start();
        }
    }
}


function stop_recognition() {
    is_recognizing = false;
    recognition.stop();
}
