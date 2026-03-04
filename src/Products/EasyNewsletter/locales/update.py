import os
import subprocess

package_name = "Products.EasyNewsletter"
# domain = package_name
package_domain = "Products.EasyNewsletter"
locale_path = os.path.dirname(os.path.realpath(__file__))
target_path = os.path.abspath(os.path.join(locale_path, os.pardir))
i18ndude = "./bin/i18ndude"


def locale_folder_setup(domain=None):
    languages = [
        d
        for d in os.listdir(locale_path)
        if os.path.isdir(os.path.join(locale_path, d)) and d != "__pycache__"
    ]
    for lang in languages:
        lc_message_dir_path = os.path.join(locale_path, lang, "LC_MESSAGES")
        if not os.path.isdir(lc_message_dir_path):
            os.mkdir(lc_message_dir_path)
        domain_po_file_path = os.path.join(locale_path, lang, "LC_MESSAGES", domain + ".po")
        if not os.path.isfile(domain_po_file_path):
            cmd = "msginit --locale={0} --input={2}/manual.pot --output={2}/{0}/LC_MESSAGES/{1}.po".format(  # NOQA: E501
                lang, domain, locale_path
            )
            subprocess.call(cmd, shell=True)


def _rebuild(domain=None, target_path=None):
    print(f"rebuild-pot domain: {domain} target_path: {target_path}")
    cmd = f"{i18ndude} rebuild-pot --no-wrap --pot {locale_path}/{domain}.pot --create {domain} {target_path} --merge {locale_path}/manual.pot"
    if domain == package_domain:
        cmd += f" --merge {locale_path}/manual.pot"
    subprocess.call(cmd, shell=True)


# def _filter(domain=None, filterdomain=u'plone'):
#     cmd = '{0} filter {1}.pot {2}/{3}.pot'.format(
#         i18ndude,
#         filterdomain,
#         locale_path,
#         domain,
#     )
#     subprocess.call(
#         cmd,
#         shell=True,
#     )


def _sync(domain=None):
    print(f"sync domain: {domain}")
    cmd = (
        f"{i18ndude} sync --pot {locale_path}/{domain}.pot {locale_path}/**/LC_MESSAGES/{domain}.po"
    )
    subprocess.call(cmd, shell=True)


def update_locale():

    locale_folder_setup(domain=package_domain)
    _rebuild(domain=package_domain, target_path=target_path)
    _sync(domain=package_domain)

    # also build locales für domain: plone
    locale_folder_setup(domain="plone")
    _rebuild(domain="plone", target_path=os.path.join(target_path, "profiles"))
    # _filter(domain=package_domain, filterdomain='plone')
    _sync(domain="plone")
