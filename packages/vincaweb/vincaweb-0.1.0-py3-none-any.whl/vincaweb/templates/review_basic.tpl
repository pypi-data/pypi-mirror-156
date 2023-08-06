<meta name="viewport" content="width=device-width, initial-scale=1">
<head>
<script type='text/javascript'>
<!-- We flip the card by hiding the flip button and showing the backside -->
  function flip() {
    backside.style.display="block";
    flip_button.style.display="none";
    good_button.focus();
  }
  function default_action() {
    if(backside.style.display=="none"){
      flip(); //flip the card if we haven't yet
    } else {
      grade('3'); // otherwise grade the card as good
    }
  }
  function delete_card(){window.location.href = "/delete/{{card.id}}/callback"}
  function edit(){       window.location.href = "/edit/{{card.id}}"}
  function quit(){       window.location.href = "/home"}
  function grade(key){   window.location.href = "/grade/".concat(key)}
  function keyListener(event){ 
    event = event || window.event; //capture the event, and ensure we have an event
    var key = event.key || event.which || event.keyCode; //find the key that was pressed
    if(key=='q'){
      quit()
    } else if(key=='e'){
      edit()
    } else if(key=='d'){
      delete_card()
    } else if(key=='1' || key == '2' || key == '3' || key == '4'){
      grade(key)
    }
  }
  document.addEventListener('keydown', keyListener);
  document.addEventListener('click', function(e){default_action()}, true);
</script>
</head>

<body style="background-color: #cfc">
<div style="width: 90vw; margin: 5vw 5vw auto auto;">
<p style="font-size: 22px">{{card.front_text}}</p>
<button id=flip_button type='button' onclick='flip()' style="padding: 9px; font-size: 22px;" autofocus>Answer<br><span style="font-size: 15px">spacebar or click anywhere</span></button>

<div id='backside' style="display:none">
<p style="font-size: 22px">{{card.back_text}}</p>

<div id="buttons" style="display:flex; flex-flow: row wrap; justify-content: space-between;">
<button type="button" style="width: 32%; padding: 15px; font-size: 21px" onclick="delete_card()">✗ delete (d)</button>
<button type="button" style="width: 32%; padding: 15px; font-size: 21px" onclick="edit()">✎ edit (e)</button>
<button type="button" style="width: 32%; padding: 15px; font-size: 21px" onclick="quit()">⏎ quit (q)</button>
<div style="height: 12px; width: 100%;"></div>
<button type="button" style="width: 24%; padding: 15px; font-size: 21px" onclick="grade('1')">again (1)</button>
<button type="button" style="width: 24%; padding: 15px; font-size: 21px" onclick="grade('2')">hard (2)<br>+{{card.history.hypothetical_due_date('hard', relative_date=True)}}</button>
<button type="button" style="width: 24%; padding: 15px; font-size: 21px" onclick="grade('3')" id="good_button">good (3)<br>+{{card.history.hypothetical_due_date('good', relative_date=True)}}</button>
<button type="button" style="width: 24%; padding: 15px; font-size: 21px" onclick="grade('4')">easy (4)<br>+{{card.history.hypothetical_due_date('easy',relative_date=True)}}</button>
</div>
</div>
</body>
</meta>
