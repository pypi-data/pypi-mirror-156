# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS bundles for oarepo-generated-ui.

You include one of the bundles in a page like the example below (using
``base`` bundle as an example):

 .. code-block:: html

    {{ webpack['base.js']}}

"""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={},
            dependencies={
                "@babel/runtime": "^7.9.0",
                "@ckeditor/ckeditor5-build-classic": "^16.0.0",
                "@ckeditor/ckeditor5-react": "^2.1.0",
                "formik": "^2.1.0",
                "i18next": "^20.3.0",
                "i18next-browser-languagedetector": "^6.1.0",
                "luxon": "^1.23.0",
                "path": "^0.12.7",
                "prop-types": "^15.7.2",
                "react-copy-to-clipboard": "^5.0.0",
                "react-dnd": "^11.1.0",
                "react-dnd-html5-backend": "^11.1.0",
                "react-dropzone": "^11.0.0",
                "react-i18next": "^11.11.0",
                "react-invenio-deposit": "^0.19.0",
                "react-invenio-forms": "^0.10.0",
                "react-searchkit": "^2.0.0",
                "yup": "^0.32.0",
            },
            devDependencies={
            },
            aliases={
                # TODO: needed until resolution of https://github.com/inveniosoftware/invenio-search-ui/issues/130
                "@translations/invenio_app_rdm": "translations/oarepo_ui",
                '@translations/oarepo_ui': 'translations/oarepo_ui',
                "../../theme.config$": "less/theme.config",
                "../../less/site": "less/site",
                "../../less": "less",
                "themes/oarepo": "less/invenio_theme/theme",
                "@less/oarepo_ui": "less/oarepo_ui",
            }
        )
    },
)
