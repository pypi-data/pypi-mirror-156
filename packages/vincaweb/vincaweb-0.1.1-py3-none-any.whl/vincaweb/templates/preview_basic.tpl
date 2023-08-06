<meta name="viewport" content="width=device-width, initial-scale=1">
<head>
<script type='text/javascript'>
<!-- We flip the card by hiding the flip button and showing the backside -->
  function delete_card(){window.location.href = "/delete/{{card.id}}"}
  function edit(){       window.location.href = "/edit/{{card.id}}"}
  function quit(){       window.location.href = "/home"}
  function keyListener(event){ 
    event = event || window.event; //capture the event, and ensure we have an event
    var key = event.key || event.which || event.keyCode; //find the key that was pressed
    if(key=='q'){
      quit()
    } else if(key=='e'){
      edit()
    } else if(key=='d'){
      delete_card()
    }
  }
  document.addEventListener('keydown', keyListener);
  document.addEventListener('click', function(e){quit()}, true);
</script>
</head>

<body style="background-color: #cfc">
<div style="width: 90vw; margin: 5vw 5vw auto auto;">
<p style="font-size: 22px">{{card.front_text}}</p>

<p style="font-size: 22px">{{card.back_text}}</p>

<div id="buttons" style="display:flex; flex-flow: row wrap; justify-content: space-between;">
<button type="button" style="width: 32%; padding: 15px; font-size: 21px" onclick="delete_card()">✗ delete (d)</button>
<button type="button" style="width: 32%; padding: 15px; font-size: 21px" onclick="edit()">✎ edit (e)</button>
<button type="button" style="width: 32%; padding: 15px; font-size: 21px" onclick="quit()">⏎ quit (q)</button>
</div>
</body>
</meta>
