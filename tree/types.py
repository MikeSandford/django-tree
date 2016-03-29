from django.db.models import QuerySet


class Path:
    def __init__(self, field, value):
        self.field = field
        self.attname = getattr(self.field, 'attname', None)
        self.field_bound = self.attname is not None
        self.qs = (self.field.model._default_manager.all()
                   if self.field_bound else QuerySet())
        self.value = value

    def __repr__(self):
        if self.field_bound:
            return '<Path %s %s>' % (self.field, self.value)
        return '<Path %s>' % self.value

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, Path):
            other = other.value
        return self.value == other

    def __ne__(self, other):
        if isinstance(other, Path):
            other = other.value
        return self.value != other

    def __lt__(self, other):
        # We simulate the effects of a NULLS LAST.
        if self.value is None:
            return False
        if isinstance(other, Path):
            other = other.value
        if other is None:
            return True
        return self.value < other

    def __le__(self, other):
        # We simulate the effects of a NULLS LAST.
        if self.value is None:
            return False
        if isinstance(other, Path):
            other = other.value
        if other is None:
            return True
        return self.value <= other

    def __gt__(self, other):
        # We simulate the effects of a NULLS LAST.
        if self.value is None:
            return True
        if isinstance(other, Path):
            other = other.value
        if other is None:
            return False
        return self.value > other

    def __ge__(self, other):
        # We simulate the effects of a NULLS LAST.
        if self.value is None:
            return True
        if isinstance(other, Path):
            other = other.value
        if other is None:
            return False
        return self.value >= other

    def get_children(self):
        if self.value is None:
            return self.qs.none()
        return self.qs.filter(
            **{self.attname + '__match': self.value + '.*{1}'})

    def get_ancestors(self, include_self=False):
        if self.value is None:
            return self.qs.none()
        qs = self.qs
        if self.is_root:
            if include_self:
                return qs.filter(**{self.attname: self.value})
            return qs.none()
        if not include_self:
            qs = qs.exclude(**{self.attname: self.value})
        return qs.filter(**{self.attname + '__ancestor_of': self.value})

    def get_descendants(self, include_self=False):
        if self.value is None:
            return self.qs.none()
        qs = self.qs
        if not include_self:
            qs = qs.exclude(**{self.attname: self.value})
        return qs.filter(**{self.attname + '__descendant_of': self.value})

    def get_siblings(self, include_self=False):
        if self.value is None:
            return self.qs.none()
        qs = self.qs
        match = '*{1}'
        if not self.is_root:
            match = self.value.rsplit('.', 1)[0] + '.' + match
        if not include_self:
            qs = qs.exclude(**{self.attname: self.value})
        return qs.filter(**{self.attname + '__match': match})

    def get_prev_siblings(self, include_self=False):
        if self.value is None:
            return self.qs.none()
        siblings = self.get_siblings(include_self=include_self)
        lookup = '__lte' if include_self else '__lt'
        return (siblings.filter(**{self.attname + lookup: self.value})
                .order_by('-' + self.attname))

    def get_next_siblings(self, include_self=False):
        if self.value is None:
            return self.qs.none()
        siblings = self.get_siblings(include_self=include_self)
        lookup = '__gte' if include_self else '__gt'
        return (siblings.filter(**{self.attname + lookup: self.value})
                .order_by(self.attname))

    def get_prev_sibling(self):
        return self.get_prev_siblings().first()

    def get_next_sibling(self):
        return self.get_next_siblings().first()

    @property
    def depth(self):
        if self.value is not None:
            return self.value.count('.')

    @property
    def level(self):
        if self.value is not None:
            return self.depth + 1

    @property
    def is_root(self):
        if self.value is not None:
            return '.' not in self.value

    @property
    def is_leaf(self):
        if self.value is not None:
            return not self.get_children().exists()

    def is_ancestor_of(self, other, include_self=False):
        if self.value is None:
            return False
        if isinstance(other, Path):
            other = other.value
        if other is None:
            return False
        if not include_self and self.value == other:
            return False
        return other.startswith(self.value)

    def is_descendant_of(self, other, include_self=False):
        if self.value is None:
            return False
        if isinstance(other, Path):
            other = other.value
        if other is None:
            return False
        if not include_self and self.value == other:
            return False
        return self.value.startswith(other)


# Tells psycopg2 how to prepare a Path object for the database,
# in case it doesn't go through the ORM.
try:
    import psycopg2
except ImportError:
    pass
else:
    from psycopg2.extensions import adapt, register_adapter, AsIs

    def adapt_path(path):
        return AsIs('%s::ltree' % adapt(path.value))

    register_adapter(Path, adapt_path)
