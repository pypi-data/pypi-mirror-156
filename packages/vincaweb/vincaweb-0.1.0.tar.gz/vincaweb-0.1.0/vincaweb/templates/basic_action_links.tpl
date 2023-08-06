<head>
<script>
window.addEventListener('resize',function(e){location.reload(true)});
function tell_server_delete_card(id) {
        var xhttp = new XMLHttpRequest();
        xhttp.open('GET', '/delete/'.concat(id), true)
        xhttp.send()
};
function toggle_filters_visible() {
        var xhttp = new XMLHttpRequest();
        if (filters_container.style.display=='flex') {
                xhttp.open('GET', '/set_session_param/advanced_filters_visible/False', true)
                filters_container.style.display = 'none';
                filters_button.textContent = 'filters ▼'
        } else if (filters_container.style.display=='none') {
                xhttp.open('GET', '/set_session_param/advanced_filters_visible/True', true)
                filters_container.style.display = 'flex';
                filters_button.textContent = 'filters ▲'
        }
        xhttp.send()
}
</script>
</head>



<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1" />

<body style="background-color:#cfc">
<div id="master" style="width: 90vw; height: calc(100vh - 10vw); margin:5vw 5vw auto auto; overflow: hidden">
<div id="banner">
<div id="buttons" style="display: flex; margin:0 auto; justify-content: center">
<button type="button" style="margin: 0 6px; padding: 1vmin; font-size: 20px" onclick="window.location.href = '/review_all'">review</button>
<button type="button" style="margin: 0 6px; padding: 1vmin; font-size: 20px" onclick="window.location.href = '/create/basic'">+ new card</button>
<button type="button" style="margin: 0 6px; padding: 1vmin; font-size: 20px" onclick="window.location.href = '/statistics'">statistics</button>
<button type="button" style="margin: 0 6px; padding: 1vmin; font-size: 20px" onclick="if(confirm('permanently remove deleted cards?')) {window.location.href = '/purge'}">purge</button>
</div>
<script>buttons.style["flex-direction"] = (screen.width < 450 ? "column" : "row")</script>
<div style="width:100%; height: 15"></div>
<div id="searchrow" style="display: flex; flex-direction: row; justify-content: center; align-items: center">
  <span style="font-size: 22px">search:</span>
  <input type="search" style="font-size: 22px; margin: 0 6px; max-width: 50%" name="search" value="{{search or ''}}" onchange="window.location.href = '/set_session_param/search/'.concat(this.value)">
  <button id="filters_button" type="button" style="padding: 3px; font-size: 22px" onclick="toggle_filters_visible()">filters {{'▲' if advanced_filters_visible else '▼'}}</button>
