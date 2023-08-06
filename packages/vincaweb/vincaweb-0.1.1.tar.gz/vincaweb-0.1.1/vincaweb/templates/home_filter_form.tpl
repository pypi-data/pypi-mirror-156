  search:
  <input type="search" name="search">
  <button type="button" onclick="window.location.href = '/set_session_param/advanced_filters_visible/{{not advanced_filters_visible}}'">{{'hide' if advanced_filters_visible else 'show'}} advanced filters {{'▲' if advanced_filters_visible else '▼'}}</button>
  <br>
  <br>
  <table border=1px style="display:{{'block' if advanced_filters_visible else 'none'}};">
  <tr><td>
  <table>
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
  </td><td>
  <table>
  <tr>
  <td align='right'>deleted:</td>
  <td>
  <input type='radio' name='deleted_filter' value='yes' {{'checked' if deleted == 'yes' else ''}}
         onclick="window.location.href = '/set_session_param/deleted/yes'"> yes
  <input type='radio' name='deleted_filter' value='no'  {{'checked' if deleted == 'no'  else ''}}
         onclick="window.location.href = '/set_session_param/deleted/no'"> no
  <input type='radio' name='deleted_filter' value='any' {{'checked' if deleted == 'any' else ''}}
         onclick="window.location.href = '/set_session_param/deleted/any'"> any
  </td>
  </tr><tr>
  <td align='right'>due:</td>
  <td>
  <input type='radio' name='due_filter' value='yes' {{'checked' if due == 'yes' else ''}}
         onclick="window.location.href = '/set_session_param/due/yes'"> yes
  <input type='radio' name='due_filter' value='no'  {{'checked' if due == 'no'  else ''}}
         onclick="window.location.href = '/set_session_param/due/no'"> no
  <input type='radio' name='due_filter' value='any' {{'checked' if due == 'any' else ''}}
         onclick="window.location.href = '/set_session_param/due/any'"> any
  </td>
  </tr><tr>
  <td align='right'>new:</td>
  <td>
  <input type='radio' name='new_filter' value='yes' {{'checked' if new == 'yes' else ''}}
         onclick="window.location.href = '/set_session_param/new/yes'"> yes
  <input type='radio' name='new_filter' value='no'  {{'checked' if new == 'no'  else ''}}
         onclick="window.location.href = '/set_session_param/new/no'"> no
  <input type='radio' name='new_filter' value='any' {{'checked' if new == 'any' else ''}}
         onclick="window.location.href = '/set_session_param/new/any'"> any
  </td>
  </tr><tr>
  <td align='right'>contains images:</td>
  <td>
  <input type='radio' name='contains_images_filter' value='yes' {{'checked' if contains_images == 'yes' else ''}}
         onclick="window.location.href = '/set_session_param/contains_images/yes'"> yes
  <input type='radio' name='contains_images_filter' value='no'  {{'checked' if contains_images == 'no'  else ''}}
         onclick="window.location.href = '/set_session_param/contains_images/no'"> no
  <input type='radio' name='contains_images_filter' value='any' {{'checked' if contains_images == 'any' else ''}}
         onclick="window.location.href = '/set_session_param/contains_images/any'"> any
  </td>
  </tr><tr>
  <td align='right'>card_type:</td>
  <td>
  <input type='radio' name='card_type_filter' value='basic' {{'checked' if card_type == 'basic' else ''}}
         onclick="window.location.href = '/set_session_param/card_type/basic'"> basic
  <input type='radio' name='card_type_filter' value='verses'  {{'checked' if card_type == 'verses'  else ''}}
         onclick="window.location.href = '/set_session_param/card_type/verses'"> verses
  <input type='radio' name='card_type_filter' value='any' {{'checked' if card_type == 'any' else ''}}
         onclick="window.location.href = '/set_session_param/card_type/any'"> any
  </td>
  </tr>
  </table>
  <td>
  <table>
  <tr>
  <td align='left'>
  sort by: 
  <select name="sort_by" onchange="window.location.href='/set_session_param/sort_by/'.concat(this.value)">
  {% for criterion in ('seen','created','due','time','random'): %}
    <option {{"selected = 'selected'" if sort_by==criterion else ''}}>{{criterion}}</option>
  {% endfor %}
  </select>
  </td>
  </tr>
  <tr>
  <td align='left'> has tag:
  <select id="has_tag" name="has_tag" onchange="window.location.href='/set_session_param/has_tag/'.concat(has_tag.value)">
  {% for tag in ('ANY','geometry','his',): %}
    <option {{"selected = 'selected'" if has_tag==tag else ''}}>{{tag}}</option>
  {% endfor %}
  </select>
  </td>
  </tr>
  <tr><td>
  <input type='checkbox' name='show_private' value='yes' {{'checked' if show_private else ''}}
        onclick="window.location.href = '/set_session_param/show_private/{{not show_private}}'"> show private
  </td></tr><tr><td>
  <input type='checkbox' name='invert' value='yes' {{'checked' if invert else ''}}
        onclick="window.location.href = '/set_session_param/invert/{{not invert}}'"> invert
  </td></tr><tr><td>
  <input type='checkbox' name='hide_backsides' value='yes' {{'checked' if hide_backsides else ''}} 
        onclick="window.location.href = '/set_session_param/hide_backsides/{{not hide_backsides}}'"> hide backsides
  </td></tr>
  </table>
  </td>
  </tr>
  </table>
