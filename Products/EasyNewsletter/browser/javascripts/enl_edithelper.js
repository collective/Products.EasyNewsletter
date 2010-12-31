/*jq(document).ready(function(init_enl_tabs){
  jq("#archetypes-fieldname-header").insertAfter("\
    <ul id=\"enl_content_tabs\" class=\"enl_tabs\">\
      <li><a href=\"#\">Tab 1</a></li>\
      <li><a href=\"#\">Tab 2</a></li>\
      <li><a href=\"#\">Tab 3</a></li>\
    </ul>")
  .after("<div id=\"enl_content_panes\" class=\"enl_panes\"></div>")
  .append(jq("#archetypes-fieldname-text"))
  .append(jq("#archetypes-fieldname-header"))
  .append(jq("#archetypes-fieldname-footer"));
  init_enl_tabs();
});

function init_enl_tabs(){  
  jq("ul.enl_tabs").tabs("div.enl_panes > div");
}*/
