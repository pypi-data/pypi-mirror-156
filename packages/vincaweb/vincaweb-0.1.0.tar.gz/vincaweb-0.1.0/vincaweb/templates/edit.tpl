<meta name="viewport" content="width=device-width, initial-scale=1">
<body style="background-color: #cfc">
<div style="width: 85vw; margin: 5vw 5vw auto auto;">
<script>
function create_verses() {
  back_text.style.display = 'none';
  qa_divide.style.display = 'none';
  front_text.rows = 15;
  front_text.placeholder = "Lines will be quizzed one by one:\n\nTo be, or not to be: that is the question:\nWhether 'tis nobler in the mind to suffer\nThe slings and arrows of outrageous fortune,\nOr to take arms against a sea of troubles,\nAnd by opposing end them? To die: to sleep;\nNo more; and by a sleep to say we end\nThe heartache and the thousand natural shocks\nThat flesh is heir to, 'tis a consummation\nDevoutly to be wished. To die, to sleep;\nTo sleep: perchance to dream: ay there's the rub;\nFor in that sleep of death what dreams may come\nWhen we have shuffled off this mortal coil,\nMust give us pause...";
}
function create_basic() {
  back_text.style.display = 'block';
  qa_divide.style.display = 'block';
  front_text.placeholder = "Question\n\nWhy did Marcus Aurelius thank the gods for not having had greater talent in rhetoric?";
  back_text.placeholder = "Answer\n\nSuch pride and power may have diverted him from philosophy.";
  front_text.rows = 7;
}
</script>

<form action='/edit/{{id}}' method='POST'>

<div style="font-size: 20px; text-align: center; width: 100%">
<input id="basic_radio" type="radio" name="verses" value=0  onclick="create_basic()" checked>
<label for="basic_radio"  style="padding:10px 0">basic card</label>
<input id="verses_radio" type="radio" name="verses" value=1 onclick="create_verses()">
<label for="verses_radio" style="padding:10px 0">verses card</label>
<input type="submit" value="save" name="save" style="font-size: 20px; margin: 5px 10px; padding: 10px;">
<button type="button" style="font-size: 20px; padding: 10px; margin: 5px 10px;" onclick="window.location.href = '/delete/{{id}}'">cancel</button>
</div>


<div style="width: 100%; height:10px;"></div>
<textarea name="front_text" id="front_text" rows='7' style="width: 100%">{{front_text or ''}}</textarea>
<div id='qa_divide' style="width: 100%; height:calc(1em - 5px);"></div>
<textarea id="back_text" name="back_text" rows='7' style="width: 100%">{{back_text or ''}}</textarea>
<script>create_basic()</script>
<div style="margin: 20px 0; width: 100%"><hr></div>
tags: ctrl+click to select multiple
<select name="tags" style="width: 100%;" onchange="if(new_tag.selected && new_tag.textContent=='+ NEW TAG'){var nt =  prompt('New tag: '); new_tag.textContent=nt; new_tag.value=nt;}" multiple>
<option id='new_tag' value='new_tag'         onclick="if(new_tag.textContent=='+ NEW TAG'){var nt =  prompt('New tag: '); new_tag.textContent=nt; new_tag.value=nt;}">+ NEW TAG</option>
<option name="this">this</option>
<option>that</option>
</select>
</form>


</div>
</body>
</meta>
