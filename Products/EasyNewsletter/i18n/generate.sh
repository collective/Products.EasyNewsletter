#!/bin/sh

rm ../skins/EasyNewsletter/._*
rm ../Extensions/._*
rm ../content/._*
rm ../interfaces/._*
rm ../._*
rm ./._*

i18ndude rebuild-pot --pot easynewsletter.pot --create EasyNewsletter --merge generated.pot --merge2 extra.pot ..
i18ndude sync --pot easynewsletter.pot easynewsletter-de.po
i18ndude sync --pot easynewsletter-plone.pot easynewsletter-plone-de.po