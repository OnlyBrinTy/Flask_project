ajax();

function href(bt_num) {
  url = `/ActionPage?param=${bt_num}`;
  window.open(url, '_self');
}

function filling(outp_data) {
  var author_1 = document.getElementById('a1');
  var author_2 = document.getElementById('a2');
  var author_3 = document.getElementById('a3');
  var author_4 = document.getElementById('a4');
  var author_5 = document.getElementById('a5');
  var author_6 = document.getElementById('a6');
  var author_7 = document.getElementById('a7');
  var author_8 = document.getElementById('a8');
  var author_9 = document.getElementById('a9');
  var author_10 = document.getElementById('a10');
  var title_1 = document.getElementById('t1');
  var title_2 = document.getElementById('t2');
  var title_3 = document.getElementById('t3');
  var title_4 = document.getElementById('t4');
  var title_5 = document.getElementById('t5');
  var title_6 = document.getElementById('t6');
  var title_7 = document.getElementById('t7');
  var title_8 = document.getElementById('t8');
  var title_9 = document.getElementById('t9');
  var title_10 = document.getElementById('t10');

  for (let i = 1; i < 11; i++) {
    eval(`author_${i}`).innerHTML = `${outp_data.DATA_author[i - 1]}`;
  }
  for (let i = 1; i < 11; i++) {
    eval(`title_${i}`).innerHTML = `${outp_data.DATA_title[i - 1]}`;
  }
}

function afterLoad() {
  document.getElementById('loading').style.display = 'none';
  document.getElementById('header').style.display = 'block';
  document.getElementById('pannel').style.display = 'block';
}

function ajax() {
  $.ajax({ 
    type: 'POST',
    url: '/DATA_authors_and_titles',
    contentType: 'application/json;charset=UTF-8',
    success : function(outp_data)
    {
      filling(outp_data);
      afterLoad();
    }
  });
}