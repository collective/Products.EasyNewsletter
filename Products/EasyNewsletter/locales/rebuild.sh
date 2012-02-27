#!/bin/bash
cd "`dirname $0`/.."
PRODUCT=EasyNewsletter

i18ndude rebuild-pot --pot locales/${PRODUCT}.pot --create $PRODUCT  .
i18ndude sync --pot locales/${PRODUCT}.pot locales/*/LC_MESSAGES/${PRODUCT}.po
for lang in $(find locales -mindepth 1 -maxdepth 1 -type d); do
    if test -d $lang/LC_MESSAGES; then
        msgfmt -o $lang/LC_MESSAGES/${PRODUCT}.mo $lang/LC_MESSAGES/${PRODUCT}.po
    fi
done
# Ok, now poedit is your friend!
    

