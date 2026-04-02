from hatchling.metadata.plugin.interface import MetadataHookInterface


class CustomMetadataHook(MetadataHookInterface):
    PLUGIN_NAME = "custom"

    def update(self, metadata: dict) -> None:
        with open("README.md", encoding="utf-8") as f:
            readme = f.read()
        with open("CHANGELOG.md", encoding="utf-8") as f:
            changelog = f.read()
        metadata["readme"] = {
            "content-type": "text/markdown",
            "text": readme + "\n\n" + changelog,
        }
