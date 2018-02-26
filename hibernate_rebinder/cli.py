import click
import re


class RebindableQuery:
    """
    Class that connects a query string and its parameters.
    """

    def __init__(self, query):
        self._query = query
        self._params = []

    def insert_param(self, position, param, sql_type):
        """
        Insert into a param/type combo into a given position
        :param position: to insert into the internal list
        :param param: parameter value
        :param sql_type: for proper type rebinding
        """
        self._params.insert(int(position), BindableParam(param, sql_type))

    def bind(self):
        """
        Binds together query.
        :return:
        """

        # Loop through paramList and replace each question mark
        binded_query = self._query
        for param in self._params:
            val = param.val
            # Null edge case.
            if val == '<null>':
                val = "NULL"
            # Determine if value should be enclosed in quotes.
            elif param.sql_type in ['VARCHAR', 'DATETIME', 'TIMESTAMP']:
                val = '"' + val + '"'
            elif param.sql_type == 'BOOLEAN':
                val = 1 if param.val is 'true' else 0
            binded_query = binded_query.replace('?', str(val), 1)
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
            if line.startswith(('select', 'insert', 'update', 'delete')):
                queries.append(RebindableQuery(line))
            elif line.startswith('binding parameter'):
                # Pull out relevant info: position, type, value
                position = re.search('(\d+)|$', line).group(1)
                sql_type = re.search('\[(\D+)\]', line).group(1)
                param = line.split('-', 1)[1].strip()
                # Add the parameter to the last entry in the query list
                queries[-1].insert_param(position, param, sql_type)

        # Perform the binding
        for query in queries:
            click.echo(query.bind())
