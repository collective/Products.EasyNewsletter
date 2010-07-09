import re
PROJECTNAME = "EasyNewsletter"

EMAIL_RE = re.compile(r"(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)",re.IGNORECASE)

DEFAULT_TEMPLATE = """
<p>&gt;&gt;PERSOLINE&gt;&gt;Dear {% subscriber-fullname %}</p>
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
"""
