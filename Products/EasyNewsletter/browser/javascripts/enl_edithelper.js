/*
jq(document).ready(function(){
  jq("#archetypes-fieldname-header").before("\
    <ul id=\"enl_content_tabs\" class=\"enl_tabs\">\
      <li><a href=\"#\">Tab 1</a></li>\
      <li><a href=\"#\">Tab 2</a></li>\
      <li><a href=\"#\">Tab 3</a></li>\
    </ul>");
  jq("#enl_content_tabs").after("\
    <div id=\"enl_content_panes\" class=\"enl_panes\">\
    </div>");

  jq("#enl_content_panes").append(jq("#archetypes-fieldname-text"));
  jq("#enl_content_panes").append(jq("#archetypes-fieldname-header"));
  jq("#enl_content_panes").append(jq("#archetypes-fieldname-footer"));
  jq("ul.enl_tabs").tabs("div.enl_panes > div");
});
*/
