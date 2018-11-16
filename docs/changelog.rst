Changelog
=========

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