</div>
<div style="width:100%; height: 15"></div>
  <div id="filters_container" style="justify-content:left; flex-flow: column; display:{{'flex' if advanced_filters_visible else 'none'}};">
  <table frame="box" style="margin:0 6px; display: flex; align-items: center; background-color: #fff">
  <tr>
  <td align='right'>created_after:</td>
  <td>
  <input type="date" name="created_after" id="created_after" value={{created_after}}
        onchange="window.location.href = '/set_session_param/created_after/'.concat(created_after.value)">
  </td>
  </tr>
  <tr>
  <td align='right'>created_before:</td>
  <td>
  <input type="date" name="created_before" id="created_before" value={{created_before}}
        onchange="window.location.href = '/set_session_param/created_before/'.concat(created_before.value)">
  </td>
  </tr>

  <tr>
  <td align='right'>due_after:</td>
  <td>
  <input type="date" name="due_after" id="due_after" value={{due_after}}
        onchange="window.location.href = '/set_session_param/due_after/'.concat(due_after.value)">
  </td>
  </tr>

  <tr>
  <td align='right'>due_before:</td>
  <td>
  <input type="date" name="due_before" id="due_before" value={{due_before}}
        onchange="window.location.href = '/set_session_param/due_before/'.concat(due_before.value)">
  </td>
  </tr>

  <tr>
  </table>
  <table frame="box" style="margin:0 6px; display: flex; align-items: center; background-color: #fff">
  <tr>
  <td align='right'>deleted:</td>
  <td>
  <input type='radio' name='deleted_filter' value='yes' {{'checked' if deleted == True else ''}}
         onclick="window.location.href = '/set_session_param/deleted/True'"> yes
  <input type='radio' name='deleted_filter' value='no'  {{'checked' if deleted == False  else ''}}
         onclick="window.location.href = '/set_session_param/deleted/False'"> no
  <input type='radio' name='deleted_filter' value='any' {{'checked' if deleted == None else ''}}
         onclick="window.location.href = '/set_session_param/deleted/None'"> any
  </td>
  </tr><tr>
  <td align='right'>due:</td>
  <td>
  <input type='radio' name='due_filter' value='yes' {{'checked' if due == True else ''}}
         onclick="window.location.href = '/set_session_param/due/True'"> yes
  <input type='radio' name='due_filter' value='no'  {{'checked' if due == False  else ''}}
         onclick="window.location.href = '/set_session_param/due/False'"> no
  <input type='radio' name='due_filter' value='any' {{'checked' if due == None else ''}}
         onclick="window.location.href = '/set_session_param/due/None'"> any
  </td>
  </tr><tr>
  <td align='right'>new:</td>
  <td>
  <input type='radio' name='new_filter' value='yes' {{'checked' if new == True else ''}}
         onclick="window.location.href = '/set_session_param/new/True'"> yes
  <input type='radio' name='new_filter' value='no'  {{'checked' if new == False else ''}}
         onclick="window.location.href = '/set_session_param/new/False'"> no
  <input type='radio' name='new_filter' value='any' {{'checked' if new == None else ''}}
         onclick="window.location.href = '/set_session_param/new/None'"> any
  </td>
  </tr><tr>
  <td align='right'>images:</td>
  <td>
  <input type='radio' name='contains_images_filter' value='yes' {{'checked' if contains_images == True else ''}}
         onclick="window.location.href = '/set_session_param/contains_images/True'"> yes
  <input type='radio' name='contains_images_filter' value='no'  {{'checked' if contains_images == False else ''}}
         onclick="window.location.href = '/set_session_param/contains_images/False'"> no
  <input type='radio' name='contains_images_filter' value='any' {{'checked' if contains_images == None else ''}}
         onclick="window.location.href = '/set_session_param/contains_images/None'"> any
  </td>
  </tr>
  </table>
  <table frame="box" style="margin:0 6px; display: flex; align-items: center; background-color: #fff">  <tr>
  <td align='left'>
  sort: 
  <select name="sort_by" onchange="window.location.href='/set_session_param/sort_by/'.concat(this.value)">
  {% for criterion in ('seen','created','due','time','random'): %}
    <option {{"selected = 'selected'" if sort_by==criterion else ''}}>{{criterion}}</option>
  {% endfor %}
  </select>
  </td>
  </tr>
  <tr>
  <td align='left'> tag:
  <select id="has_tag" name="has_tag" onchange="window.location.href='/set_session_param/has_tag/'.concat(has_tag.value)">
  {% for tag in ('any','geometry','his',): %}
    <option {{"selected = 'selected'" if has_tag==tag else ''}}>{{tag}}</option>
  {% endfor %}
  </select>
  </td>
  </tr>
  <tr>
  <td align='left'> type:
  <select id="card_type" name="card_type" onchange="window.location.href='/set_session_param/card_type/'.concat(this.value)">
  {% for type in ('any','basic','verses',): %}
    <option {{"selected = 'selected'" if card_type==type else ''}}>{{type}}</option>
  {% endfor %}
  </select>
  </td>
  </tr>
  </table>
  </div>
<script>filters_container.style["flex-direction"] = (screen.width < 450 ? "column" : "row")</script>
<script>filters_container.style["justify-content"] = (screen.width < 450 ? "left" : "center")</script>
</div>


<div style="width:100%; height: 15"></div>

<div id='cz' style="border: 1px; overflow: auto">
<table style="margin: 0 auto; border-spacing: 1vmin;"> 
{% for card in cards: %}
  <tr id="{{'row' + card.id}}" style="vertical-align: top; {{'text-decoration: line-through' if card.deleted else ''}}"  >
  <script>alert(document.getElementById(r))</script>
  <td><button onclick="tell_server_delete_card('{{card.id}}'); var r = document.getElementById({{'\'' + 'row' + card.id + '\''}}); if(r.style['text-decoration']=='line-through'){r.style['text-decoration']=''}else{r.style['text-decoration']='line-through'}" style="border-radius: 50%; background-color: #fee; color: #900; width: 32px; height: 32px; margin: 0 auto;" >✗</button></td>
  <td><button style="border-radius: 50%; background-color: #aaf; width: 32px; height: 32px">{{card.due_date.relative_date}}</button></td>
  <td style="font-size: 18px; margin: 0 auto;">
  {{card.front_text.splitlines()[0] or '(blank)'}}
  </td>
  <td><button style="border-radius: 50%; background-color: #aaf; width: 32px; height: 32px" onclick="window.location.href = '/preview/{{card.id}}'">👁</button></td>
  <td><button style="border-radius: 50%; background-color: #FF0; width: 32px; height: 32px" onclick="window.location.href = '/edit/{{card.id}}'">✎</button></td>
  </tr>
{% endfor %}
</table>
</div>
<script>cz.style["height"] = master.offsetHeight - banner.offsetHeight</script>
</div>
</body>

</meta>

