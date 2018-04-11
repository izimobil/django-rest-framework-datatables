from rest_framework.renderers import JSONRenderer


class DatatablesRenderer(JSONRenderer):
    media_type = 'application/json'
    format = 'datatables'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        if data is None:
            return bytes()

        request = renderer_context['request']
        new_data = {}

        if 'recordsTotal' not in data:
            # pagination was not used, let's fix the data dict
            if 'results' in data:
                results = data['results']
                count = data['count'] if 'count' in data else len(results)
            else:
                results = data
                count = len(results)
            new_data['data'] = results
            view = renderer_context.get('view')
            if view and hasattr(view, '_datatables_filtered_count'):
                count = view._datatables_filtered_count
            if view and hasattr(view, '_datatables_total_count'):
                total_count = view._datatables_total_count
            else:
                total_count = count
            new_data['recordsFiltered'] = count
            new_data['recordsTotal'] = total_count
        else:
            new_data = data
        # add datatables "draw" parameter
        new_data['draw'] = int(request.query_params.get('draw', '1'))
        new_data = self._filter_unused_fields(request, new_data)

        return super(DatatablesRenderer, self).render(
            new_data, accepted_media_type, renderer_context
        )

    def _filter_unused_fields(self, request, result):
        cols = []
        i = 0
        while True:
            col = request.query_params.get('columns[%d][data]' % i)
            if col is None:
                break
            cols.append(col)
            i += 1
        if len(cols):
            data = result['data']
            for i, item in enumerate(data):
                try:
                    keys = set(item.keys())
                except AttributeError:
                    continue
                for k in keys:
                    if k not in cols:
                        result['data'][i].pop(k)
        return result
