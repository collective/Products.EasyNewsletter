from plone.app.upgrade.utils import loadMigrationProfile


def reload_gs_profile(context):
    loadMigrationProfile(
        context,
        "profile-Products.EasyNewsletter:default",
    )
