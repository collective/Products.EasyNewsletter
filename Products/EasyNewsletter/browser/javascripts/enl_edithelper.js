var jq = $;

jq(document).ready(function(){
    var members = "#archetypes-fieldname-ploneReceiverMembers";
    var groups = "#archetypes-fieldname-ploneReceiverGroups";

	if (jq("#sendToAllPloneMembers").attr('checked')){
		jq(members).css('visibility', 'hidden');
		jq(groups).css('visibility', 'hidden');
	}else{
		jq(members).css('visibility', 'visible');
		jq(groups).css('visibility', 'visible');
	}
	jq("#sendToAllPloneMembers").click(function (){
		if (jq(this).attr('checked')){
			jq(members).css('visibility', 'hidden');
			jq(groups).css('visibility', 'hidden');
		}else{
			jq(members).css('visibility', 'visible');
			jq(groups).css('visibility', 'visible');
		}
	});
});

/*
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
*/


/*
function init_enl_tabs(){
  jq("ul.enl_tabs").tabs("div.enl_panes > div");
}*/
