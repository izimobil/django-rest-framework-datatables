Changelog
=========

Version 0.7.2 (2024-06-14):
---------------------------

- Django 5.0 and 5.1 support
- Allow overriding queryset.count() with two additional methods

Many thanks to all the contributors on this release !

Version 0.7.1 (2024-03-06):
---------------------------

- Django 4.2 support
- Dependencies versions updates
- Fixed deprecation warnings on tests

Many thanks to all the contributors on this release !

Version 0.7.0 (2021-12-09):
---------------------------

- Django 4.0 compatibility
- Added global search support to YADCFModelMultipleChoiceFilter
- Various fixes on filters
- Various fixes on pagination
- Fixed / improved documentation and examples

Many thanks to all the contributors on this release !

Version 0.6.0 (2021-02-09):
---------------------------

- Integration with django-filter
- Example of using yadcf and django-filter to create a multi-select column
- Fixed support for POST requests from datatables
- Some fixes on pagination

Many thanks to all the contributors on this release !

Version 0.5.2 (2020-04-10):
---------------------------

- Added support for POST requests from datatables
- Avoid extra count queries
- Handle dummy columns gracefully

Version 0.5.1 (2020-01-13):
---------------------------

- Added support for Django 3.0
- Added support for disabling pagination when the client requests it with length=-1 parameter
- Added optional column sorting to handle ties
- Minor code fixes

Version 0.5.0 (2019-03-31):
---------------------------

- Fixed total number of rows when view is using multiple filter back-ends
- New meta option ``datatables_extra_json`` on view for adding key/value pairs to rendered JSON
- Minor docs fixes

Version 0.4.1 (2018-11-16):
---------------------------

- Added support for Django 2.1 and DRF 3.9
- Updated README

Version 0.4.0 (2018-06-22):
---------------------------

- Added top level filtering for nested serializers
- Added multiple field filtering
- Added a ?keep= parameter that allows to bypass the filtering of unused fields
- Better detection of the requested format
- Fixed typo in Queryset.count() method name


Version 0.3.0 (2018-05-11):
---------------------------

- Added a serializer Meta option ``datatables_always_serialize`` that allows to specify a tuple of fields that should always be serialized in the response, regardless of what fields are requested in the Datatables request
- Optimize filters
- Use AND operator for column filtering instead of OR, to be consistant with the client-side behavior of Datatables

Version 0.2.1 (2018-04-11):
---------------------------

- This version replaces the 0.2.0 who was broken (bad setup.py)

Version 0.2.0 (2018-04-11):
---------------------------

- Added full documentation
- Removed serializers, they are no longer necessary, filtering of columns is made by the renderer

Version 0.1.0 (2018-04-10):
---------------------------

Initial release.
