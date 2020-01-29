from django.db.models import Q


class GlobalFilter(object):

    def global_q(self):
        """Return a Q-Object for the local search for this column"""
        ret = Q()
        if self.global_search_value:
            lookup_expr_parts = self.lookup_expr.split('__')
            new_lookup = ''
            if lookup_expr_parts:
                new_lookup = '__'.join([self.field_name]
                                       + lookup_expr_parts[:-1]
                                       + ['icontains'])
            else:
                new_lookup = '__'.join([self.field_name, 'icontains'])
            ret = Q(**{new_lookup: self.global_search_value})
        return ret
