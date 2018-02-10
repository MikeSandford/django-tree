from django.db.models import Lookup


class AncestorOf(Lookup):
    lookup_name = 'ancestor_of'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return '%s @> %s' % (lhs, rhs), lhs_params + rhs_params


class DescendantOf(Lookup):
    lookup_name = 'descendant_of'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return '%s <@ %s' % (lhs, rhs), lhs_params + rhs_params


class Match(Lookup):
    lookup_name = 'match'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return '%s ~ %s::lquery' % (lhs, rhs), lhs_params + rhs_params


class MatchAny(Lookup):
    lookup_name = 'match_any'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return '%s ? %s::lquery[]' % (lhs, rhs), lhs_params + rhs_params


class Search(Lookup):
    lookup_name = 'search'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        return '%s @ %s' % (lhs, rhs), lhs_params + rhs_params
