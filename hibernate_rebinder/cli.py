import click
import re

import collections


class RebindableQuery:
    """
    Class that connects a query string and its parameters.
    """

    def __init__(self, query):
        self._query = query
        self._params = {}

    def insert_param(self, position, param, sql_type):
        """
        Insert into a param/type combo into a given position
        :param position: to insert into the internal list
        :param param: parameter value
        :param sql_type: for proper type rebinding
        """
        self._params[int(position)] = BindableParam(param, sql_type)

    def bind(self):
        """
        Binds together query.
        :return:
        """

        # Loop through paramList and replace each question mark
        binded_query = self._query

        # Create ordered dict using params.
        sorted_params = collections.OrderedDict(sorted(self._params.items()))
        for position in sorted_params:
            # Get the bindable param object
            param = sorted_params[position]

            # Null edge case.
            if param.val == '<null>':
                rebinded_val = "NULL"
            # Determine if value should be enclosed in quotes.
            elif param.sql_type in ['VARCHAR', 'DATETIME', 'TIMESTAMP']:
                rebinded_val = '"' + param.val + '"'
            # Boolean maps to 0/1
            elif param.sql_type == 'BOOLEAN':
                rebinded_val = 1 if param.val.lower() is 'true' else 0
            # Default
            else:
                rebinded_val = param.val

            # Replace one question mark at a time
            binded_query = binded_query.replace('?', str(rebinded_val), 1)
        return binded_query


class BindableParam:
    """
    Represents value and type
    """

    def __init__(self, val, sql_type):
        self.val = val
        self.sql_type = sql_type


@click.command()
@click.argument('filename', required=True)
def main(filename):
    """Rebinds Hibernate logs into executable and readable SQL queries."""
    # click.echo('{0}, {1}.'.format(greet, name))
    # list of rebindable queries
    with open(filename) as fp:
        queries = []
        for line in fp:
            # Determine if this line is a query or a param
            if line.lower().startswith(('select', 'insert', 'update', 'delete')):
                queries.append(RebindableQuery(line))
            elif line.startswith('binding parameter'):
                # Make sure we have a query that we can bind these parameters to
                if len(queries) > 0:
                    # Pull out relevant info: position, type, value
                    position = re.search('(\d+)|$', line).group(1)
                    sql_type = re.search('\[(\D+)\]', line).group(1)
                    param = line.split('-', 1)[1].strip()
                    # Add the parameter to the last entry in the query list
                    queries[-1].insert_param(position, param, sql_type)

        # Perform the binding
        for query in queries:
            click.echo(query.bind())
