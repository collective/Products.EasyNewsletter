PROJECTNAME = "EasyNewsletter"

DEFAULT_TEMPLATE = """
<tal:block tal:content="structure context/getHeader" />

<tal:block tal:repeat="object context/queryCatalog">
    <h1 tal:content="object/Title">Title</h1>

    <p>
        <span tal:content="object/Description">Description</span>
    </p>
    <p>
        <a tal:attributes="href object/getURL">Please read on.</a>
    </p>
</tal:block>

<tal:block tal:repeat="subtopic context/getSubTopics">
    <h1 tal:content="subtopic/Title">Title</h1>

    <tal:block tal:repeat="object subtopic/queryCatalog">
        <h2 tal:content="object/Title">Title</h2>
  
        <p>
            <span tal:content="object/Description">Description</span>
        </p>
        <p>
            <a tal:attributes="href object/getURL">Please read on.</a>
        </p>
    </tal:block>
</tal:block>

<tal:block tal:content="structure context/getFooter" />

<hr />
<p>
    <a href="{% unsubscribe-link %}">Click here to unscubsribe</a>
</p>
"""