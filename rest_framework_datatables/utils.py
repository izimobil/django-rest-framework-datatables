
def get_param(request, param, default=None):
    if request.method == 'POST':
        return request.data.get(param, default)
    return request.query_params.get(param, default)
