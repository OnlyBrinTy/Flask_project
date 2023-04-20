var speechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
var listening_animation;
var is_recognizing;
var paragraph_text;
var paragraph_id;
var is_reciting;
var mic_button;
var textarea;
var curr_div;
var button;

function send_delete_signal(local_p_id) {
    $.ajax({
        type: 'POST',
        url: '/DATA_delete_paragraph',
        data: JSON.stringify({'paragraph_id': local_p_id, 'article_id': window.location.pathname.slice(1)}),        contentType: 'application/json;charset=UTF-8',
        complete: function() {close_block(local_p_id)}
    });
}

function send_text_to_server() {
    $.ajax({
        type: 'POST',
        url: '/DATA_text_from_speech',
        data: JSON.stringify({"transcript": textarea.value, "text": paragraph_text}),
        contentType: 'application/json;charset=UTF-8',
        success: function(response) {end_reciting(response)}
    });
}

function replace_first_child(new_elem) {
    curr_div.firstElementChild.remove();
    curr_div.prepend(new_elem);
}

function start_reciting(id) {
    if (is_reciting) {
        if (is_recognizing) {
            stop_listening()
        }

        return_to_initial_state()
    }

    is_reciting = true
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

function return_to_initial_state() {
    mic_button.style.display = 'none';

    button.className = 'start_button';
    button.innerHTML = 'Начать';
    button.setAttribute('onclick', `start_reciting(${paragraph_id})`);

    deleted_paragraph = document.createElement('a')
    deleted_paragraph.id = paragraph_id
    deleted_paragraph.innerHTML = paragraph_text

    replace_first_child(deleted_paragraph)
}

function end_reciting(difference_html) {
    if (is_recognizing) {
        stop_listening()
    }

    is_reciting = false

    let diff_table = document.createElement('div');
    diff_table.innerHTML = difference_html;

    replace_first_child(diff_table);

    button.className = 'start_button';
    button.innerHTML = 'Закрыть';
    button.setAttribute('onclick', `send_delete_signal(${paragraph_id})`);

    mic_button.style.display = 'none';
}

function close_block(local_p_id) {
    curr_div = document.getElementById(`paragraph_${local_p_id}`);
    let last_paragraph = document.getElementById('tasks_panel').childElementCount == 1;

    if (last_paragraph) {
        let ending_label = document.createElement('h1')
        ending_label.innerHTML = 'Отлично! Вы всё выполнили.';

        replace_first_child(ending_label)

        button.setAttribute('onclick', `return_to_home_page()`);
    }
    else {
        let next_block = document.getElementById(`paragraph_${local_p_id + 1}`)

        if (next_block && curr_div.className == '') {
            next_block.className = ''
        }

        curr_div.remove()
    }

    curr_div = document.getElementById(`paragraph_${paragraph_id}`);
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
