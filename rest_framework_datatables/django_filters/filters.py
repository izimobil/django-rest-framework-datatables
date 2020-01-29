from django.db.models import Q


class GlobalFilter(object):

    def global_q(self):
        """Return a Q-Object for the local search for this column"""
        ret = Q()
        if self.global_search_value:
            ret = Q(**{self.global_lookup: self.global_search_value})
        return ret

    @property
    def global_lookup(self):
        ret = self.lookup_expr
        lookup_expr_parts = self.lookup_expr.split('__')
        if lookup_expr_parts:
            ret = '__'.join([self.field_name]
                            + lookup_expr_parts[:-1]
                            + ['icontains'])
        else:
            ret = '__'.join([self.field_name, 'icontains'])
        return ret
